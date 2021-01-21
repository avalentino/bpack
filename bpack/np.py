"""Numpy based codec for binary data structures."""

import math
import collections

import numpy as np

import bpack
import bpack.utils
import bpack.codecs

from .enums import EBaseUnits
from .descriptors import (
    field_descriptors, get_field_descriptor, BinFieldDescriptor,
)


__all__ = [
    'Decoder', 'decoder', 'BACKEND_NAME', 'BACKEND_TYPE',
    'descriptor_to_dtype', 'unpackbits',
]


BACKEND_NAME = 'numpy'
BACKEND_TYPE = EBaseUnits.BYTES


def bin_field_descripor_to_dtype(field_descr: BinFieldDescriptor) -> np.dtype:
    """Convert a field descriptor into a :class:`numpy.dtype`.

    .. seealso:: :class:`bpack.descriptors.BinFieldDescriptor`.
    """
    # TODO: add byteorder
    size = field_descr.size
    etype = bpack.utils.effective_type(field_descr.type)
    typecode = np.dtype(etype).kind

    if etype in (bytes, str):
        typecode = 'S'
    elif etype is int and not field_descr.signed:
        typecode = 'u'

    if typecode == 'O':
        raise TypeError(f'unsupported type: {field_descr.type:!r}')

    repeat = field_descr.repeat
    repeat = repeat if repeat and repeat > 1 else ''

    return np.dtype(f'{repeat}{typecode}{size}')


def descriptor_to_dtype(descriptor) -> np.dtype:
    """Convert the descriptor of a binary record into a :class:`numpy.dtype`.

    Please note that (unicode) strings are treated as "utf-8" encoded
    byte strings.
    UCS4 encoded strings are not supported.

    Sequences (:class:`typing.Sequence` and :class:`typing.List`) are
    always converted into :class:`numpy.ndarray`.

    .. seealso:: :func:`bpack.descriptors.descriptor`.
    """
    params = collections.defaultdict(list)
    for field in bpack.fields(descriptor):
        field_descr = get_field_descriptor(field)
        if bpack.is_descriptor(field_descr.type):
            dtype = descriptor_to_dtype(field_descr.type)
        else:
            dtype = bin_field_descripor_to_dtype(field_descr)
        params['names'].append(field.name)
        params['formats'].append(dtype)
        params['offsets'].append(field_descr.offset)
        # params['titles'].append('...')

    params = dict(params)  # numpy do not accept defaultdict
    params['itemsize'] = bpack.calcsize(descriptor)

    dt = np.dtype(dict(params))

    byteorder = bpack.byteorder(descriptor).value
    if byteorder:
        dt = dt.newbyteorder(byteorder)

    return dt


def _converter_factory(type_):
    etype = bpack.utils.effective_type(type_)
    if bpack.utils.is_enum_type(type_):
        if etype is str:
            def converter(x, cls=type_):
                return cls(x.tobytes().decode('utf-8'))
        else:
            def converter(x, cls=type_):
                return cls(x)
    elif etype is str:
        def converter(x):
            return x.tobytes().decode('utf-8')
    elif bpack.is_descriptor(type_):
        def converter(x, cls=type_):
            return cls(*x)
    else:
        converter = None

    return converter


class Decoder(bpack.codecs.Decoder):
    """Numpy based data decoder.

    (Unicode) strings are treated as "utf-8" encoded byte strings.
    UCS4 encoded strings are not supported.
    """

    baseunits = EBaseUnits.BYTES

    def __init__(self, descriptor):
        """Initializer.

        The *descriptor* parameter* is a bpack record descriptor.
        """
        super().__init__(descriptor)

        assert bpack.bitorder(descriptor) is None

        converters = [
            (idx, _converter_factory(field_descr.type))
            for idx, field_descr in enumerate(field_descriptors(descriptor))
        ]

        self._dtype = descriptor_to_dtype(descriptor)
        self._converters = [(idx, func) for idx, func in converters if func]

    @property
    def dtype(self):
        return self._dtype

    def decode(self, data: bytes, count: int = 1):
        """Decode binary data and return a record object."""
        v = np.frombuffer(data, dtype=self._dtype, count=count)
        if self._converters:
            out = []
            for item in v:
                item = list(item)
                for idx, func in self._converters:
                    item[idx] = func(item[idx])
                out.append(self.descriptor(*item))
        else:
            out = [self.descriptor(*item) for item in v]
        if len(v) == 1:
            out = out[0]
        return out


decoder = bpack.codecs.make_codec_decorator(Decoder)


def unpackbits(data: bytes, bits_per_sample: int, signed: bool = False):
    """Unpack packed (integer) values form a string of bytes.

    Takes in input a string of bytes in which (integer) samples have been
    stored using ``bits_per_sample`` bit for each sample, and returns
    the sequence of corresponding Python integers.

    Example::

                 3 bytes                            4 samples

      |------|------|------|------| --> [samp_1, samp_2, samp_3, samp_4]

      4 samples (6 bits per sample)

    If ``signed`` is set to True integers are assumed to be stored as
    signed integers.
    """
    # TODO: support byteorder: str = ''
    # if byteprder:
    #     raise NotImplementedError(f'byteorder = "{byteprder}"')

    if bits_per_sample > 8:
        # TODO: support bits_per_sample > 8
        raise NotImplementedError(f'bits_per_sample = {bits_per_sample}')
    elif bits_per_sample == 8:
        dtype = np.dtype('int8') if signed else np.dtype('uint8')
        return np.frombuffer(data, dtype=dtype)
    nbits = len(data) * 8
    assert nbits % bits_per_sample == 0
    samples = nbits // bits_per_sample

    chunksize = bits_per_sample // math.gcd(bits_per_sample, 8)     # bytes
    samples_per_chunk = (chunksize * 8) // bits_per_sample
    nchunks = samples // samples_per_chunk

    basetypes = {
        # nbits: (basetype, offset),
        2: (np.dtype('>u1'), 0),
        3: (np.dtype('>u4'), 1),
        4: (np.dtype('>u1'), 0),
        5: (np.dtype('>u8'), 3),
        6: (np.dtype('>u4'), 1),
        7: (np.dtype('>u8'), 1),
    }
    basetype, offset = basetypes[bits_per_sample]
    itemsize = basetype.itemsize

    # byte array
    npdata = np.frombuffer(data, np.uint8)

    # pad
    odata = np.zeros([nchunks, itemsize], dtype=np.uint8)
    odata[:, offset:] = npdata.reshape([nchunks, chunksize])

    # to int
    odata = odata.view(dtype=basetype)

    # replicate
    odata = odata.repeat(samples_per_chunk, 1)

    # shift
    shifts = bits_per_sample * np.arange(samples_per_chunk)[::-1]
    shifts = np.asarray(shifts, dtype=np.uint32)  # workaround for numpy issue
    odata = np.right_shift(odata, shifts)

    # mask
    mask = np.packbits([1] * bits_per_sample, bitorder='little')
    odata = np.bitwise_and(odata, mask)

    dtype = np.int8 if signed else np.uint8
    return odata.ravel().astype(dtype)

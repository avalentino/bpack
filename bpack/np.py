"""Numpy based codec for binary data structures."""

import functools
import collections
from typing import NamedTuple, Optional

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


# --- bits packing/unpacking --------------------------------------------------
def _get_item_size(bits_per_sample: int) -> int:
    """Item size of the integer type that can take requested bits."""
    if bits_per_sample > 64 or bits_per_sample < 1:
        raise ValueError(f'bits_per_sample: {bits_per_sample}')
    elif bits_per_sample <= 8:
        return 1
    else:
        return 2**int(np.ceil(np.log2(bits_per_sample))-3)


def _get_buffer_size(bits_per_sample: int) -> int:
    """Item size of the integer type that can take requested bits and shift."""
    return _get_item_size(bits_per_sample + 7)


def _get_mask(nbits: int, dtype: str) -> np.ndarray:
    """Returns a mask for dtype to select the nbits least significant bits."""
    shift = np.array(64 - nbits, dtype=np.uint32)
    mask = np.array(0xffffffffffffffff) >> shift
    return mask.astype(dtype)


class _BitUnpackParams(NamedTuple):
    samples: int
    dtype: str
    buf_itemsize: int
    buf_dtype: str
    index_map: np.ndarray
    shifts: np.ndarray
    mask: np.ndarray


@functools.lru_cache()  # COPMPATIBILITY with Python3.7
def _unpackbits_params(nbits: int, bits_per_sample: int,
                       samples_per_block: int, bit_offset: int,
                       blockstride: int, signed: bool = False,
                       byteorder: str = '>') -> _BitUnpackParams:
    assert nbits >= bit_offset
    if samples_per_block is None:
        if blockstride is not None:
            raise ValueError(
                '"samples_per_block" cannot be computed automatically '
                'when "blockstride" is provided')
        samples_per_block = (nbits - bit_offset) // bits_per_sample
    blocksize = bits_per_sample * samples_per_block
    if blockstride is None:
        blockstride = blocksize
    else:
        assert blockstride >= blocksize
    nstrides = (nbits - bit_offset) // blockstride
    extrabits = nbits - bit_offset - nstrides * blockstride
    if extrabits >= blocksize:
        nblocks = nstrides + 1
        extra_samples = 0
    else:
        nblocks = nstrides
        extra_samples = extrabits // bits_per_sample
    assert nblocks >= 0
    pad = blockstride - blocksize

    sizes = [bit_offset]
    if nblocks > 0:
        sizes.extend([bits_per_sample] * (samples_per_block - 1))
        block_sizes = (
                [bits_per_sample + pad] +
                [bits_per_sample] * (samples_per_block - 1)
        )
        sizes.extend(block_sizes * (nblocks - 1))
    if extra_samples:
        sizes.append(bits_per_sample + pad)
        sizes.extend([bits_per_sample] * (extra_samples - 1))

    bit_offsets = np.cumsum(sizes)
    byte_offsets = bit_offsets // 8
    samples = len(bit_offsets)

    itemsize = _get_item_size(bits_per_sample)
    buf_itemsize = _get_buffer_size(bits_per_sample)
    dtype = f'{byteorder}{"i" if signed else "u"}{itemsize}'
    buf_dtype = f'{byteorder}{"i" if signed else "u"}{buf_itemsize}'

    index = np.arange(buf_itemsize) + byte_offsets[:, None]
    index = np.clip(index, 0, nbits // 8 - 1)

    mask = _get_mask(bits_per_sample, buf_dtype)
    shifts = (bit_offsets - byte_offsets * 8 + bits_per_sample)
    shifts = buf_itemsize * 8 - shifts

    return _BitUnpackParams(samples=samples,
                            dtype=dtype,
                            buf_itemsize=buf_itemsize,
                            buf_dtype=buf_dtype,
                            index_map=index,
                            shifts=shifts,
                            mask=mask)


def unpackbits(data: bytes, bits_per_sample: int,
               samples_per_block: Optional[int] = None, bit_offset: int = 0,
               blockstride: Optional[int] = None, signed: bool = False,
               byteorder: str = '>') -> np.ndarray:
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
    if bit_offset == 0 and blockstride is None:
        if bits_per_sample == 1:
            return np.unpackbits(np.frombuffer(data, dtype='uint8'))
        elif bits_per_sample in {8, 16, 32, 64}:
            size = bits_per_sample // 8
            kind = "i" if signed else "u"
            typestr = f'{byteorder}{kind}{size}'
            return np.frombuffer(data, dtype=np.dtype(typestr))

    nbits = len(data) * 8

    params = _unpackbits_params(nbits, bits_per_sample, samples_per_block,
                                bit_offset, blockstride, signed, byteorder)
    samples, dtype, buf_itemsize, buf_dtype, index_map, shifts, mask = params

    npdata = np.frombuffer(data, dtype='u1')
    buf = np.empty(samples, dtype=buf_dtype)
    bytesview = buf.view(dtype='u1').reshape(samples, buf_itemsize)
    bytesview[...] = npdata[index_map]
    outdata = ((buf >> shifts) & mask).astype(dtype)

    return outdata

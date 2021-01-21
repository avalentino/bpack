"""Bitarray based codec for binary data structures."""

import struct
import itertools
from typing import Any, Callable, Optional

import bitarray
from bitarray.util import ba2int

import bpack
import bpack.utils
import bpack.codecs

from .enums import EBaseUnits, EBitOrder, EByteOrder
from .descriptors import field_descriptors


__all__ = ['Decoder', 'decoder', 'BACKEND_NAME', 'BACKEND_TYPE']


BACKEND_NAME = 'bitarray'
BACKEND_TYPE = EBaseUnits.BITS


FactoryType = Callable[[bitarray.bitarray], Any]


def ba_to_float_factory(size, byteorder: str = '>',
                        bitorder: str = 'big') -> FactoryType:
    """Convert a bitarray into a float."""
    assert bitorder == 'big'

    if size == 16:
        fmt = f'{byteorder}e'
    elif size == 32:
        fmt = f'{byteorder}f'
    elif size == 64:
        fmt = f'{byteorder}d'
    else:
        raise ValueError('floating point item size must be 16, 32 or 64 bits')

    codec = struct.Struct(fmt)

    def func(ba):
        return codec.unpack(ba.tobytes())[0]

    return func


def converter_factory(type_, size: Optional[int] = None, signed: bool = False,
                      byteorder: str = '>',
                      bitorder: str = 'big') -> FactoryType:
    if bpack.utils.is_sequence_type(type_, error=True):
        raise TypeError(
            f'backend "{BACKEND_NAME}" does not supports sequence types: '
            f'"{type_}".')
    etype = bpack.utils.effective_type(type_)
    if etype is int:
        def func(ba):
            return ba2int(ba, signed)
    elif etype is float:
        func = ba_to_float_factory(size, byteorder, bitorder)
    elif etype is bytes:
        def func(ba):
            return ba.tobytes()
    elif etype is str:
        def func(ba):
            return ba.tobytes().decode('ascii')
    elif etype is bool:
        def func(ba):
            return bool(bitarray.util.ba2int(ba))
    else:
        raise TypeError(
            f'type "{type_}" is not supported by the {__name__} backend'
            f'({BACKEND_NAME})')

    if etype is not type_:
        def converter(x, conv_func=func):
            return type_(conv_func(x))
    else:
        converter = func
    return converter


def _bitorder_to_baorder(bitorder: EBitOrder) -> str:
    if bitorder in {EBitOrder.MSB, EBitOrder.DEFAULT}:
        s = 'big'
    elif bitorder is EBitOrder.LSB:
        s = 'little'
    else:
        raise ValueError(f'invalid bit order: "{bitorder}"')
    return s


class Decoder(bpack.codecs.Decoder):
    """Bitarray based data decoder.

    Only supports "big endian" byte-order and MSB bit-order.
    """

    baseunits = EBaseUnits.BITS

    def __init__(self, descriptor, converters=converter_factory):
        """Initializer.

        The *descriptor* parameter* is a bpack record descriptor.
        """
        super().__init__(descriptor)

        byteorder = bpack.byteorder(descriptor)
        if byteorder in {EByteOrder.LE, EByteOrder.NATIVE}:
            raise NotImplementedError(
                f'byte order "{byteorder}" is not supported by the {__name__} '
                f'backend ({BACKEND_NAME})')

        bitorder = _bitorder_to_baorder(bpack.bitorder(descriptor))
        if bitorder != 'big':
            raise NotImplementedError(
                f'bit order "{bitorder}" is not supported by the {__name__} '
                f'backend ({BACKEND_NAME})')

        if callable(converters):
            conv_factory = converters
            byteorder_str = byteorder.value if byteorder.value else '>'
            converters = [
                conv_factory(field_descr.type, field_descr.size,
                             field_descr.signed, byteorder_str)
                for field_descr in field_descriptors(descriptor)
            ]

        if converters is not None:
            converters = list(converters)
            n_fields = len(list(bpack.fields(descriptor)))
            if len(converters) != n_fields:
                raise ValueError(
                    f'the number of converters ({len(converters)}) does not '
                    f'match the number of fields ({n_fields})')

        self._converters = converters
        self._slices = [
            slice(field_descr.offset, field_descr.offset + field_descr.size)
            for field_descr in field_descriptors(descriptor)
        ]

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        ba = bitarray.bitarray()
        ba.frombytes(data)
        values = [ba[slice_] for slice_ in self._slices]

        if self._converters is not None:
            values = [
                convert(value) if convert is not None else value
                for convert, value in zip(self._converters, values)
            ]

        return self.descriptor(*values)


decoder = bpack.codecs.make_codec_decorator(Decoder)


def _pairwise(it):
    a, b = itertools.tee(it)
    next(b, None)
    return itertools.zip_longest(a, b, fillvalue=None)


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
    nbits = len(data) * 8
    # assert nbits % bits_per_sample == 0
    slices = [
        slice(s, e) for s, e in _pairwise(range(0, nbits, bits_per_sample))
    ]
    ba = bitarray.bitarray()
    ba.frombytes(data)
    return [ba2int(ba[slice_],  signed) for slice_ in slices]

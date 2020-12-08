"""Bitarray based codec for binary data structures."""

import struct

from typing import Any, Callable, Optional

import bitarray
from bitarray.util import ba2int, make_endian

import bpack

from . import utils
from .utils import classdecorator
from .descriptors import field_descriptors


__all__ = ['Decoder', 'decoder', 'BACKEND_NAME', 'BACKEND_TYPE']


BACKEND_NAME = 'bitarray'
BACKEND_TYPE = bpack.EBaseUnits.BITS


FactoryType = Callable[[bitarray.bitarray], Any]


def ba_to_float_factory(size, byteorder: str = '>',
                        bitorder: str = 'big') -> FactoryType:
    """Convert a bitarray into a float."""
    if size == 16:
        fmt = f'{byteorder}e'
    elif size == 32:
        fmt = f'{byteorder}f'
    elif size == 64:
        fmt = f'{byteorder}d'
    else:
        raise ValueError('floating point item size must be 16, 32 or 64 bits')

    codec = struct.Struct(fmt)

    if bitorder != 'big':
        assert byteorder == '>' and bitorder == 'little'
        codec = struct.Struct(f'<{fmt[-1]}')  # hack

        def func(ba, bitorder=bitorder, make_endian=make_endian):
            ba = make_endian(ba, bitorder)
            return codec.unpack(ba.tobytes())[0]
    else:
        def func(ba):
            return codec.unpack(ba.tobytes())[0]

    return func


def converter_factory(type_, size: Optional[int] = None, signed: bool = False,
                      byteorder: str = '>',
                      bitorder: str = 'big') -> FactoryType:
    if type_ is int:
        if bitorder != 'big':
            def func(ba, bitorder=bitorder, make_endian=make_endian):
                ba = make_endian(ba, bitorder)
                return ba2int(ba, signed)
        else:
            def func(ba):
                return ba2int(ba, signed)
    elif type_ is float:
        func = ba_to_float_factory(size, byteorder, bitorder)
    elif type_ is bytes:
        if bitorder != 'big':
            def func(ba, bitorder=bitorder, make_endian=make_endian):
                ba = make_endian(ba, bitorder)
                return ba.tobytes()[::-1]
        else:
            def func(ba):
                return ba.tobytes()
    elif type_ is str:
        if bitorder != 'big':
            def func(ba, bitorder=bitorder, make_endian=make_endian):
                ba = make_endian(ba, bitorder)
                return ba.tobytes().decode('ascii')[::-1]
        else:
            def func(ba):
                return ba.tobytes().decode('ascii')
    elif type_ is bool:
        def func(ba):
            return bool(bitarray.util.ba2int(ba))
    else:
        raise TypeError(
            f'type "{type_}" is not supported by the {__name__} backend'
            f'({BACKEND_NAME})')

    return func


def _bitorder_to_baorder(bitorder: bpack.EBitOrder) -> str:
    if bitorder in {bpack.EBitOrder.MSB, bpack.EBitOrder.DEFAULT}:
        s = 'big'
    elif bitorder is bpack.EBitOrder.LSB:
        s = 'little'
    else:
        raise ValueError(f'invalid bit order: "{bitorder}"')
    return s


class Decoder:
    """Bitarray based data decoder.

    Only supports "big endian" byte-order.
    """

    def __init__(self, descriptor, converters=converter_factory):
        if bpack.baseunits(descriptor) is not bpack.EBaseUnits.BITS:
            raise ValueError(
                'bitarray decoder only accepts descriptors with '
                'base units "bits"')

        assert bpack.bitorder(descriptor) is not None

        byteorder = bpack.byteorder(descriptor)

        if byteorder in {bpack.EByteOrder.LITTLE, bpack.EByteOrder.NATIVE}:
            raise NotImplementedError(
                f'byte order "{byteorder}" is not supported by the {__name__} '
                f'backend ({BACKEND_NAME})')

        bitorder = _bitorder_to_baorder(bpack.bitorder(descriptor))

        if callable(converters):
            conv_factory = converters
            byteorder_str = byteorder.value if byteorder.value else '>'
            converters = [
                conv_factory(field_descr.type, field_descr.size,
                             field_descr.signed, byteorder_str, bitorder)
                for field_descr in field_descriptors(descriptor)
            ]

        if converters is not None:
            converters = list(converters)
            n_fields = len(list(bpack.fields(descriptor)))
            if len(converters) != n_fields:
                raise ValueError(
                    f'the number of converters ({len(converters)}) does not '
                    f'match the number of fields ({n_fields})')

        self._bitorder = bitorder
        self._descriptor = descriptor
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

        return self._descriptor(*values)


@classdecorator
def decoder(cls, *, converters=converter_factory):
    """Class decorator to add decoding methods to a descriptor classes.

    The decorator automatically generates a :class:`Decoder` object
    form the input descriptor class and attach a "from_bytes" method
    using the decoder to the descriptor class itself.
    """
    decoder_ = Decoder(descriptor=cls, converters=converters)

    decode_func = utils.create_fn(
        name='decode',
        args=('data',),
        body=['return decoder.decode(data)'],
        locals={'decoder': decoder_},
    )
    decode_func = staticmethod(decode_func)
    utils.set_new_attribute(cls, 'from_bytes', decode_func)

    return cls

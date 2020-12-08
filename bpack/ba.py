"""Bitarray based codec for binary data structures."""

import struct

import bitarray
import bitarray.util

import bpack

from . import utils
from .utils import classdecorator
from .descriptors import field_descriptors


__all__ = ['Decoder', 'decoder', 'BACKEND_NAME', 'BACKEND_TYPE']


BACKEND_NAME = 'bitarray'
BACKEND_TYPE = bpack.EBaseUnits.BITS
ba2int = bitarray.util.ba2int


def ba_to_float_factory(size, byteorder: str = '>'):
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

    def func(ba):
        return codec.unpack(ba.tobytes())[0]

    return func


def converter_factory(type_, size=None, signed=False, byteorder='>'):
    if type_ is int:
        def func(ba):
            return ba2int(ba, signed)
    elif type_ is float:
        func = ba_to_float_factory(size, byteorder)
    elif type_ is bytes:
        def func(ba):
            return ba.tobytes()
    elif type_ is str:
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

    Default bit-order: MSB.
    """

    def __init__(self, descriptor, converters=converter_factory):
        if bpack.baseunits(descriptor) is not bpack.EBaseUnits.BITS:
            raise ValueError(
                'bitarray decoder only accepts descriptors with '
                'base units "bits"')

        assert bpack.bitorder(descriptor) is not None

        byteorder = bpack.byteorder(descriptor)
        if byteorder is None:
            byteorder = bpack.EByteOrder.BIG

        if byteorder not in {bpack.EByteOrder.BIG, bpack.EByteOrder.NATIVE}:
            raise NotImplementedError(
                f'byte order "{byteorder}" is not supported by the {__name__} '
                f'backend ({BACKEND_NAME})')

        if callable(converters):
            conv_factory = converters
            converters = [
                conv_factory(field_descr.type, field_descr.size,
                             field_descr.signed, str(byteorder.value))
                for field_descr in field_descriptors(descriptor)
            ]

        if converters is not None:
            converters = list(converters)
            n_fields = len(list(bpack.fields(descriptor)))
            if len(converters) != n_fields:
                raise ValueError(
                    f'the number of converters ({len(converters)}) does not '
                    f'match the number of fields ({n_fields})')

        bitorder: bpack.EBitOrder = bpack.bitorder(descriptor)
        self._bitorder = _bitorder_to_baorder(bitorder)
        if self._bitorder != 'big':
            raise NotImplementedError(
                f'bit order "{bitorder}" is not supported by the {__name__} '
                f'backend ({BACKEND_NAME})')

        self._descriptor = descriptor
        self._converters = converters
        self._slices = [
            slice(field_descr.offset, field_descr.offset + field_descr.size)
            for field_descr in field_descriptors(descriptor)
        ]

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        ba = bitarray.bitarray(endian=self._bitorder)
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

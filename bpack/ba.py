"""Bitarray based codec for binary data structures."""

import sys
import struct

import bitarray
import bitarray.util

from . import utils
from .utils import classdecorator
from .descriptors import (
    EBaseUnits, EEndian, fields, field_descriptors, baseunits, byteorder,
)


__all__ = ['Decoder', 'decoder']


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


def converter_factory(type_, size=None, signed=False, order='>'):
    if type_ is int:
        def func(ba):
            return ba2int(ba, signed)
    elif type_ is float:
        func = ba_to_float_factory(size, order)
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
            f'type "{type_}" is not supported by the bpack.ba backend '
            f'(bitarray)')

    return func


def _order_to_endian(order: EEndian) -> str:
    if order is EEndian.NATIVE:
        endian = sys.byteorder
    elif order in {EEndian.BIG, EEndian.DEFAULT}:
        endian = 'big'
    else:
        endian = 'little'
    return endian


class Decoder:
    """Bitarray based data decoder.

    Default bit-order: MSB.
    """

    def __init__(self, descriptor, converters=converter_factory):
        if baseunits(descriptor) is not EBaseUnits.BITS:
            raise ValueError(
                'bitarray decoder only accepts descriptors with '
                'base units "bits"')

        order = byteorder(descriptor)
        if order is None:
            order = EEndian.BIG

        if callable(converters):
            conv_factory = converters
            converters = [
                conv_factory(field_descr.type, field_descr.size,
                             field_descr.signed, str(order.value))
                for field_descr in field_descriptors(descriptor)
            ]

        if converters is not None:
            converters = list(converters)
            n_fields = len(list(fields(descriptor)))
            if len(converters) != n_fields:
                raise ValueError(
                    f'the number of converters ({len(converters)}) does not '
                    f'match the number of fields ({n_fields})')

        self._endian = _order_to_endian(order)
        self._descriptor = descriptor
        self._converters = converters
        self._slices = [
            slice(field_descr.offset, field_descr.offset + field_descr.size)
            for field_descr in field_descriptors(descriptor)
        ]

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        ba = bitarray.bitarray(endian=self._endian)
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

"""Bitstruct based codec for binary data structures."""

import sys
import enum
from typing import Optional

import bitstruct

import bpack
import bpack.utils

from .utils import classdecorator
from .descriptors import field_descriptors


__all__ = ['Decoder', 'decoder', 'BACKEND_NAME', 'BACKEND_TYPE']


BACKEND_NAME = 'bitstruct'
BACKEND_TYPE = bpack.EBaseUnits.BITS


_TYPE_TO_STR = {
    bool: 'b',
    int: 'u',
    (int, False): 'u',
    (int, True): 's',
    float: 'f',
    bytes: 'r',
    str: 't',
    None: 'p',
}


def _to_fmt(type_, size: int, bitorder: str = '',
            signed: Optional[bool] = None,
            repeat: Optional[int] = None) -> str:
    assert size > 0, f'invalid size: {size:r}'
    assert bitorder in ('', '>', '<'), f'invalid order: {bitorder:r}'
    if repeat is None:
        repeat = 1
    assert repeat > 0, f'invalid repeat: {repeat:r}'

    etype = bpack.utils.effective_type(type_)
    key = (etype, signed) if etype is int and signed is not None else etype

    try:
        fmt = f'{bitorder}{_TYPE_TO_STR[key]}{size}' * repeat
    except KeyError:
        raise TypeError(f'unsupported type: {etype:!r}')

    return fmt


def _endianess_to_str(order: bpack.EByteOrder) -> str:
    if order is bpack.EByteOrder.NATIVE:
        return '<' if sys.byteorder == 'little' else '>'
    return order.value


class Decoder:
    """Bitstruct based data decoder.

    Default bit-order: MSB.
    """

    def __init__(self, descriptor):
        if bpack.baseunits(descriptor) is not bpack.EBaseUnits.BITS:
            raise ValueError(
                'bitsruct decoder only accepts descriptors with '
                'base units "bits"')

        byteorder = bpack.byteorder(descriptor)
        byteorder = _endianess_to_str(byteorder)
        bitorder = bpack.bitorder(descriptor).value

        fmt = ''.join(
            _to_fmt(field_descr.type, size=field_descr.size, bitorder=bitorder,
                    signed=field_descr.signed)  # field_descr.repeat
            for field_descr in field_descriptors(descriptor, pad=True)
        )
        fmt = fmt + byteorder  # byte order

        self._codec = bitstruct.compile(fmt)
        self._descriptor = descriptor
        self._converters = [
            (idx, field.type)
            for idx, field in enumerate(bpack.fields(descriptor))
            if issubclass(field.type, enum.Enum)
        ]

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        values = self._codec.unpack(data)
        if self._converters:
            values = list(values)
            for idx, func in self._converters:
                values[idx] = func(values[idx])
        return self._descriptor(*values)


@classdecorator
def decoder(cls):
    """Class decorator to add decoding methods to a descriptor classes.

    The decorator automatically generates a :class:`Decoder` object
    form the input descriptor class and attach a "from_bytes" method
    using the decoder to the descriptor class itself.
    """
    decoder_ = Decoder(descriptor=cls)

    decode_func = bpack.utils.create_fn(
        name='decode',
        args=('data',),
        body=['return decoder.decode(data)'],
        locals={'decoder': decoder_},
    )
    decode_func = staticmethod(decode_func)
    bpack.utils.set_new_attribute(cls, 'from_bytes', decode_func)

    return cls

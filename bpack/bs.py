"""Bitstruct based codec for binary data structures."""

import sys
from typing import Optional

import bitstruct

from . import utils
from .utils import classdecorator
from .descriptors import (
    EBaseUnits, EOrder, field_descriptors, baseunits, order,
)


__all__ = ['Decoder', 'decoder']


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


def _to_fmt(type_, size: int, order: str = '', signed: Optional[bool] = None,
            repeat: Optional[int] = None) -> str:
    if size <= 0:
        raise TypeError(f'invalid size: {size:r}')
    if order not in ('', '>', '<'):
        raise TypeError(f'invalid order: {order:r}')
    if repeat is None:
        repeat = 1
    elif repeat <= 0:
        raise TypeError(f'invalid repeat: {repeat:r}')

    key = (type_, signed) if type_ is int and signed is not None else type_
    try:
        fmt = f'{order}{_TYPE_TO_STR[key]}{size}' * repeat
    except KeyError:
        raise TypeError(f'unsupported type: {type:!r}')

    return fmt


def _order_to_str(order: EOrder) -> str:
    if order is EOrder.NATIVE:
        return '<' if sys.byteorder == 'little' else '>'
    return order.value


class Decoder:
    """Bitstruct based data decoder.

    Default bit-order: MSB.
    """

    def __init__(self, descriptor):
        if baseunits(descriptor) is not EBaseUnits.BITS:
            raise ValueError(
                'bitsruct decoder only accepts descriptors with '
                'base units "bits"')

        bitorder = order(descriptor)
        if bitorder is None:
            bitorder = EOrder.MSB

        # assert all(descr.order for descr in field_descriptors(descriptor))
        bitorder = _order_to_str(bitorder)

        fmt = ''.join(
            _to_fmt(field_descr.type, field_descr.size, bitorder,
                    field_descr.signed)  # field_descr.repeat
            for field_descr in field_descriptors(descriptor, pad=True)
        )

        self._codec = bitstruct.compile(fmt)
        self._descriptor = descriptor

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        values = self._codec.unpack(data)
        return self._descriptor(*values)


@classdecorator
def decoder(cls):
    """Class decorator to add decoding methods to a descriptor classes.

    The decorator automatically generates a :class:`Decoder` object
    form the input descriptor class and attach a "from_bytes" method
    using the decoder to the descriptor class itself.
    """
    decoder_ = Decoder(descriptor=cls)

    decode_func = utils.create_fn(
        name='decode',
        args=('data',),
        body=['return decoder.decode(data)'],
        locals={'decoder': decoder_},
    )
    decode_func = staticmethod(decode_func)
    utils.set_new_attribute(cls, 'from_bytes', decode_func)

    return cls

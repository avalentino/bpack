"""Bitarray based decoder for binary data structures."""

import dataclasses

import bitstruct

from .utils import classdecorator
from .descriptor import EBaseUnits, _fields_with_padding


_TYPE_TO_STR = {
    bool: 'b',
    int: 'u',
    float: 'f',
    bytes: 'r',
    str: 't',
    None: 'p',
}


# TODO: add repeat parameter
def _type_size_order_to_str(type_, size: int, order: str = ''):
    if size <= 0:
        raise TypeError(f'invalid size: {size:r}')
    if order not in ('', '>', '<'):
        raise TypeError(f'invalid order: {order:r}')
    try:
        return f'{order}{_TYPE_TO_STR[type_]}{size}'
    except KeyError:
        raise TypeError(f'unsupported type: {type:!r}')


class Decoder:
    def __init__(self, descriptor, *, order=''):
        if descriptor._BASEUNITS is not EBaseUnits.BITS:
            raise ValueError(
                'bitsruct decoder only accepts descriptors with '
                'base units "bits"')

        fmt = ''.join(
            _type_size_order_to_str(field.type, field.size, order)
            for field in _fields_with_padding(descriptor)
        )

        self._codec = bitstruct.compile(fmt)
        self._descriptor = descriptor

    def decode(self, data):
        values = self._codec.unpack(data)
        return self._descriptor(*values)


@classdecorator
def decoder(cls, **kwargs):
    decoder_ = Decoder(descriptor=cls, **kwargs)

    decode_func = dataclasses._create_fn(
        name='decode',
        args=('data',),
        body=['return decoder.decode(data)'],
        locals={'decoder': decoder_},
    )
    decode_func = staticmethod(decode_func)
    dataclasses._set_new_attribute(cls, 'from_bytes', decode_func)

    return cls

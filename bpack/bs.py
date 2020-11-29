"""Bitarray based decoder for binary data structures."""

import bitstruct

from . import utils
from .utils import classdecorator
from .descriptors import EBaseUnits, fields


_TYPE_TO_STR = {
    bool: 'b',
    int: 'u',
    float: 'f',
    bytes: 'r',
    str: 't',
    None: 'p',
}


# TODO: add repeat parameter
def _type_size_order_to_str(type_, size: int, order: str = '') -> str:
    if size <= 0:
        raise TypeError(f'invalid size: {size:r}')
    if order not in ('', '>', '<'):
        raise TypeError(f'invalid order: {order:r}')
    try:
        return f'{order}{_TYPE_TO_STR[type_]}{size}'
    except KeyError:
        raise TypeError(f'unsupported type: {type:!r}')


class Decoder:
    """Bitstruct based data decoder."""

    def __init__(self, descriptor, *, order=''):
        if descriptor.__bpack_baseunits__ is not EBaseUnits.BITS:
            raise ValueError(
                'bitsruct decoder only accepts descriptors with '
                'base units "bits"')

        fmt = ''.join(
            _type_size_order_to_str(field.type, field.size, order)
            for field in fields(descriptor, True)
        )

        self._codec = bitstruct.compile(fmt)
        self._descriptor = descriptor

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        values = self._codec.unpack(data)
        return self._descriptor(*values)


@classdecorator
def decoder(cls, **kwargs):
    """Class decorator to add decoding methods to a descriptor classes.

    The decorator automatically generates a :class:`Decoder` object
    form the input descriptor class and attach a "from_bytes" method
    using the decoder to the descriptor class itself.
    """
    decoder_ = Decoder(descriptor=cls, **kwargs)

    decode_func = utils.create_fn(
        name='decode',
        args=('data',),
        body=['return decoder.decode(data)'],
        locals={'decoder': decoder_},
    )
    decode_func = staticmethod(decode_func)
    utils.set_new_attribute(cls, 'from_bytes', decode_func)

    return cls

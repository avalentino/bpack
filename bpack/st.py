"""Struct based codec for binary data structures."""

import struct

from typing import Optional

import bpack

from . import utils
from .utils import classdecorator
from .descriptors import field_descriptors


__all__ = ['Decoder', 'decoder']


_TYPE_SIGNED_AND_SIZE_TO_STR = {
    # type, signed, size
    (bool, None, 1): 'B',
    (int, None, 1): 'b',        # default
    (int, False, 1): 'B',
    (int, True, 1): 'b',
    (int, None, 2): 'h',        # default
    (int, False, 2): 'H',
    (int, True, 2): 'h',
    (int, None, 4): 'i',        # default
    (int, False, 4): 'I',
    (int, True, 4): 'i',
    (int, None, 8): 'q',        # default
    (int, False, 8): 'Q',
    (int, True, 8): 'q',
    (float, None, 2): 'e',
    (float, None, 4): 'f',
    (float, None, 8): 'd',
    (bytes, None, None): 's',
    (str, None, None): 's',
    (None, None, None): 'x',        # padding
}


_DEFAULT_SIZE = {
    bool: 1,
    int: 4,
    float: 4,
    bytes: 1,
    # str: 1,
}


def _to_fmt(type_, size: Optional[int] = None, order: str = '',
            signed: Optional[bool] = None,
            repeat: Optional[int] = None) -> str:
    size = _DEFAULT_SIZE.get(type_, size) if size is None else size

    if size is None or size <= 0:
        raise TypeError(f'invalid size: {size!r} for type {type_!r}')
    if order not in ('', '>', '<', '=', '@', '!'):
        raise TypeError(f'invalid order: {order!r}')
    # signed = bool(signed)  # TODO: check

    try:
        if type_ in (str, bytes, None):  # none is for padding bytes
            repeat = 1 if repeat is None else repeat
            key = (type_, signed, None)
            return f'{order}{size}{_TYPE_SIGNED_AND_SIZE_TO_STR[key]}' * repeat
        else:
            repeat_str = '' if repeat is None else str(repeat)
            key = (type_, signed, size)
            return f'{order}{repeat_str}{_TYPE_SIGNED_AND_SIZE_TO_STR[key]}'
    except KeyError:
        raise TypeError(
            f'unable to generate format string for '
            f'type="{type_}", size="{size}", order="{order}", '
            f'signed="{signed}", repeat="{repeat}"')


class Decoder:
    """Struct based data decoder.

    Default byte-order: MSB.
    """

    def __init__(self, descriptor):
        if bpack.baseunits(descriptor) is not bpack.EBaseUnits.BYTES:
            raise ValueError(
                'struct decoder only accepts descriptors with '
                'base units "bytes"')

        byteorder = bpack.byteorder(descriptor)
        if byteorder is None:
            byteorder = bpack.EEndian.BIG

        if byteorder.value not in ('', '>', '<', '=', '@', '!'):
            raise TypeError(f'invalid byte order: {byteorder!r}')

        # assert all(descr.order for descr in field_descriptors(descriptor))

        byteorder = byteorder.value

        # NOTE: struct expects that the byteorder specifier is used only
        #       once at the beginning of the format string
        fmt = byteorder + ''.join(
            _to_fmt(field_descr.type, field_descr.size, order='')
            for field_descr in field_descriptors(descriptor, pad=True)
        )

        self._codec = struct.Struct(fmt)
        self._descriptor = descriptor
        converters = {
            str: lambda s: s.decode('ascii'),
            bool: bool,
            # Enums
        }
        # TODO: enum support
        # converters.update(
        #     (field_.type, field_.type)
        #     for field_ in dataclasses.fields(self._descriptor)
        #     if issubclass(field_.type, enum.Enum))
        self._converters = [
            (idx, converters[field_.type])
            for idx, field_ in enumerate(bpack.fields(self._descriptor))
            if field_.type in converters
        ]

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        values = list(self._codec.unpack(data))
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

    decode_func = utils.create_fn(
        name='decode',
        args=('data',),
        body=['return decoder.decode(data)'],
        locals={'decoder': decoder_},
    )
    decode_func = staticmethod(decode_func)
    utils.set_new_attribute(cls, 'from_bytes', decode_func)

    return cls

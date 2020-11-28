"""Bitarray based decoder for binary data structures."""

import struct

from typing import Optional

from . import utils
from .utils import classdecorator
from .descriptors import EBaseUnits, fields


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
            signed: Optional[bool] = None, repeat: Optional[int] = None):
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
            repeat = '' if repeat is None else str(repeat)
            key = (type_, signed, size)
            return f'{order}{repeat}{_TYPE_SIGNED_AND_SIZE_TO_STR[key]}'
    except KeyError:
        raise TypeError(
            f'unable to generate format string for '
            f'type="{type_}", size="{size}", order="{order}", '
            f'signed="{signed}", repeat="{repeat}"')


class Decoder:
    def __init__(self, descriptor, *, order='>'):
        if descriptor.__bpack_baseunits__ is not EBaseUnits.BYTES:
            raise ValueError(
                'struct decoder only accepts descriptors with '
                'base units "bytes"')

        if order not in ('', '>', '<', '=', '@', '!'):
            raise TypeError(f'invalid order: {order!r}')

        fmt = order + ''.join(
            _to_fmt(field.type, field.size, order='')
            for field in fields(descriptor, True)
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
        #     (field.type, field.type)
        #     for field in dataclasses.fields(self._descriptor)
        #     if issubclass(field.type, enum.Enum))
        self._converters = [
            (idx, converters[field.type])
            for idx, field in enumerate(fields(self._descriptor))
            if field.type in converters
        ]

    def decode(self, data):
        values = list(self._codec.unpack(data))
        for idx, func in self._converters:
            values[idx] = func(values[idx])
        return self._descriptor(*values)


@classdecorator
def decoder(cls, **kwargs):
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

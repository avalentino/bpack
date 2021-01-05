"""Struct based codec for binary data structures."""

import struct

from typing import Optional

import bpack
import bpack.utils

from .codec_utils import (
    get_sequence_groups, make_decoder_decorator, is_decoder, get_decoder,
)
from .descriptors import field_descriptors
from .enums import EBaseUnits


__all__ = ['Decoder', 'decoder', 'BACKEND_NAME', 'BACKEND_TYPE']


BACKEND_NAME = 'bitstruct'
BACKEND_TYPE = EBaseUnits.BYTES


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

    assert size is not None and size > 0
    assert order in ('', '>', '<', '=', '@', '!'), f'invalid order: {order!r}'
    assert signed in (True, False, None)

    if is_decoder(type_):
        decoder = get_decoder(type_)
        if isinstance(decoder, Decoder):
            return decoder._codec.format
    elif (bpack.is_descriptor(type_) and
          bpack.baseunits(type_) is Decoder.baseunits):
        decoder = Decoder(type_)
        return decoder._codec.format

    etype = bpack.utils.effective_type(type_)
    repeat = 1 if repeat is None else repeat
    try:
        if etype in (str, bytes, None):  # none is for padding bytes
            key = (etype, signed, None)
            return f'{order}{size}{_TYPE_SIGNED_AND_SIZE_TO_STR[key]}' * repeat
        else:
            key = (etype, signed, size)
            return f'{order}{repeat}{_TYPE_SIGNED_AND_SIZE_TO_STR[key]}'
    except KeyError:
        raise TypeError(
            f'unable to generate format string for '
            f'type="{type_}", size="{size}", order="{order}", '
            f'signed="{signed}", repeat="{repeat}"')


def _enum_converter_factory(type_, converters=None):
    converters = converters if converters is not None else dict()
    enum_item_type = bpack.utils.enum_item_type(type_)
    if enum_item_type in converters:
        base_converter = converters[enum_item_type]
        return lambda x: type_(base_converter(x))
    else:
        return type_


class Decoder:
    """Struct based data decoder.

    Default byte-order: MSB.
    """

    baseunits = EBaseUnits.BYTES

    def __init__(self, descriptor):
        """Initializer.

        The *descriptor* parameter* is a bpack record descriptor.
        """
        if bpack.baseunits(descriptor) is not self.baseunits:
            raise ValueError(
                f'struct decoder only accepts descriptors with '
                f'base units "{self.baseunits}"')

        assert bpack.bitorder(descriptor) is None

        byteorder = bpack.byteorder(descriptor)
        # assert all(descr.order for descr in field_descriptors(descriptor))
        byteorder = byteorder.value

        # NOTE: struct expects that the byteorder specifier is used only
        #       once at the beginning of the format string
        fmt = byteorder + ''.join(
            _to_fmt(field_descr.type, field_descr.size, order='',
                    repeat=field_descr.repeat)
            for field_descr in field_descriptors(descriptor, pad=True)
        )

        converters_map = {
            str: lambda s: s.decode('ascii'),
            bool: bool,
        }
        converters_map.update(
            (field_descr.type,
             _enum_converter_factory(field_descr.type, converters_map))
            for field_descr in field_descriptors(descriptor)
            if bpack.utils.is_enum_type(field_descr.type)
        )

        self._codec = struct.Struct(fmt)
        self._descriptor = descriptor
        self._converters = [
            (idx, converters_map[field_descr.type])
            for idx, field_descr in enumerate(
                field_descriptors(self._descriptor))
            if field_descr.type in converters_map
        ]
        self._groups = get_sequence_groups(descriptor)

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        values = list(self._codec.unpack(data))

        for idx, func in self._converters:
            values[idx] = func(values[idx])

        for type_, slice_ in self._groups[::-1]:
            subtype = type_(values[slice_])
            del values[slice_]
            values.insert(slice_.start, subtype)

        return self._descriptor(*values)


decoder = make_decoder_decorator(Decoder)

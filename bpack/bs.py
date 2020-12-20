"""Bitstruct based codec for binary data structures."""

import sys
from typing import Optional

import bitstruct

import bpack
import bpack.utils

from .codec_utils import get_sequence_groups, make_decoder_decorator
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
        """Initializer.

        The *descriptor* parameter* is a bpack record descriptor.
        """
        if bpack.baseunits(descriptor) is not bpack.EBaseUnits.BITS:
            raise ValueError(
                'bitsruct decoder only accepts descriptors with '
                'base units "bits"')

        byteorder = bpack.byteorder(descriptor)
        byteorder = _endianess_to_str(byteorder)
        bitorder = bpack.bitorder(descriptor).value

        fmt = ''.join(
            _to_fmt(field_descr.type, size=field_descr.size, bitorder=bitorder,
                    signed=field_descr.signed, repeat=field_descr.repeat)
            for field_descr in field_descriptors(descriptor, pad=True)
        )
        fmt = fmt + byteorder  # byte order

        self._codec = bitstruct.compile(fmt)
        self._descriptor = descriptor
        self._converters = [
            (idx, field.type)
            for idx, field in enumerate(bpack.fields(descriptor))
            if bpack.utils.is_enum_type(field.type)
        ]
        self._groups = get_sequence_groups(descriptor)

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        values = list(self._codec.unpack(data))

        for idx, func in self._converters:
            values[idx] = func(values[idx])

        for type_, slice_ in self._groups[::-1]:
            sub_sequence = type_(values[slice_])
            del values[slice_]
            values.insert(slice_.start, sub_sequence)

        return self._descriptor(*values)


decoder = make_decoder_decorator(Decoder)

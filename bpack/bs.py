"""Bitstruct based codec for binary data structures."""

from typing import Optional

import bitstruct

import bpack
import bpack.utils

from .codec_utils import (
    get_sequence_groups, make_decoder_decorator, is_decoder, get_decoder,
)
from .descriptors import field_descriptors
from bpack.enums import EBaseUnits, EByteOrder


__all__ = ['Decoder', 'decoder', 'BACKEND_NAME', 'BACKEND_TYPE']


BACKEND_NAME = 'bitstruct'
BACKEND_TYPE = EBaseUnits.BITS


class BitStruct(bitstruct.CompiledFormat):
    def __init__(self, format: str):                                    # noqa
        super().__init__(format)
        self._format: str = format

    @property
    def format(self) -> str:
        return self._format


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

    if is_decoder(type_):
        decoder_ = get_decoder(type_)
        if isinstance(decoder_, Decoder):
            return decoder_.format
    elif (bpack.is_descriptor(type_) and
          bpack.baseunits(type_) is Decoder.baseunits):
        decoder_ = Decoder(type_)
        return decoder_.format

    etype = bpack.utils.effective_type(type_)
    key = (etype, signed) if etype is int and signed is not None else etype

    try:
        fmt = f'{bitorder}{_TYPE_TO_STR[key]}{size}' * repeat           # noqa
    except KeyError:
        raise TypeError(f'unsupported type: {etype:!r}')

    return fmt


def _endianess_to_str(order: EByteOrder) -> str:
    if order is EByteOrder.NATIVE:
        return EByteOrder.get_native().value
    return order.value


class Decoder:
    """Bitstruct based data decoder.

    Default bit-order: MSB.
    """

    baseunits = EBaseUnits.BITS

    def __init__(self, descriptor):
        """Initializer.

        The *descriptor* parameter* is a bpack record descriptor.
        """
        if bpack.baseunits(descriptor) is not self.baseunits:
            raise ValueError(
                f'bitsruct decoder only accepts descriptors with '
                f'base units "{self.baseunits.value}"')

        byteorder = bpack.byteorder(descriptor)
        byteorder = _endianess_to_str(byteorder)
        bitorder = bpack.bitorder(descriptor).value

        fmt = ''.join(
            _to_fmt(field_descr.type, size=field_descr.size, bitorder=bitorder,
                    signed=field_descr.signed, repeat=field_descr.repeat)
            for field_descr in field_descriptors(descriptor, pad=True)
        )
        fmt = fmt + byteorder  # byte order

        codec = BitStruct(fmt)

        self._codec = codec
        self._descriptor = descriptor
        self._converters = [
            (idx, field_descr.type)
            for idx, field_descr in enumerate(field_descriptors(descriptor))
            if bpack.utils.is_enum_type(field_descr.type)
        ]
        self._groups = get_sequence_groups(descriptor)

    @property
    def format(self) -> str:
        return self._codec.format

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

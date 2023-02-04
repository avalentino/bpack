"""Struct based codec for binary data structures."""

import struct
from typing import Optional

import bpack
import bpack.utils
import bpack.codecs

from .enums import EBaseUnits
from .codecs import has_codec, get_codec
from .descriptors import field_descriptors

__all__ = [
    "Decoder",
    "decoder",
    "Encoder",
    "encoder",
    "Codec",
    "codec",
    "BACKEND_NAME",
    "BACKEND_TYPE",
]


BACKEND_NAME = "bitstruct"
BACKEND_TYPE = EBaseUnits.BYTES


_TYPE_SIGNED_AND_SIZE_TO_STR = {
    # type, signed, size
    (bool, None, 1): "?",
    (int, None, 1): "b",  # default
    (int, False, 1): "B",
    (int, True, 1): "b",
    (int, None, 2): "h",  # default
    (int, False, 2): "H",
    (int, True, 2): "h",
    (int, None, 4): "i",  # default
    (int, False, 4): "I",
    (int, True, 4): "i",
    (int, None, 8): "q",  # default
    (int, False, 8): "Q",
    (int, True, 8): "q",
    (float, None, 2): "e",
    (float, None, 4): "f",
    (float, None, 8): "d",
    (bytes, None, None): "s",
    (str, None, None): "s",
    (None, None, None): "x",  # padding
}


_DEFAULT_SIZE = {
    bool: 1,
    int: 4,
    float: 4,
    bytes: 1,
    # str: 1,
}


def _format_string_without_order(fmt: str, order: str) -> str:
    # NOTE: in the current implementation the byte order is handled
    #       externally to _to_fmt
    # if order != '':
    #     fmt = fmt[1:] if fmt.startswith(order) else fmt

    # TODO: improve.
    #       This is mainly a hack necessary because, in the current
    #       implementation, _to_fmt is always called by Decoder.__init__
    #       with order='' so here it is not possible to rely on the value
    #       of order
    if fmt[0] in {">", "<", "=", "@", "!"}:
        if order and fmt[0] != order:
            raise ValueError(
                f"inconsistent byteorder for nested record: "
                f"record byteorder is '{order}', "
                f"nested record byteorder is '{fmt[0]}'"
            )
        fmt = fmt[1:]
    # else:
    #     # TODO: how to check consistency when order=''?

    return fmt


def _to_fmt(
    type_,
    size: Optional[int] = None,
    order: str = "",
    signed: Optional[bool] = None,
    repeat: Optional[int] = None,
) -> str:
    size = _DEFAULT_SIZE.get(type_, size) if size is None else size

    assert size is not None and size > 0
    assert order in ("", ">", "<", "=", "@", "!"), f"invalid order: {order!r}"
    assert signed in (True, False, None)

    if has_codec(type_, bpack.codecs.Decoder):
        decoder_ = get_codec(type_)
        if isinstance(decoder_, Decoder):
            return _format_string_without_order(decoder_.format, order)
    elif (
        bpack.is_descriptor(type_)
        and bpack.baseunits(type_) is Decoder.baseunits
    ):
        decoder_ = Decoder(type_)
        return _format_string_without_order(decoder_.format, order)

    etype = bpack.utils.effective_type(type_)
    repeat = 1 if repeat is None else repeat
    try:
        if etype in (str, bytes, None):  # none is for padding bytes
            key = (etype, signed, None)
            return f"{order}{size}{_TYPE_SIGNED_AND_SIZE_TO_STR[key]}" * repeat
        else:
            key = (etype, signed, size)
            return f"{order}{repeat}{_TYPE_SIGNED_AND_SIZE_TO_STR[key]}"
    except KeyError:
        raise TypeError(
            f"unable to generate format string for "
            f"type='{type_}', size='{size}', order='{order}', "
            f"signed='{signed}', repeat='{repeat}'"
        )


def _enum_decode_converter_factory(type_, converters_map=None):
    converters_map = converters_map if converters_map is not None else dict()
    enum_item_type = bpack.utils.enum_item_type(type_)
    if enum_item_type in converters_map:
        base_converter = converters_map[enum_item_type]

        def to_enum(x):
            return type_(base_converter(x))

    else:
        to_enum = type_

    return to_enum


def _enum_encode_converter_factory(type_, converters_map=None):
    converters_map = converters_map if converters_map is not None else dict()
    enum_item_type = bpack.utils.enum_item_type(type_)
    if enum_item_type in converters_map:
        base_converter = converters_map[enum_item_type]

        def from_enum(x):
            return base_converter(x.value)

    else:

        def from_enum(x):
            return x.value

    return from_enum


class Codec(bpack.codecs.BaseStructCodec):
    """Struct based codec.

    Default byte-order: MSB.
    """

    baseunits = EBaseUnits.BYTES

    @staticmethod
    def _get_base_codec(descriptor):
        byteorder = bpack.byteorder(descriptor)
        # assert all(descr.order for descr in field_descriptors(descriptor))
        byteorder = byteorder.value

        # NOTE: struct expects that the byteorder specifier is used only
        #       once at the beginning of the format string
        fmt = byteorder + "".join(
            _to_fmt(
                field_descr.type,
                field_descr.size,
                order="",
                repeat=field_descr.repeat,
            )
            for field_descr in field_descriptors(descriptor, pad=True)
        )

        return struct.Struct(fmt)

    @staticmethod
    def _get_decode_converters_map(descriptor):
        converters_map = {
            str: lambda s: s.decode("ascii"),
        }
        converters_map.update(
            (
                field_descr.type,
                _enum_decode_converter_factory(
                    field_descr.type, converters_map
                ),
            )
            for field_descr in field_descriptors(descriptor)
            if bpack.utils.is_enum_type(field_descr.type)
        )
        return converters_map

    @staticmethod
    def _get_encode_converters_map(descriptor):
        converters_map = {
            str: lambda s: s.encode("ascii"),
        }
        converters_map.update(
            (
                field_descr.type,
                _enum_encode_converter_factory(
                    field_descr.type, converters_map
                ),
            )
            for field_descr in field_descriptors(descriptor)
            if bpack.utils.is_enum_type(field_descr.type)
        )
        return converters_map


codec = bpack.codecs.make_codec_decorator(Codec)
Decoder = Encoder = Codec
decoder = encoder = codec

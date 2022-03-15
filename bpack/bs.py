"""Bitstruct based codec for binary data structures."""

import math
import warnings
import functools
from typing import Optional


try:
    import cbitstruct as bitstruct
except ImportError:
    import bitstruct
    try:
        import bitstruct.c
    except ImportError:
        pass

import bpack
import bpack.utils
import bpack.codecs

from .enums import EBaseUnits, EByteOrder
from .codecs import has_codec, get_codec
from .descriptors import field_descriptors


__all__ = [
    'Decoder', 'decoder', 'Encoder', 'encoder', 'Codec', 'codec',
    'BACKEND_NAME', 'BACKEND_TYPE',
    'packbits', 'unpackbits',
]


BACKEND_NAME = 'bitstruct'
BACKEND_TYPE = EBaseUnits.BITS


class BitStruct:
    @staticmethod
    def _simplified_fmt(format: str) -> Optional[str]:
        fmt = format.replace('>', '')
        if '<' in fmt:
            return None
        else:
            return fmt

    def __init__(self, format: str, names=None):                        # noqa
        codec_ = None
        if hasattr(bitstruct, 'c'):
            fmt = self._simplified_fmt(format)
            if fmt is not None:
                try:
                    codec_ = bitstruct.c.compile(fmt, names)
                except NotImplementedError:
                    pass

        if codec_ is None:
            codec_ = bitstruct.compile(format, names)

        self._bitstruct = codec_
        self._format: str = format

    @property
    def format(self) -> str:
        return self._format

    def __getattr__(self, name):
        return getattr(self._bitstruct, name)


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


def _format_string_without_order(fmt: str, order: str) -> str:
    # NOTE: in the current implementation the byte order is handled
    #       externally to _to_fmt
    if order != '':
        fmt = fmt[:-1] if fmt.endswith(order) else fmt
    return fmt


def _to_fmt(type_, size: int, bitorder: str = '', byteorder: str = '',
            signed: Optional[bool] = None,
            repeat: Optional[int] = None) -> str:
    assert size > 0, f'invalid size: {size:r}'
    assert bitorder in ('', '>', '<'), f'invalid order: {bitorder:r}'
    if repeat is None:
        repeat = 1
    assert repeat > 0, f'invalid repeat: {repeat:r}'

    if has_codec(type_, bpack.codecs.Decoder):
        decoder_ = get_codec(type_)
        if isinstance(decoder_, Decoder):
            return _format_string_without_order(decoder_.format, byteorder)
    elif (bpack.is_descriptor(type_) and
          bpack.baseunits(type_) is Decoder.baseunits):
        decoder_ = Decoder(type_)
        return _format_string_without_order(decoder_.format, byteorder)

    etype = bpack.utils.effective_type(type_)
    key = (etype, signed) if etype is int and signed is not None else etype

    try:
        fmt = f'{bitorder}{_TYPE_TO_STR[key]}{size}' * repeat           # noqa
    except KeyError:
        raise TypeError(f'unsupported type: {etype:!r}')

    # fmt += byteorder  # NOTE: handled externally

    return fmt


def _endianess_to_str(order: EByteOrder) -> str:
    if order is EByteOrder.NATIVE:
        return EByteOrder.get_native().value
    return order.value


class Codec(bpack.codecs.BaseStructCodec):
    """Bitstruct based codec.

    Default bit-order: MSB.
    """

    baseunits = EBaseUnits.BITS

    @staticmethod
    def _get_base_codec(descriptor):
        byteorder = bpack.byteorder(descriptor)
        byteorder = _endianess_to_str(byteorder)
        bitorder = bpack.bitorder(descriptor).value

        fmt = ''.join(
            _to_fmt(field_descr.type, size=field_descr.size, bitorder=bitorder,
                    byteorder=byteorder, signed=field_descr.signed,
                    repeat=field_descr.repeat)
            for field_descr in field_descriptors(descriptor, pad=True)
        )
        fmt = fmt + byteorder  # byte order

        return BitStruct(fmt)

    @staticmethod
    def _get_decode_converters_map(descriptor):
        return {
            field_descr.type: field_descr.type
            for field_descr in field_descriptors(descriptor)
            if bpack.utils.is_enum_type(field_descr.type)
        }

    @staticmethod
    def _get_encode_converters_map(descriptor):
        def from_enum(x):
            return x.value

        converters_map = {
            field_descr.type: from_enum
            for field_descr in field_descriptors(descriptor)
            if (bpack.utils.is_enum_type(field_descr.type) and
                not issubclass(field_descr.type, int))
        }
        return converters_map


codec = bpack.codecs.make_codec_decorator(Codec)
Decoder = Encoder = Codec
decoder = encoder = codec


@functools.lru_cache()
def _get_sequence_codec(nsamples: int, bits_per_sample, signed=False,
                        byteorder: str = '') -> BitStruct:
    nbits = nsamples * bits_per_sample
    outsize = math.ceil(nbits / 8)
    npad = outsize * 8 - nbits

    if signed:
        fmt = f's{bits_per_sample:d}' * nsamples
    else:
        fmt = f'u{bits_per_sample:d}' * nsamples

    if npad > 0:
        fmt += f'p{npad:d}'

    fmt += byteorder
    return BitStruct(fmt)


def packbits(values, bits_per_sample: int, signed: bool = False,
             byteorder: str = '') -> bytes:
    """Pack integer values using the specified number of bits for each sample.

    Converts a sequence of values into a string of bytes in which each
    sample is stored according to the specified number of bits.

    Example::

                 4 samples                          3 bytes

      [samp_1, samp_2, samp_3, samp_4] --> |------|------|------|------|

                                           4 samples (6 bits per sample)

    Please note that no check that the input values actually fits in the
    specified number of bits is performed is performed.

    The function return a sting of bytes including same number of samples
    of the input plus possibly some padding bit (at the end) to fill an
    integer number of bytes.

    If ``signed`` is set to True integers are stored as signed integers.
    """
    nsamples = len(values)
    if (nsamples * bits_per_sample) % 8:
        warnings.warn(f'packing {nsamples} with {bits_per_sample} bits per '
                      f'sample requires padding')
    encoder_ = _get_sequence_codec(nsamples, bits_per_sample,
                                   signed=signed, byteorder=byteorder)
    return encoder_.pack(*values)


def unpackbits(data: bytes, bits_per_sample: int, signed: bool = False,
               byteorder: str = ''):
    """Unpack packed (integer) values form a string of bytes.

    Takes in input a string of bytes in which (integer) samples have been
    stored using ``bits_per_sample`` bit for each sample, and returns
    the sequence of corresponding Python integers.

    Example::

                 3 bytes                            4 samples

      |------|------|------|------| --> [samp_1, samp_2, samp_3, samp_4]

      4 samples (6 bits per sample)

    If ``signed`` is set to True integers are assumed to be stored as
    signed integers.
    """
    nsamples = len(data) * 8 // bits_per_sample
    decoder_ = _get_sequence_codec(nsamples, bits_per_sample,
                                   signed=signed, byteorder=byteorder)
    return decoder_.unpack(data)

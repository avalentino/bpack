"""Bitarray based decoder for binary data structures."""

import struct
import dataclasses
import collections.abc

import bitarray
import bitarray.util

from .utils import classdecorator
from .descriptor import EBaseUnits


def ba_to_float(ba, order='>'):
    if len(ba) == 32:
        return struct.unpack(f'{order}f', ba.tobytes())[0]
    elif len(ba) == 64:
        return struct.unpack(f'{order}d', ba.tobytes())[0]
    else:
        raise ValueError('ba must be 32 or 64 bits')


STD_CONVERTER_MAP = {
    int: bitarray.util.ba2int,
    bool: lambda ba: bool(bitarray.util.ba2int(ba)),
    bytes: lambda ba: ba.tobytes(),
    str: lambda ba: ba.tobytes().decode('utf-8'),
    float: ba_to_float,
    # np.float32: np.frombuffer(ba.tobytes(), dtype=np.float32).item(),
    # np.float64: np.frombuffer(ba.tobytes(), dtype=np.float64).item(),
}


class Decoder:
    def __init__(self, descriptor, converters=STD_CONVERTER_MAP):
        if descriptor._BASEUNITS is not EBaseUnits.BITS:
            raise ValueError(
                'bitarray decoder only accepts descriptors with '
                'base units "bits"')

        fields_ = dataclasses.fields(descriptor)
        types_ = [field.type for field in fields_]

        if isinstance(converters, collections.abc.Mapping):
            converters_map = converters
            converters = [converters_map.get(type_) for type_ in types_]

        assert converters is None or isinstance(converters,
                                                collections.abc.Iterable)

        self._descriptor = descriptor
        self._converters = converters
        self._slices = [
            slice(field.offset, field.offset + field.size) for field in fields_
        ]

    def decode(self, data):
        ba = bitarray.bitarray()
        ba.frombytes(data)
        values = [ba[slice_] for slice_ in self._slices]

        if self._converters is not None:
            values = [
                convert(value) if convert is not None else value
                for convert, value in zip(self._converters, values)
            ]

        return self._descriptor(*values)


@classdecorator
def decoder(cls, converter_map=STD_CONVERTER_MAP):
    decoder_ = Decoder(descriptor=cls, converters=converter_map)

    decode_func = dataclasses._create_fn(
        name='decode',
        args=('data',),
        body=['return decoder.decode(data)'],
        locals={'decoder': decoder_},
    )
    decode_func = staticmethod(decode_func)
    dataclasses._set_new_attribute(cls, 'from_bytes', decode_func)

    return cls

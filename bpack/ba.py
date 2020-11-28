"""Bitarray based decoder for binary data structures."""

import struct
import dataclasses
import collections.abc

import bitarray
import bitarray.util

from .utils import classdecorator
from .descriptors import EBaseUnits, fields


# TODO: custom ba_to_int with size


def ba_to_float(ba, order='>'):
    if len(ba) == 32:
        return struct.unpack(f'{order}f', ba.tobytes())[0]
    elif len(ba) == 64:
        return struct.unpack(f'{order}d', ba.tobytes())[0]
    else:
        raise ValueError('ba must be 32 or 64 bits')


STD_CONVERTER_MAP = {
    bool: lambda ba: bool(bitarray.util.ba2int(ba)),
    int: bitarray.util.ba2int,
    float: ba_to_float,
    bytes: lambda ba: ba.tobytes(),
    str: lambda ba: ba.tobytes().decode('ascii'),
}


class Decoder:
    def __init__(self, descriptor, converters=STD_CONVERTER_MAP):
        if descriptor.__bpack_baseunits__ is not EBaseUnits.BITS:
            raise ValueError(
                'bitarray decoder only accepts descriptors with '
                'base units "bits"')

        fields_ = fields(descriptor)
        types_ = [field.type for field in fields_]

        if isinstance(converters, collections.abc.Mapping):
            converters_map = converters
            try:
                converters = [converters_map[type_] for type_ in types_]
            except KeyError as exc:
                type_ = str(exc)
                raise TypeError(
                    f'no conversion function available for type {type_!r}')

        if converters is not None:
            if not isinstance(converters, collections.abc.Iterable):
                raise ValueError(f'invalid converters: {converters!r}')
            if len(list(converters)) != len(fields_):
                raise ValueError(
                    f'the number of converters ({len(converters)}) does not '
                    f'match the number of fields ({len(fields_)})')

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

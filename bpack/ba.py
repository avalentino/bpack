"""Bitarray based decoder for binary data structures."""

import struct
import collections.abc

import bitarray
import bitarray.util

from . import utils
from .utils import classdecorator
from .descriptors import EBaseUnits, fields, field_descriptors, baseunits


# TODO: custom ba_to_int with size


def ba_to_float(ba: bitarray.bitarray, order: str = '>') -> float:
    """Convert a bitarray into a float."""
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

DEFAULT_CONVERTERS = object()


class Decoder:
    """Bitarray based data decoder."""

    def __init__(self, descriptor, converters=DEFAULT_CONVERTERS):
        if baseunits(descriptor) is not EBaseUnits.BITS:
            raise ValueError(
                'bitarray decoder only accepts descriptors with '
                'base units "bits"')

        if converters is DEFAULT_CONVERTERS:
            converters = STD_CONVERTER_MAP

        if isinstance(converters, collections.abc.Mapping):
            converters_map = converters
            try:
                converters = [
                    converters_map[field_.type]
                    for field_ in fields(descriptor)
                ]

            except KeyError as exc:
                type_ = str(exc)
                raise TypeError(
                    f'no conversion function available for type {type_!r}')

        if converters is not None:
            converters = list(converters)
            n_fields = len(list(fields(descriptor)))
            if len(converters) != n_fields:
                raise ValueError(
                    f'the number of converters ({len(converters)}) does not '
                    f'match the number of fields ({n_fields})')

        self._descriptor = descriptor
        self._converters = converters
        self._slices = [
            slice(field_descr.offset, field_descr.offset + field_descr.size)
            for field_descr in field_descriptors(descriptor)
        ]

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
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
def decoder(cls, converter_map=DEFAULT_CONVERTERS):
    """Class decorator to add decoding methods to a descriptor classes.

    The decorator automatically generates a :class:`Decoder` object
    form the input descriptor class and attach a "from_bytes" method
    using the decoder to the descriptor class itself.
    """
    if converter_map is DEFAULT_CONVERTERS:
        converter_map = STD_CONVERTER_MAP

    decoder_ = Decoder(descriptor=cls, converters=converter_map)

    decode_func = utils.create_fn(
        name='decode',
        args=('data',),
        body=['return decoder.decode(data)'],
        locals={'decoder': decoder_},
    )
    decode_func = staticmethod(decode_func)
    utils.set_new_attribute(cls, 'from_bytes', decode_func)

    return cls

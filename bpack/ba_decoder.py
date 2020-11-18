# bitarray based decoder

import struct
import collections.abc

import bitarray
import bitarray.util


def ba_to_float(ba):
    if len(ba) == 32:
        return struct.unpack('f', ba, tobytes())
    else:
        struct.unpack('d', ba.tobytes())


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
    def __init__(self, record_type, converters=STD_CONVERTER_MAP):
        fields = dataclasses.fields(record_type)
        types_ = [field.type for field in fields]

        if isinstance(converters, collections.abc.Mapping):
            converters_map = converters
            converters = [converters_map.get(type_) for type_ in types_]

        assert converters is None or isinstance(converters,
                                                collections.abc.Iterable)

        self._record_type = record_type
        self._converters = converters
        self._slices = [
            slice(field.offset, field.offset + field.size) for field in fields
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

        return self._record_type(*values)


@decorator
def decoder(cls, converter_map=STD_CONVERTER_MAP):
    decoder_ = Decoder(record_type=cls, converters=converter_map)

    decode_func = dataclasses._create_fn(
        name='decode',
        args=('data',),
        body=['return decoder.decode(data)'],
        locals={'decoder': decoder_},
    )
    decode_func = staticmethod(decode_func)
    dataclasses._set_new_attribute(cls, 'decode', decode_func)

    return cls

"""Test bpack decoders."""

import dataclasses

import pytest

import bpack
import bpack.ba
import bpack.bs
import bpack.st


# TODO: add support for enums


@bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
@dataclasses.dataclass(frozen=True)
class BitRecord:
    # default (unsigned)
    field_1: bool = bpack.field(size=1, default=True)
    field_2: int = bpack.field(size=3, default=2)
    field_3: int = bpack.field(size=12, default=2048)
    field_4: float = bpack.field(size=32, default=1.)
    field_5: bytes = bpack.field(size=24, default=b'abc')
    field_6: str = bpack.field(size=24, default='ABC')
    # 4 padding bits ([96:100])  0b1111
    field_8: int = bpack.field(size=28, default=134217727, offset=100)

    # signed
    field_11: bool = bpack.field(size=1, default=False)
    field_12: int = bpack.field(size=3, default=-4, signed=True)
    field_13: int = bpack.field(size=12, default=-2048, signed=True)
    field_18: int = bpack.field(size=32, default=-2**31, signed=True)

    # unsigned
    field_21: bool = bpack.field(size=1, default=True)
    field_22: int = bpack.field(size=3, default=2, signed=False)
    field_23: int = bpack.field(size=12, default=2048, signed=False)
    field_28: int = bpack.field(size=32, default=2**31, signed=False)


# Big Endian
BIT_ENCODED_DATA_BE = b''.join([
    # default (unsigned)
    bytes([
        0b10101000, 0b00000000,                             # fields for 1 to 3
        0b00111111, 0b10000000, 0b00000000, 0b00000000,     # field_4 (float32)
    ]),
    b'abc',                                         # field_5 (bytes)
    'ABC'.encode('ascii'),                          # field_6 (str)
    bytes([                                         # 4 padding bits + field_8
        0b11110111, 0b11111111, 0b11111111, 0b11111111,
    ]),

    # signed
    bytes([
        0b01001000, 0b00000000,                             # fields for 1 to 3
        0b10000000, 0b00000000, 0b00000000, 0b00000000,     # field_4 (float32)
    ]),

    # unsigned
    bytes([
        0b10101000, 0b00000000,                             # fields for 1 to 3
        0b10000000, 0b00000000, 0b00000000, 0b00000000,     # field_4 (float32)
    ]),
])


@bpack.descriptor(baseunits=bpack.EBaseUnits.BYTES)
@dataclasses.dataclass(frozen=True)
class ByteRecord:
    field_01: bool = bpack.field(size=1, default=False)

    field_02: int = bpack.field(size=1, default=1)
    field_03: int = bpack.field(size=1, default=-1, signed=True)
    field_04: int = bpack.field(size=1, default=+1, signed=False)

    field_05: int = bpack.field(size=2, default=2)
    field_06: int = bpack.field(size=2, default=-2, signed=True)
    field_07: int = bpack.field(size=2, default=+2, signed=False)

    field_08: int = bpack.field(size=4, default=4)
    field_09: int = bpack.field(size=4, default=-4, signed=True)
    field_10: int = bpack.field(size=4, default=+4, signed=False)

    field_11: int = bpack.field(size=8, default=8)
    field_12: int = bpack.field(size=8, default=-8, signed=True)
    field_13: int = bpack.field(size=8, default=+8, signed=False)

    field_14: float = bpack.field(size=2, default=10.)
    field_15: float = bpack.field(size=4, default=100.)
    field_16: float = bpack.field(size=8, default=1000.)

    field_17: bytes = bpack.field(size=3, default=b'abc')
    field_18: str = bpack.field(size=3, default='ABC')

    # 4 padding bytes ([66:70]) b'xxxx'

    field_20: bytes = bpack.field(size=4, offset=70, default=b'1234')


# Big Endian
BYTE_ENCODED_DATA_BE = bytes([
    False,                                              # bool (8 bit)

    0b00000001,                                         # +1    sint8
    0b11111111,                                         # -1    sint8
    0b00000001,                                         # +1    uint8

    0b00000000, 0b00000010,                             # +2    sint16
    0b11111111, 0b11111110,                             # -2    sint16
    0b00000000, 0b00000010,                             # +2    uint16

    0b00000000, 0b00000000, 0b00000000, 0b00000100,     # +4    sint32
    0b11111111, 0b11111111, 0b11111111, 0b11111100,     # -4    sint32
    0b00000000, 0b00000000, 0b00000000, 0b00000100,     # +4    uint32

    0b00000000, 0b00000000, 0b00000000, 0b00000000,
    0b00000000, 0b00000000, 0b00000000, 0b00001000,     # +8    sint64
    0b11111111, 0b11111111, 0b11111111, 0b11111111,
    0b11111111, 0b11111111, 0b11111111, 0b11111000,     # -8    sint64
    0b00000000, 0b00000000, 0b00000000, 0b00000000,
    0b00000000, 0b00000000, 0b00000000, 0b00001000,     # +8    uint64

    0b01001001, 0b00000000,                             # 10    float16
    0b01000010, 0b11001000, 0b00000000, 0b00000000,     # 100   float32
    0b01000000, 0b10001111, 0b01000000, 0b00000000,
    0b00000000, 0b00000000, 0b00000000, 0b00000000,     # 1000  float64

    0b01100001, 0b01100010, 0b01100011,                 # b'abc'    bytes
    0b01000001, 0b01000010, 0b01000011,                 # 'ABC'     str

    # 4 padding bytes ([36:40])
    0b01111000, 0b01111000, 0b01111000, 0b01111000,     # b'xxxx'   bytes

    # field_20
    0b00110001, 0b00110010, 0b00110011, 0b00110100,     # b'1234'   bytes
])


@pytest.mark.parametrize(
    'backend, Record, encoded_data, decoded_data',
    [(bpack.ba, BitRecord, BIT_ENCODED_DATA_BE, BitRecord()),
     (bpack.bs, BitRecord, BIT_ENCODED_DATA_BE, BitRecord()),
     (bpack.st, ByteRecord, BYTE_ENCODED_DATA_BE, ByteRecord())],
    ids=['ba', 'bs', 'st'])
def test_decoder(backend, Record, encoded_data, decoded_data):  # noqa
    d = backend.Decoder(Record)
    record = d.decode(encoded_data)
    assert record == decoded_data


@pytest.mark.parametrize(
    'backend, Record, encoded_data, decoded_data',
    [(bpack.ba, BitRecord, BIT_ENCODED_DATA_BE, BitRecord()),
     (bpack.bs, BitRecord, BIT_ENCODED_DATA_BE, BitRecord()),
     (bpack.st, ByteRecord, BYTE_ENCODED_DATA_BE, ByteRecord())],
    ids=['ba', 'bs', 'st'])
def test_decoder_func(backend, Record, encoded_data, decoded_data):  # noqa
    record_type = backend.decoder(Record)
    record = record_type.from_bytes(encoded_data)
    assert record == decoded_data


@pytest.mark.parametrize('backend', [bpack.ba, bpack.bs])
def test_bit_decoder_decorator(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
    @dataclasses.dataclass(frozen=True)
    class Record:
        field_1: int = bpack.field(size=3, default=0b101)
        field_2: bool = bpack.field(size=1, default=False)
        field_3: int = bpack.field(size=12, default=2048)
        field_4: float = bpack.field(size=32, default=1.)

    decoded_data = Record()
    encoded_data = BIT_ENCODED_DATA_BE
    record = Record.from_bytes(encoded_data)

    assert record.field_1 == decoded_data.field_1
    assert record.field_2 == decoded_data.field_2
    assert record.field_3 == decoded_data.field_3
    assert record.field_4 == decoded_data.field_4


@pytest.mark.parametrize('backend', [bpack.st], ids=['st'])
def test_byte_decoder_decorator(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BYTES)
    @dataclasses.dataclass(frozen=True)
    class Record:
        field_1: int = bpack.field(size=1, default=1)
        field_2: int = bpack.field(size=2, default=2)

    decoded_data = Record()
    encoded_data = bytes([0b00000001, 0b00000000, 0b00000010])
    record = Record.from_bytes(encoded_data)

    assert record.field_1 == decoded_data.field_1
    assert record.field_2 == decoded_data.field_2


@pytest.mark.parametrize(
    'backend, baseunits',
    [(bpack.ba, bpack.EBaseUnits.BITS),
     (bpack.bs, bpack.EBaseUnits.BITS),
     (bpack.st, bpack.EBaseUnits.BYTES)],
    ids=['ba', 'bs', 'st'])
def test_unsupported_type(backend, baseunits):
    class CustomType:
        pass

    with pytest.raises(TypeError):
        @backend.decoder
        @bpack.descriptor(baseunits=baseunits)
        @dataclasses.dataclass(frozen=True)
        class Record:
            field_1: CustomType = bpack.field(size=8)

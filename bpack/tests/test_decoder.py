# -*- coding: utf-8 -*-

import dataclasses
from bpack.descriptor import descriptor, Field, EBaseUnits
from bpack import ba_decoder as ba
from bpack import bs_decoder as bs
from bpack import st_decoder as st

import pytest


# TODO: test records with offsets and pad bit/bytes
# TODO: add support for enums


@descriptor(baseunits=EBaseUnits.BITS)
@dataclasses.dataclass(frozen=True)
class BitRecord:
    field_1: bool = Field(size=1, default=True)
    field_2: int = Field(size=3, default=0b010)
    field_3: int = Field(size=12, default=2048)
    field_4: float = Field(size=32, default=1.)
    field_5: bytes = Field(size=24, default=b'abc')
    field_6: str = Field(size=24, default='ABC')


# Big Endian
BIT_ENCODED_DATA_BE = bytes(
    [0b10101000, 0b00000000, 0b00111111, 0b10000000, 0b00000000, 0b00000000]
) + b'abc' + 'ABC'.encode('ascii')


@descriptor(baseunits=EBaseUnits.BYTES)
@dataclasses.dataclass(frozen=True)
class ByteRecord:
    field_01: bool = Field(size=1, default=False)

    field_02: int = Field(size=1, default=1)
    # field_03: int = Field(size=1, default=-1, signed=True)
    # field_04: int = Field(size=1, default=+1, signed=False)

    field_05: int = Field(size=2, default=2)
    # field_06: int = Field(size=2, default=-2, signed=True)
    # field_07: int = Field(size=2, default=+2, signed=False)

    field_08: int = Field(size=4, default=4)
    # field_09: int = Field(size=4, default=-4, signed=True)
    # field_10: int = Field(size=4, default=+4, signed=False)

    field_11: int = Field(size=8, default=8)
    # field_12: int = Field(size=8, default=-8, signed=True)
    # field_13: int = Field(size=8, default=+8, signed=False)

    field_14: float = Field(size=2, default=10.)
    field_15: float = Field(size=4, default=100.)
    field_16: float = Field(size=8, default=1000.)

    field_17: bytes = Field(size=3, default=b'abc')
    field_18: str = Field(size=3, default='ABC')

    # 4 padding bytes ([36:40]) b'xxxx'

    field_20: bytes = Field(size=4, offset=40, default=b'1234')


# Big Endian
BYTE_ENCODED_DATA_BE = bytes([
    False,                                              # bool (8 bit)

    0b00000001,                                         # +1    sint8
    # 0b11111111,                                       # -1    sint8
    # 0b00000001,                                       # +1    uint8

    0b00000000, 0b00000010,                             # +2    sint16
    # 0b11111111, 0b11111110,                           # -2    sint16
    # 0b00000000, 0b00000010,                           # +2    uint16

    0b00000000, 0b00000000, 0b00000000, 0b00000100,     # +4    sint32
    # 0b11111111, 0b11111111, 0b11111111, 0b11111100,   # -4    sint32
    # 0b00000000, 0b00000000, 0b00000000, 0b00000100,   # +4    uint32

    0b00000000, 0b00000000, 0b00000000, 0b00000000,
    0b00000000, 0b00000000, 0b00000000, 0b00001000,     # +8    sint64
    # 0b11111111, 0b11111111, 0b11111111, 0b11111111,
    # 0b11111111, 0b11111111, 0b11111111, 0b11111000,   # -8    sint64
    # 0b00000000, 0b00000000, 0b00000000, 0b00000000,
    # 0b00000000, 0b00000000, 0b00000000, 0b00001000,   # +8    uint64

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
    [(ba, BitRecord, BIT_ENCODED_DATA_BE, BitRecord()),
     (bs, BitRecord, BIT_ENCODED_DATA_BE, BitRecord()),
     (st, ByteRecord, BYTE_ENCODED_DATA_BE, ByteRecord())],
    ids=['ba', 'bs', 'st'])
def test_decoder(backend, Record, encoded_data, decoded_data):
    d = backend.Decoder(Record)
    record = d.decode(encoded_data)
    assert record == decoded_data


@pytest.mark.parametrize(
    'backend, Record, encoded_data, decoded_data',
    [(ba, BitRecord, BIT_ENCODED_DATA_BE, BitRecord()),
     (bs, BitRecord, BIT_ENCODED_DATA_BE, BitRecord()),
     (st, ByteRecord, BYTE_ENCODED_DATA_BE, ByteRecord())],
    ids=['ba', 'bs', 'st'])
def test_decoder_func(backend, Record, encoded_data, decoded_data):
    record_type = backend.decoder(Record)
    record = record_type.from_bytes(encoded_data)
    assert record == decoded_data


@pytest.mark.parametrize('backend', [ba, bs])
def test_bit_decoder_decorator(backend):
    @backend.decoder
    @descriptor(baseunits=EBaseUnits.BITS)
    @dataclasses.dataclass(frozen=True)
    class Record:
        field_1: int = Field(size=3, default=0b101)
        field_2: bool = Field(size=1, default=False)
        field_3: int = Field(size=12, default=2048)
        field_4: float = Field(size=32, default=1.)

    decoded_data = Record()
    encoded_data = BIT_ENCODED_DATA_BE
    record = Record.from_bytes(encoded_data)

    assert record.field_1 == decoded_data.field_1
    assert record.field_2 == decoded_data.field_2
    assert record.field_3 == decoded_data.field_3
    assert record.field_4 == decoded_data.field_4


@pytest.mark.parametrize('backend', [st], ids=['st'])
def test_byte_decoder_decorator(backend):
    @backend.decoder
    @descriptor(baseunits=EBaseUnits.BYTES)
    @dataclasses.dataclass(frozen=True)
    class Record:
        field_1: int = Field(size=1, default=1)
        field_2: int = Field(size=2, default=2)

    decoded_data = Record()
    encoded_data = bytes([0b00000001, 0b00000000, 0b00000010])
    record = Record.from_bytes(encoded_data)

    assert record.field_1 == decoded_data.field_1
    assert record.field_2 == decoded_data.field_2


@pytest.mark.parametrize(
    'backend, baseunits',
    [(ba, EBaseUnits.BITS),
     (bs, EBaseUnits.BITS),
     (st, EBaseUnits.BYTES)],
    ids=['ba', 'bs', 'st'])
def test_unsupported_type(backend, baseunits):
    class CustomType:
        pass

    with pytest.raises(TypeError):
        @backend.decoder
        @descriptor(baseunits=baseunits)
        @dataclasses.dataclass(frozen=True)
        class Record:
            field_1: CustomType = Field(size=8)

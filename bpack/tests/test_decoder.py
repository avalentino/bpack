"""Test bpack decoders."""

import dataclasses

import pytest

import bpack
import bpack.ba
import bpack.bs
import bpack.st


# TODO: add support for enums


@pytest.mark.parametrize('backend', [bpack.ba, bpack.bs, bpack.st])
def test_backend(backend):
    assert hasattr(backend, 'BACKEND_NAME')
    assert hasattr(backend, 'BACKEND_TYPE')


@bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                  byteorder=bpack.EByteOrder.BIG,
                  bitorder=bpack.EBitOrder.MSB)
@dataclasses.dataclass(frozen=True)
class BitRecordBeMsb:
    # default (unsigned)
    field_01: bool = bpack.field(size=1, default=True)
    field_02: int = bpack.field(size=3, default=4)
    field_03: int = bpack.field(size=12, default=2048)
    field_04: float = bpack.field(size=32, default=1.)
    field_05: bytes = bpack.field(size=24, default=b'abc')
    field_06: str = bpack.field(size=24, default='ABC')
    # 4 padding bits ([96:100])
    field_08: int = bpack.field(size=28, default=134217727, offset=100)

    # signed
    field_11: bool = bpack.field(size=1, default=False)
    field_12: int = bpack.field(size=3, default=-4, signed=True)
    field_13: int = bpack.field(size=12, default=-2048, signed=True)
    field_18: int = bpack.field(size=32, default=-2**31, signed=True)

    # unsigned
    field_21: bool = bpack.field(size=1, default=True)
    field_22: int = bpack.field(size=3, default=4, signed=False)
    field_23: int = bpack.field(size=12, default=2048, signed=False)
    field_28: int = bpack.field(size=32, default=2**31, signed=False)


BIT_ENCODED_DATA_BE_MSB = b''.join([
    # default (unsigned)
    bytes([
        0b11001000, 0b00000000,                             # fields 1 to 3
        0b00111111, 0b10000000, 0b00000000, 0b00000000,     # field_4 (float32)
    ]),
    b'abc',                                                 # field_5 (bytes)
    'ABC'.encode('ascii'),                                  # field_6 (str)
    bytes([                                         # 4 padding bits + field_8
        0b00000111, 0b11111111, 0b11111111, 0b11111111,
    ]),

    # signed
    bytes([
        0b01001000, 0b00000000,                             # fields 11 to 13
        0b10000000, 0b00000000, 0b00000000, 0b00000000,     # field_18 (uint32)
    ]),

    # unsigned
    bytes([
        0b11001000, 0b00000000,                             # fields 21 to 23
        0b10000000, 0b00000000, 0b00000000, 0b00000000,     # field_28 (sint32)
    ]),
])


@bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                  byteorder=bpack.EByteOrder.LITTLE,
                  bitorder=bpack.EBitOrder.MSB)
@dataclasses.dataclass(frozen=True)
class BitRecordLeMsb:
    # default (unsigned)
    field_01: bool = bpack.field(size=1, default=True)
    field_02: int = bpack.field(size=3, default=4)
    field_03: int = bpack.field(size=12, default=2048)
    field_04: float = bpack.field(size=32, default=1.)
    field_05: bytes = bpack.field(size=24, default=b'abc')
    field_06: str = bpack.field(size=24, default='ABC')
    # 4 padding bits ([96:100])
    field_08: int = bpack.field(size=28, default=134217727, offset=100)

    # signed
    field_11: bool = bpack.field(size=1, default=False)
    field_12: int = bpack.field(size=3, default=-4, signed=True)
    field_13: int = bpack.field(size=12, default=-2048, signed=True)
    field_18: int = bpack.field(size=32, default=-2**31, signed=True)

    # unsigned
    field_21: bool = bpack.field(size=1, default=True)
    field_22: int = bpack.field(size=3, default=4, signed=False)
    field_23: int = bpack.field(size=12, default=2048, signed=False)
    field_28: int = bpack.field(size=32, default=2**31, signed=False)


BIT_ENCODED_DATA_LE_MSB = b''.join([
    # default (unsigned)
    bytes([
        0b11000000, 0b10000000,                             # fields 1 to 3
        0b00000000, 0b00000000, 0b10000000, 0b00111111,     # field_4 (float32)
    ]),
    b'abc',                                                 # field_5 (bytes)
    'ABC'.encode('ascii'),                                  # field_6 (str)
    bytes([                                         # 4 padding bits + field_8
        0b00001111, 0b11111111, 0b11111111, 0b01111111,
    ]),

    # signed
    bytes([
        0b01000000, 0b10000000,                             # fields 11 to 13
        0b00000000, 0b00000000, 0b00000000, 0b10000000,     # field_18 (sint32)
    ]),

    # unsigned
    bytes([
        0b11000000, 0b10000000,                             # fields 21 to 23
        0b00000000, 0b00000000, 0b00000000, 0b10000000,     # field_28 (uint32)
    ]),
])


@bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                  byteorder=bpack.EByteOrder.BIG,
                  bitorder=bpack.EBitOrder.LSB)
@dataclasses.dataclass(frozen=True)
class BitRecordBeLsb:
    # default (unsigned)
    field_01: bool = bpack.field(size=1, default=True)
    field_02: int = bpack.field(size=3, default=4)
    field_03: int = bpack.field(size=12, default=2048)
    field_04: float = bpack.field(size=32, default=1.)
    field_05: bytes = bpack.field(size=24, default=b'abc')
    field_06: str = bpack.field(size=24, default='ABC')
    # 4 padding bits ([96:100])
    field_08: int = bpack.field(size=28, default=134217727, offset=100)

    # signed
    field_11: bool = bpack.field(size=1, default=False)
    field_12: int = bpack.field(size=3, default=-4, signed=True)
    field_13: int = bpack.field(size=12, default=-2048, signed=True)
    field_18: int = bpack.field(size=32, default=-2**31, signed=True)

    # unsigned
    field_21: bool = bpack.field(size=1, default=True)
    field_22: int = bpack.field(size=3, default=4, signed=False)
    field_23: int = bpack.field(size=12, default=2048, signed=False)
    field_28: int = bpack.field(size=32, default=2**31, signed=False)


BIT_ENCODED_DATA_BE_LSB = b''.join([
    # default (unsigned)
    bytes([
        0b10010000, 0b00000001,                             # fields 1 to 3
        0b00000000, 0b00000000, 0b00000001, 0b11111100,     # field_4 (float32)
    ]),
    bytes([0b11000110, 0b01000110, 0b10000110]),    # field_5 (bytes) - b'abc'
    bytes([0b11000010, 0b01000010, 0b10000010]),    # field_6 (str)   - 'ABC'
    bytes([                                         # 4 padding bits + field_8
        0b00001111, 0b11111111, 0b11111111, 0b11111110,
    ]),

    # signed
    bytes([
        0b00010000, 0b00000001,                             # fields 11 to 13
        0b00000000, 0b00000000, 0b00000000, 0b00000001,     # field_18 (uint32)
    ]),

    # unsigned
    bytes([
        0b10010000, 0b00000001,                             # fields 21 to 23
        0b00000000, 0b00000000, 0b00000000, 0b00000001,     # field_28 (sint32)
    ]),
])


@bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                  byteorder=bpack.EByteOrder.LITTLE,
                  bitorder=bpack.EBitOrder.LSB)
@dataclasses.dataclass(frozen=True)
class BitRecordLeLsb:
    # default (unsigned)
    field_01: bool = bpack.field(size=1, default=True)
    field_02: int = bpack.field(size=3, default=4)
    field_03: int = bpack.field(size=12, default=2048)
    field_04: float = bpack.field(size=32, default=1.)
    field_05: bytes = bpack.field(size=24, default=b'abc')
    field_06: str = bpack.field(size=24, default='ABC')
    # 4 padding bits ([96:100])
    field_08: int = bpack.field(size=28, default=134217727, offset=100)

    # signed
    field_11: bool = bpack.field(size=1, default=False)
    field_12: int = bpack.field(size=3, default=-4, signed=True)
    field_13: int = bpack.field(size=12, default=-2048, signed=True)
    field_18: int = bpack.field(size=32, default=-2**31, signed=True)

    # unsigned
    field_21: bool = bpack.field(size=1, default=True)
    field_22: int = bpack.field(size=3, default=4, signed=False)
    field_23: int = bpack.field(size=12, default=2048, signed=False)
    field_28: int = bpack.field(size=32, default=2**31, signed=False)


BIT_ENCODED_DATA_LE_LSB = b''.join([
    # default (unsigned)
    bytes([
        0b10010001, 0b00000000,                             # fields 1 to 3
        0b11111100, 0b00000001, 0b00000000, 0b00000000,     # field_4 (float32)
    ]),
    bytes([0b11000110, 0b01000110, 0b10000110]),    # field_5 (bytes) - b'abc'
    bytes([0b11000010, 0b01000010, 0b10000010]),    # field_6 (str)   - 'ABC'
    bytes([                                         # 4 padding bits + field_8
        0b00001110, 0b11111111, 0b11111111, 0b11111111,
    ]),

    # signed
    bytes([
        0b00010001, 0b00000000,                             # fields 11 to 13
        0b00000001, 0b00000000, 0b00000000, 0b00000000,     # field_18 (sint32)
    ]),

    # unsigned
    bytes([
        0b10010001, 0b00000000,                             # fields 21 to 23
        0b00000001, 0b00000000, 0b00000000, 0b00000000,     # field_28 (uint32)
    ]),
])


@bpack.descriptor(baseunits=bpack.EBaseUnits.BYTES,
                  byteorder=bpack.EByteOrder.BIG)
@dataclasses.dataclass(frozen=True)
class ByteRecordBe:
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


@bpack.descriptor(baseunits=bpack.EBaseUnits.BYTES,
                  byteorder=bpack.EByteOrder.LITTLE)
@dataclasses.dataclass(frozen=True)
class ByteRecordLe:
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


BYTE_ENCODED_DATA_LE = bytes([
    False,                                              # bool (8 bit)

    0b00000001,                                         # +1    sint8
    0b11111111,                                         # -1    sint8
    0b00000001,                                         # +1    uint8

    0b00000010, 0b00000000,                             # +2    sint16
    0b11111110, 0b11111111,                             # -2    sint16
    0b00000010, 0b00000000,                             # +2    uint16

    0b00000100, 0b00000000, 0b00000000, 0b00000000,     # +4    sint32
    0b11111100, 0b11111111, 0b11111111, 0b11111111,     # -4    sint32
    0b00000100, 0b00000000, 0b00000000, 0b00000000,     # +4    uint32

    0b00001000, 0b00000000, 0b00000000, 0b00000000,
    0b00000000, 0b00000000, 0b00000000, 0b00000000,     # +8    sint64
    0b11111000, 0b11111111, 0b11111111, 0b11111111,
    0b11111111, 0b11111111, 0b11111111, 0b11111111,     # -8    sint64
    0b00001000, 0b00000000, 0b00000000, 0b00000000,
    0b00000000, 0b00000000, 0b00000000, 0b00000000,     # +8    uint64

    0b00000000, 0b01001001,                             # 10    float16
    0b00000000, 0b00000000, 0b11001000, 0b01000010,     # 100   float32
    0b00000000, 0b00000000, 0b00000000, 0b00000000,
    0b00000000, 0b01000000, 0b10001111, 0b01000000,     # 1000  float64

    0b01100001, 0b01100010, 0b01100011,                 # b'abc'    bytes
    0b01000001, 0b01000010, 0b01000011,                 # 'ABC'     str

    # 4 padding bytes ([36:40])
    0b01111000, 0b01111000, 0b01111000, 0b01111000,     # b'xxxx'   bytes

    # field_20
    0b00110001, 0b00110010, 0b00110011, 0b00110100,     # b'1234'   bytes
])


@pytest.mark.parametrize(
    'backend, Record, encoded_data, decoded_data',
    [(bpack.st, ByteRecordBe, BYTE_ENCODED_DATA_BE, ByteRecordBe()),
     (bpack.st, ByteRecordLe, BYTE_ENCODED_DATA_LE, ByteRecordLe()),
     (bpack.bs, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, BitRecordBeMsb()),
     (bpack.bs, BitRecordLeMsb, BIT_ENCODED_DATA_LE_MSB, BitRecordLeMsb()),
     (bpack.bs, BitRecordBeLsb, BIT_ENCODED_DATA_BE_LSB, BitRecordBeLsb()),
     (bpack.bs, BitRecordLeLsb, BIT_ENCODED_DATA_LE_LSB, BitRecordLeLsb()),
     (bpack.ba, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, BitRecordBeMsb()),
     (bpack.ba, BitRecordBeLsb, BIT_ENCODED_DATA_BE_LSB, BitRecordBeLsb())],
    ids=['st BE', 'st LE',
         'bs BE MSB', 'bs LE MSB', 'bs BE LSB', 'bs LE LSB',
         'ba BE MSB', 'ba BE LSB'])
def test_decoder(backend, Record, encoded_data, decoded_data):  # noqa
    decoder = backend.Decoder(Record)
    record = decoder.decode(encoded_data)
    assert record == decoded_data


@pytest.mark.parametrize(
    'backend, Record, encoded_data, decoded_data',
    [(bpack.st, ByteRecordBe, BYTE_ENCODED_DATA_BE, ByteRecordBe()),
     (bpack.st, ByteRecordLe, BYTE_ENCODED_DATA_LE, ByteRecordLe()),
     (bpack.bs, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, BitRecordBeMsb()),
     (bpack.bs, BitRecordLeMsb, BIT_ENCODED_DATA_LE_MSB, BitRecordLeMsb()),
     (bpack.bs, BitRecordBeLsb, BIT_ENCODED_DATA_BE_LSB, BitRecordBeLsb()),
     (bpack.bs, BitRecordLeLsb, BIT_ENCODED_DATA_LE_LSB, BitRecordLeLsb()),
     (bpack.ba, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, BitRecordBeMsb()),
     (bpack.ba, BitRecordBeLsb, BIT_ENCODED_DATA_BE_LSB, BitRecordBeLsb())],
    ids=['st BE', 'st LE',
         'bs BE MSB', 'bs LE MSB', 'bs BE LSB', 'bs LE LSB',
         'ba BE MSB', 'ba BE LSB'])
def test_decoder_func(backend, Record, encoded_data, decoded_data):  # noqa
    record_type = backend.decoder(Record)
    record = record_type.from_bytes(encoded_data)
    assert record == decoded_data


@pytest.mark.parametrize('backend', [bpack.ba, bpack.bs], ids=['ba', 'bs'])
def test_bit_decoder_decorator(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
    @dataclasses.dataclass(frozen=True)
    class Record:
        field_01: bool = bpack.field(size=1, default=True)
        field_02: int = bpack.field(size=3, default=4)
        field_03: int = bpack.field(size=12, default=2048)
        field_04: float = bpack.field(size=32, default=1.)
        field_05: bytes = bpack.field(size=24, default=b'abc')
        field_06: str = bpack.field(size=24, default='ABC')
        # 4 padding bits ([96:100])  0b1111
        field_08: int = bpack.field(size=28, default=134217727, offset=100)

    decoded_data = Record()
    encoded_data = BIT_ENCODED_DATA_BE_MSB[:bpack.calcsize(Record)]
    record = Record.from_bytes(encoded_data)

    assert record.field_01 == decoded_data.field_01
    assert record.field_02 == decoded_data.field_02
    assert record.field_03 == decoded_data.field_03
    assert record.field_04 == decoded_data.field_04
    assert record.field_05 == decoded_data.field_05
    assert record.field_06 == decoded_data.field_06
    assert record.field_08 == decoded_data.field_08


@pytest.mark.parametrize('backend', [bpack.st], ids=['st'])
def test_byte_decoder_decorator(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BYTES,
                      byteorder=bpack.EByteOrder.BIG)
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


@pytest.mark.parametrize('backend', [bpack.st], ids=['st'])
def test_byte_decoder_native_byteorder(backend):
    @backend.decoder
    @bpack.descriptor(byteorder=bpack.EByteOrder.NATIVE)
    @dataclasses.dataclass(frozen=True)
    class Record:
        field_1: int = bpack.field(size=4, default=1)


@pytest.mark.parametrize('backend', [bpack.bs], ids=['bs'])
def test_bit_decoder_native_byteorder(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                      byteorder=bpack.EByteOrder.NATIVE)
    @dataclasses.dataclass(frozen=True)
    class Record:
        field_1: int = bpack.field(size=8, default=1)


@pytest.mark.parametrize('backend', [bpack.ba, bpack.bs], ids=['ba', 'bs'])
def test_bit_decoder_default_byteorder(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                      byteorder=bpack.EByteOrder.DEFAULT)
    @dataclasses.dataclass(frozen=True)
    class Record:
        field_1: int = bpack.field(size=8, default=1)


@pytest.mark.parametrize('backend', [bpack.ba, bpack.bs], ids=['ba', 'bs'])
def test_wrong_baseunits_bit(backend):
    with pytest.raises(ValueError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BYTES)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=8, default=1)


@pytest.mark.parametrize('backend', [bpack.st], ids=['st'])
def test_wrong_baseunits_byte(backend):
    with pytest.raises(ValueError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=8, default=1)

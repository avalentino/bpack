"""Test bpack codecs."""

import sys
import enum
import struct

from typing import List, Sequence

import pytest

import bpack
import bpack.st
import bpack.codecs

try:
    import bpack.bs as bpack_bs
except ImportError:                                         # pragma: no cover
    bpack_bs = None

try:
    import bpack.ba as bpack_ba
except ImportError:                                         # pragma: no cover
    bpack_ba = None

try:
    import bpack.np as bpack_np
except ImportError:                                         # pragma: no cover
    bpack_np = None


skipif = pytest.mark.skipif

BITS_BACKENDS = [
    pytest.param(bpack_bs, id='bs',
                 marks=skipif(not bpack_bs, reason='not available')),
    pytest.param(bpack_ba, id='ba',
                 marks=skipif(not bpack_ba, reason='not available')),
]
BYTES_BACKENDS = [
    pytest.param(bpack.st, id='st'),
    pytest.param(bpack_np, id='np',
                 marks=skipif(not bpack_np, reason='not available')),
]
ALL_BACKENDS = BITS_BACKENDS + BYTES_BACKENDS


@pytest.mark.parametrize('backend', ALL_BACKENDS)
def test_backend(backend):
    assert hasattr(backend, 'BACKEND_NAME')
    assert hasattr(backend, 'BACKEND_TYPE')


@pytest.mark.parametrize('backend', ALL_BACKENDS)
def test_attrs(backend):
    codec = getattr(backend, 'codec', backend.decoder)

    @codec
    @bpack.descriptor(baseunits=backend.BACKEND_TYPE)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: int = bpack.field(size=4, default=1)

    assert hasattr(Record, bpack.descriptors.BASEUNITS_ATTR_NAME)
    assert hasattr(Record, bpack.descriptors.BYTEORDER_ATTR_NAME)
    assert hasattr(Record, bpack.descriptors.BITORDER_ATTR_NAME)
    assert hasattr(Record, bpack.descriptors.SIZE_ATTR_NAME)
    assert hasattr(Record, bpack.codecs.CODEC_ATTR_NAME)


@bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                  byteorder=bpack.EByteOrder.BE,
                  bitorder=bpack.EBitOrder.MSB,
                  frozen=True)
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
                  byteorder=bpack.EByteOrder.LE,
                  bitorder=bpack.EBitOrder.MSB,
                  frozen=True)
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
                  byteorder=bpack.EByteOrder.BE,
                  bitorder=bpack.EBitOrder.LSB,
                  frozen=True)
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
                  byteorder=bpack.EByteOrder.LE,
                  bitorder=bpack.EBitOrder.LSB,
                  frozen=True)
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
                  byteorder=bpack.EByteOrder.BE,
                  frozen=True)
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
                  byteorder=bpack.EByteOrder.LE,
                  frozen=True)
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

    # 4 padding bytes ([66:70])
    0b01111000, 0b01111000, 0b01111000, 0b01111000,     # b'xxxx'   bytes

    # field_20
    0b00110001, 0b00110010, 0b00110011, 0b00110100,     # b'1234'   bytes
])


def _fix_padding(data, refdata):
    if refdata in {BYTE_ENCODED_DATA_BE, BYTE_ENCODED_DATA_LE}:
        return data[:66] + b'xxxx' + data[70:]
    return refdata


@pytest.mark.parametrize(
    'backend, Record, encoded_data',
    [pytest.param(bpack.st, ByteRecordBe, BYTE_ENCODED_DATA_BE, id='st BE'),
     pytest.param(bpack.st, ByteRecordLe, BYTE_ENCODED_DATA_LE, id='st LE'),
     pytest.param(
         bpack_np, ByteRecordBe, BYTE_ENCODED_DATA_BE, id='np BE',
         marks=pytest.mark.skipif(not bpack_np, reason='not available')),
     pytest.param(
         bpack_np, ByteRecordLe, BYTE_ENCODED_DATA_LE, id='np LE',
         marks=pytest.mark.skipif(not bpack_np, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, id='bs BE MSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordLeMsb, BIT_ENCODED_DATA_LE_MSB, id='bs LE MSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordBeLsb, BIT_ENCODED_DATA_BE_LSB, id='bs BE LSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordLeLsb, BIT_ENCODED_DATA_LE_LSB, id='bs LE LSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_ba, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, id='ba BE MSB',
         marks=pytest.mark.skipif(not bpack_ba, reason='not available'))])
def test_decoder(backend, Record, encoded_data):                        # noqa
    decoded_data = Record()                                             # noqa

    decoder = backend.Decoder(Record)
    assert hasattr(decoder, 'baseunits')
    assert decoder.baseunits is bpack.baseunits(Record)
    record = decoder.decode(encoded_data)
    assert record == decoded_data

    if hasattr(backend, 'Codec'):
        codec = backend.Codec(Record)
        assert hasattr(codec, 'baseunits')
        assert codec.baseunits is bpack.baseunits(Record)
        record = codec.decode(encoded_data)
        assert record == decoded_data


@pytest.mark.parametrize(
    'backend, Record, encoded_data',
    [pytest.param(bpack.st, ByteRecordBe, BYTE_ENCODED_DATA_BE, id='st BE'),
     pytest.param(bpack.st, ByteRecordLe, BYTE_ENCODED_DATA_LE, id='st LE'),
     pytest.param(
         bpack_np, ByteRecordBe, BYTE_ENCODED_DATA_BE, id='np BE',
         marks=pytest.mark.skipif(not bpack_np, reason='not available')),
     pytest.param(
         bpack_np, ByteRecordLe, BYTE_ENCODED_DATA_LE, id='np LE',
         marks=pytest.mark.skipif(not bpack_np, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, id='bs BE MSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordLeMsb, BIT_ENCODED_DATA_LE_MSB, id='bs LE MSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordBeLsb, BIT_ENCODED_DATA_BE_LSB, id='bs BE LSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordLeLsb, BIT_ENCODED_DATA_LE_LSB, id='bs LE LSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_ba, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, id='ba BE MSB',
         marks=pytest.mark.skipif(not bpack_ba, reason='not available'))])
def test_decoder_func(backend, Record, encoded_data):                   # noqa
    decoded_data = Record()                                             # noqa

    record_type = backend.decoder(Record)
    record = record_type.frombytes(encoded_data)
    assert record == decoded_data

    if hasattr(backend, 'codec'):
        record_type = backend.codec(Record)
        record = record_type.frombytes(encoded_data)
        assert record == decoded_data


@pytest.mark.parametrize(
    'backend, Record, encoded_data',
    [pytest.param(bpack.st, ByteRecordBe, BYTE_ENCODED_DATA_BE, id='st BE'),
     pytest.param(bpack.st, ByteRecordLe, BYTE_ENCODED_DATA_LE, id='st LE'),
     pytest.param(
         bpack_np, ByteRecordBe, BYTE_ENCODED_DATA_BE, id='np BE',
         marks=pytest.mark.skipif(not bpack_np, reason='not available')),
     pytest.param(
         bpack_np, ByteRecordLe, BYTE_ENCODED_DATA_LE, id='np LE',
         marks=pytest.mark.skipif(not bpack_np, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, id='bs BE MSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordLeMsb, BIT_ENCODED_DATA_LE_MSB, id='bs LE MSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordBeLsb, BIT_ENCODED_DATA_BE_LSB, id='bs BE LSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordLeLsb, BIT_ENCODED_DATA_LE_LSB, id='bs LE LSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available'))])
def test_encoder(backend, Record, encoded_data):                        # noqa
    record = Record()                                                   # noqa

    encoder = backend.Encoder(Record)
    assert hasattr(encoder, 'baseunits')
    assert encoder.baseunits is bpack.baseunits(Record)
    data = encoder.encode(record)
    if backend.BACKEND_TYPE is bpack.EBaseUnits.BYTES:
        data = _fix_padding(data, encoded_data)
    assert data == encoded_data

    codec = backend.Codec(Record)
    assert hasattr(codec, 'baseunits')
    assert codec.baseunits is bpack.baseunits(Record)
    data = codec.encode(record)
    if backend.BACKEND_TYPE is bpack.EBaseUnits.BYTES:
        data = _fix_padding(data, encoded_data)
    assert data == encoded_data


@pytest.mark.parametrize(
    'backend, Record, encoded_data',
    [pytest.param(bpack.st, ByteRecordBe, BYTE_ENCODED_DATA_BE, id='st BE'),
     pytest.param(bpack.st, ByteRecordLe, BYTE_ENCODED_DATA_LE, id='st LE'),
     pytest.param(
         bpack_np, ByteRecordBe, BYTE_ENCODED_DATA_BE, id='np BE',
         marks=pytest.mark.skipif(not bpack_np, reason='not available')),
     pytest.param(
         bpack_np, ByteRecordLe, BYTE_ENCODED_DATA_LE, id='np LE',
         marks=pytest.mark.skipif(not bpack_np, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB, id='bs BE MSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordLeMsb, BIT_ENCODED_DATA_LE_MSB, id='bs LE MSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordBeLsb, BIT_ENCODED_DATA_BE_LSB, id='bs BE LSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available')),
     pytest.param(
         bpack_bs, BitRecordLeLsb, BIT_ENCODED_DATA_LE_LSB, id='bs LE LSB',
         marks=pytest.mark.skipif(not bpack_bs, reason='not available'))])
def test_encoder_func(backend, Record, encoded_data):                   # noqa
    record = Record()                                                   # noqa

    record_type = backend.encoder(Record)
    data = record_type.tobytes(record)
    if backend.BACKEND_TYPE is bpack.EBaseUnits.BYTES:
        data = _fix_padding(data, encoded_data)
    assert data == encoded_data

    record_type = backend.codec(Record)
    data = record_type.tobytes(record)
    if backend.BACKEND_TYPE is bpack.EBaseUnits.BYTES:
        data = _fix_padding(data, encoded_data)
    assert data == encoded_data


@pytest.mark.parametrize('backend', BITS_BACKENDS)
def test_bit_decoder_decorator_frombytes(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS, frozen=True)
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
    record = Record.frombytes(encoded_data)

    assert record.field_01 == decoded_data.field_01
    assert record.field_02 == decoded_data.field_02
    assert record.field_03 == decoded_data.field_03
    assert record.field_04 == decoded_data.field_04
    assert record.field_05 == decoded_data.field_05
    assert record.field_06 == decoded_data.field_06
    assert record.field_08 == decoded_data.field_08


@pytest.mark.parametrize(
    'backend',
    [pytest.param(
        bpack_bs, id='bs', marks=skipif(not bpack_bs,
                                        reason='not available'))])
def test_bit_encoder_decorator_tobytes(backend):
    @backend.encoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS, frozen=True)
    class Record:
        field_01: bool = bpack.field(size=1, default=True)
        field_02: int = bpack.field(size=3, default=4)
        field_03: int = bpack.field(size=12, default=2048)
        field_04: float = bpack.field(size=32, default=1.)
        field_05: bytes = bpack.field(size=24, default=b'abc')
        field_06: str = bpack.field(size=24, default='ABC')
        # 4 padding bits ([96:100])  0b1111
        field_08: int = bpack.field(size=28, default=134217727, offset=100)

    encoded_data = BIT_ENCODED_DATA_BE_MSB[:bpack.calcsize(Record)]
    record = Record()
    data = record.tobytes()
    data = _fix_padding(data, encoded_data)

    assert data == encoded_data


@pytest.mark.parametrize('backend', BYTES_BACKENDS)
def test_byte_decoder_decorator_frombytes(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BYTES,
                      byteorder=bpack.EByteOrder.BE,
                      frozen=True)
    class Record:
        field_1: int = bpack.field(size=1, default=1)
        field_2: int = bpack.field(size=2, default=2)

    decoded_data = Record()
    encoded_data = bytes([0b00000001, 0b00000000, 0b00000010])
    record = Record.frombytes(encoded_data)

    assert record.field_1 == decoded_data.field_1
    assert record.field_2 == decoded_data.field_2


@pytest.mark.parametrize('backend', BYTES_BACKENDS)
def test_byte_encoder_decorator_tobytes(backend):
    @backend.encoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BYTES,
                      byteorder=bpack.EByteOrder.BE,
                      frozen=True)
    class Record:
        field_1: int = bpack.field(size=1, default=1)
        field_2: int = bpack.field(size=2, default=2)

    encoded_data = bytes([0b00000001, 0b00000000, 0b00000010])
    record = Record()
    data = record.tobytes()

    assert data == encoded_data


@pytest.mark.parametrize('backend', ALL_BACKENDS)
def test_unsupported_type(backend):
    class CustomType:
        pass

    codec = getattr(backend, 'codec', backend.decoder)

    with pytest.raises(TypeError):
        @codec
        @bpack.descriptor(baseunits=backend.Decoder.baseunits, frozen=True)
        class Record:                                                   # noqa
            field_1: CustomType = bpack.field(size=8)


@pytest.mark.parametrize('backend', BYTES_BACKENDS)
def test_byte_decoder_native_byteorder_frombytes(backend):
    size = 4
    value = 1

    @backend.decoder
    @bpack.descriptor(byteorder=bpack.EByteOrder.NATIVE, frozen=True)
    class Record:
        field_1: int = bpack.field(size=size, default=value)

    data = value.to_bytes(size, sys.byteorder)
    assert Record.frombytes(data) == Record()


@pytest.mark.parametrize('backend', BYTES_BACKENDS)
def test_byte_encoder_native_byteorder_tobytes(backend):
    size = 4
    value = 1

    @backend.encoder
    @bpack.descriptor(byteorder=bpack.EByteOrder.NATIVE, frozen=True)
    class Record:
        field_1: int = bpack.field(size=size, default=value)

    record = Record()
    data = value.to_bytes(size, sys.byteorder)
    assert record.tobytes() == data


@pytest.mark.parametrize(
    'backend',
    [pytest.param(bpack_bs, id='bs',
                  marks=skipif(not bpack_bs, reason='not available'))])
def test_bit_decoder_native_byteorder_frombytes(backend):
    size = 64
    value = 1

    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                      byteorder=bpack.EByteOrder.NATIVE,
                      frozen=True)
    class Record:
        field_1: int = bpack.field(size=size, default=value)

    data = value.to_bytes(size // 8, sys.byteorder)
    assert Record.frombytes(data) == Record()


@pytest.mark.parametrize(
    'backend',
    [pytest.param(bpack_bs, id='bs',
                  marks=skipif(not bpack_bs, reason='not available'))])
def test_bit_encoder_native_byteorder_tobytes(backend):
    size = 64
    value = 1

    @backend.encoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                      byteorder=bpack.EByteOrder.NATIVE,
                      frozen=True)
    class Record:
        field_1: int = bpack.field(size=size, default=value)

    record = Record()
    data = value.to_bytes(size // 8, sys.byteorder)
    assert record.tobytes() == data


@pytest.mark.parametrize('backend', BITS_BACKENDS)
def test_bit_decoder_default_byteorder_frombytes(backend):
    size = 64
    value = 1

    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                      byteorder=bpack.EByteOrder.DEFAULT,
                      frozen=True)
    class Record:
        field_1: int = bpack.field(size=size, default=value)

    # default byte order is big for bit descriptors
    data = value.to_bytes(size // 8, 'big')
    assert Record.frombytes(data) == Record()


@pytest.mark.parametrize(
    'backend',
    [pytest.param(bpack_bs, id='bs',
                  marks=skipif(not bpack_bs, reason='not available'))])
def test_bit_encoder_default_byteorder_tobytes(backend):
    size = 64
    value = 1

    @backend.encoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                      byteorder=bpack.EByteOrder.DEFAULT,
                      frozen=True)
    class Record:
        field_1: int = bpack.field(size=size, default=value)

    record = Record()
    # default byte order is big for bit descriptors
    data = value.to_bytes(size // 8, 'big')  # default is "big" for bits
    assert record.tobytes() == data


@pytest.mark.parametrize('backend', BITS_BACKENDS)
def test_wrong_baseunits_bit(backend):
    codec = getattr(backend, 'codec', backend.decoder)

    with pytest.raises(ValueError):
        @codec
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BYTES)
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=8, default=1)


@pytest.mark.parametrize('backend', BYTES_BACKENDS)
def test_wrong_baseunits_byte(backend):
    codec = getattr(backend, 'codec', backend.decoder)

    with pytest.raises(ValueError):
        @codec
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=8, default=1)


@pytest.mark.parametrize('backend', ALL_BACKENDS)
def test_enum_decoding_bytes(backend):
    class EStrEnumType(enum.Enum):
        A = 'a'
        B = 'b'

    class EBytesEnumType(enum.Enum):
        A = b'a'
        B = b'b'

    class EIntEnumType(enum.Enum):
        A = 1
        B = 2

    class EFlagEnumType(enum.Enum):
        A = 1
        B = 2

    if backend.Decoder.baseunits is bpack.EBaseUnits.BYTES:
        bitorder = None
        ssize = 1
        isize = 1
        encoded_data = b''.join([
            EStrEnumType.A.value.encode('ascii'),
            EBytesEnumType.A.value,
            EIntEnumType.A.value.to_bytes(1, 'little', signed=False),
            EFlagEnumType.A.value.to_bytes(1, 'little', signed=False),
        ])
    else:
        bitorder = bpack.EBitOrder.MSB
        ssize = 8
        isize = 4
        encoded_data = b''.join([
            EStrEnumType.A.value.encode('ascii'),
            EBytesEnumType.A.value,
            bytes([0b00010001])
        ])

    @backend.decoder
    @bpack.descriptor(baseunits=backend.Decoder.baseunits, bitorder=bitorder)
    class Record:
        field_1: EStrEnumType = bpack.field(size=ssize, default=EStrEnumType.A)
        field_2: EBytesEnumType = bpack.field(size=ssize,
                                              default=EBytesEnumType.A)
        field_3: EIntEnumType = bpack.field(size=isize, default=EIntEnumType.A)
        field_4: EFlagEnumType = bpack.field(size=isize,
                                             default=EFlagEnumType.A)

    record = Record.frombytes(encoded_data)
    assert record == Record()


@pytest.mark.parametrize(
    'backend',
    [pytest.param(bpack.st, id='st'),
     pytest.param(bpack_bs, id='bs',
                  marks=skipif(not bpack_bs, reason='not available')),
     pytest.param(bpack_np, id='np',
                  marks=skipif(not bpack_np, reason='not available'))])
def test_enum_encoding_bytes(backend):
    class EStrEnumType(enum.Enum):
        A = 'a'
        B = 'b'

    class EBytesEnumType(enum.Enum):
        A = b'a'
        B = b'b'

    class EIntEnumType(enum.Enum):
        A = 1
        B = 2

    class EFlagEnumType(enum.Enum):
        A = 1
        B = 2

    if backend.Decoder.baseunits is bpack.EBaseUnits.BYTES:
        bitorder = None
        ssize = 1
        isize = 1
        encoded_data = b''.join([
            EStrEnumType.A.value.encode('ascii'),
            EBytesEnumType.A.value,
            EIntEnumType.A.value.to_bytes(1, 'little', signed=False),
            EFlagEnumType.A.value.to_bytes(1, 'little', signed=False),
        ])
    else:
        bitorder = bpack.EBitOrder.MSB
        ssize = 8
        isize = 4
        encoded_data = b''.join([
            EStrEnumType.A.value.encode('ascii'),
            EBytesEnumType.A.value,
            bytes([0b00010001])
        ])

    @backend.encoder
    @bpack.descriptor(baseunits=backend.Decoder.baseunits, bitorder=bitorder)
    class Record:
        field_1: EStrEnumType = bpack.field(size=ssize, default=EStrEnumType.A)
        field_2: EBytesEnumType = bpack.field(size=ssize,
                                              default=EBytesEnumType.A)
        field_3: EIntEnumType = bpack.field(size=isize, default=EIntEnumType.A)
        field_4: EFlagEnumType = bpack.field(size=isize,
                                             default=EFlagEnumType.A)

    record = Record()
    data = record.tobytes()
    assert data == encoded_data


@pytest.mark.parametrize(
    'backend',
    [pytest.param(bpack.st, id='st'),
     pytest.param(bpack_bs, id='bs',
                  marks=skipif(not bpack_bs, reason='not available'))])
def test_decode_sequence(backend):
    if backend.Decoder.baseunits is bpack.EBaseUnits.BYTES:
        bitorder = None
        size = 1
        repeat = 2
        encoded_data = bytes([3, 3, 4, 4])
    else:
        bitorder = bpack.EBitOrder.MSB
        size = 4
        repeat = 2
        encoded_data = bytes([0b00110011, 0b01000100])

    @backend.decoder
    @bpack.descriptor(baseunits=backend.Decoder.baseunits, bitorder=bitorder)
    class Record:
        field_1: List[int] = bpack.field(size=size, repeat=repeat)
        field_2: Sequence[int] = bpack.field(size=size, repeat=repeat)

    ref_record = Record([3, 3], (4, 4))
    record = Record.frombytes(encoded_data)
    assert record == ref_record

    assert type(record.field_1) is list
    assert type(record.field_2) is tuple

    for field, sequence_type in zip(bpack.fields(Record),
                                    (List[int], Sequence[int])):
        assert field.type == sequence_type


@pytest.mark.parametrize(
    'backend',
    [pytest.param(bpack.st, id='st'),
     pytest.param(bpack_bs, id='bs',
                  marks=skipif(not bpack_bs, reason='not available'))])
def test_encode_sequence(backend):
    if backend.Decoder.baseunits is bpack.EBaseUnits.BYTES:
        bitorder = None
        size = 1
        repeat = 2
        encoded_data = bytes([3, 3, 4, 4])
    else:
        bitorder = bpack.EBitOrder.MSB
        size = 4
        repeat = 2
        encoded_data = bytes([0b00110011, 0b01000100])

    @backend.encoder
    @bpack.descriptor(baseunits=backend.Decoder.baseunits, bitorder=bitorder)
    class Record:
        field_1: List[int] = bpack.field(size=size, repeat=repeat)
        field_2: Sequence[int] = bpack.field(size=size, repeat=repeat)

    record = Record([3, 3], (4, 4))
    data = record.tobytes()
    assert data == encoded_data


@pytest.mark.parametrize(
    'backend',
    [pytest.param(bpack.st, id='st'),
     pytest.param(bpack_bs, id='bs',
                  marks=skipif(not bpack_bs, reason='not available')),
     pytest.param(bpack_np, id='np',
                  marks=skipif(not bpack_np, reason='not available'))])
class TestNestedRecord:
    @staticmethod
    def get_encoded_data(baseunits):
        if baseunits is bpack.EBaseUnits.BYTES:
            # TODO: use the default byte order
            encoded_data = bytes([
                0b00000000, 0b00000000, 0b00000000, 0b00000000,
                0b00000001, 0b00000000, 0b00000000, 0b00000000,
                0b00000010, 0b00000000, 0b00000000, 0b00000000,
                0b00000011, 0b00000000, 0b00000000, 0b00000000,
                0b00000001, 0b00000000, 0b00000000, 0b00000000,
                0b00000010, 0b00000000, 0b00000000, 0b00000000,
            ])

        else:  # baseunits is bpack.EBaseUnits.BITS:
            encoded_data = bytes([0b00000001, 0b00100011, 0b000010010])

        return encoded_data

    def test_nested_record_decoder(self, backend):
        encoded_data = self.get_encoded_data(backend.Decoder.baseunits)

        @backend.decoder  # NOTE: this is a decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class Record:
            field_1: int = bpack.field(size=4, default=1)
            field_2: int = bpack.field(size=4, default=2)

        @backend.decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: Record = Record()
            field_3: int = bpack.field(size=4, default=3)
            field_4: Record = Record()

        assert NestedRecord.frombytes(encoded_data) == NestedRecord()

    def test_nested_record_encoder(self, backend):
        encoded_data = self.get_encoded_data(backend.Decoder.baseunits)

        @backend.encoder  # NOTE: this is an encoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class Record:
            field_1: int = bpack.field(size=4, default=1)
            field_2: int = bpack.field(size=4, default=2)

        @backend.encoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: Record = Record()
            field_3: int = bpack.field(size=4, default=3)
            field_4: Record = Record()

        record = NestedRecord()
        assert record.tobytes() == encoded_data

    def test_nested_record_frombytes(self, backend):
        encoded_data = self.get_encoded_data(backend.Decoder.baseunits)

        # NOTE: this time the inner record is not a decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class Record:
            field_1: int = bpack.field(size=4, default=1)
            field_2: int = bpack.field(size=4, default=2)

        @backend.decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: Record = Record()
            field_3: int = bpack.field(size=4, default=3)
            field_4: Record = Record()

        assert NestedRecord.frombytes(encoded_data) == NestedRecord()

    def test_nested_record_tobytes(self, backend):
        encoded_data = self.get_encoded_data(backend.Decoder.baseunits)

        # NOTE: this time the inner record is not a decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class Record:
            field_1: int = bpack.field(size=4, default=1)
            field_2: int = bpack.field(size=4, default=2)

        @backend.encoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: Record = Record()
            field_3: int = bpack.field(size=4, default=3)
            field_4: Record = Record()

        record = NestedRecord()
        assert record.tobytes() == encoded_data

    def test_nested_record_decoder_with_order(self, backend):
        encoded_data = self.get_encoded_data(backend.Decoder.baseunits)
        if backend.Decoder.baseunits is bpack.EBaseUnits.BITS:
            kwargs = dict(bitorder='>', byteorder='>')
        else:
            # TODO: use the default byteorder (see get_encoded_data)
            kwargs = dict(byteorder=bpack.EByteOrder.LE)

        @backend.decoder  # NOTE: this is a decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits, **kwargs)
        class Record:
            field_1: int = bpack.field(size=4, default=1)
            field_2: int = bpack.field(size=4, default=2)

        @backend.decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits, **kwargs)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: Record = Record()
            field_3: int = bpack.field(size=4, default=3)
            field_4: Record = Record()

        assert NestedRecord.frombytes(encoded_data) == NestedRecord()

    def test_nested_record_encoder_with_order(self, backend):
        encoded_data = self.get_encoded_data(backend.Decoder.baseunits)
        if backend.Decoder.baseunits is bpack.EBaseUnits.BITS:
            kwargs = dict(bitorder='>', byteorder='>')
        else:
            # TODO: use the default byteorder (see get_encoded_data)
            kwargs = dict(byteorder=bpack.EByteOrder.LE)

        @backend.encoder  # NOTE: this is a encoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits, **kwargs)
        class Record:
            field_1: int = bpack.field(size=4, default=1)
            field_2: int = bpack.field(size=4, default=2)

        @backend.encoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits, **kwargs)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: Record = Record()
            field_3: int = bpack.field(size=4, default=3)
            field_4: Record = Record()

        record = NestedRecord()
        assert record.tobytes() == encoded_data


@pytest.mark.parametrize(
    'backend',
    [pytest.param(bpack.st, id='st'),
     # pytest.param(bpack_np, id='np',
     #              marks=skipif(not bpack_np, reason='not available'))
     pytest.param(bpack_bs, id='bs',
                  marks=skipif(not bpack_bs, reason='not available'))])
class TestMultiNestedRecord:
    def _record_to_list(self, record):
        from bpack.utils import is_sequence_type
        out = []
        for filed in bpack.fields(record):
            value = getattr(record, filed.name)
            if bpack.is_descriptor(value):
                out.extend(self._record_to_list(value))
            elif is_sequence_type(filed.type):
                out.extend(value)
            else:
                out.append(value)
        return out

    def _bytes_record_to_data(self, record):
        from bpack import st as _st
        values = self._record_to_list(record)
        decoder = _st.Decoder(type(record))
        fmt = decoder.format
        values = [getattr(v, 'value', v) for v in values]
        return struct.pack(fmt, *values)

    def _bits_record_to_data(self, record):
        # TODO: check
        import bitstruct
        from bpack import bs as _bs
        values = self._record_to_list(record)
        decoder = _bs.Decoder(type(record))
        fmt = decoder.format
        values = [getattr(v, 'value', v) for v in values]
        return bitstruct.pack(fmt, *values)

    def _record_to_data(self, record):
        baseunits = bpack.baseunits(record)
        if baseunits is bpack.EBaseUnits.BYTES:
            data = self._bytes_record_to_data(record)
        else:
            data = self._bits_record_to_data(record)
        nbytes = bpack.calcsize(record, bpack.EBaseUnits.BYTES)
        assert len(data) == nbytes
        return data

    def test_decode_nested_record_two_levels(self, backend):
        class EEnum(enum.Enum):
            ONE = 1
            FOUR = 4

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel02:
            field_01: EEnum = bpack.field(size=4, default=EEnum.ONE)
            field_02: int = bpack.field(size=4, default=2)

        @backend.decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: RecordLevel02 = RecordLevel02()
            field_3: int = bpack.field(size=4, default=3)
            field_4: RecordLevel02 = RecordLevel02(EEnum.FOUR, 5)

        record = NestedRecord()
        encoded_data = self._record_to_data(record)
        assert NestedRecord.frombytes(encoded_data) == record

    def test_encode_nested_record_two_levels(self, backend):
        class EEnum(enum.Enum):
            ONE = 1
            FOUR = 4

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel02:
            field_01: EEnum = bpack.field(size=4, default=EEnum.ONE)
            field_02: int = bpack.field(size=4, default=2)

        @backend.codec
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: RecordLevel02 = RecordLevel02()
            field_3: int = bpack.field(size=4, default=3)
            field_4: RecordLevel02 = RecordLevel02(EEnum.FOUR, 5)

        record = NestedRecord()
        encoded_data = self._record_to_data(record)
        assert record.tobytes() == encoded_data

    def test_decode_nested_record_three_levels(self, backend):
        class EEnum(enum.Enum):
            ONE = 1
            TWO = 2
            SEVEN = 7

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel03:
            field_001: EEnum = bpack.field(size=4, default=EEnum.ONE)
            field_002: int = bpack.field(size=4, default=2)

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel02:
            field_01: int = bpack.field(size=4, default=1)
            field_02: RecordLevel03 = RecordLevel03(EEnum.TWO, 3)
            field_03: int = bpack.field(size=4, default=4)

        @backend.decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: RecordLevel02 = RecordLevel02()
            field_3: int = bpack.field(size=4, default=5)
            field_4: RecordLevel02 = RecordLevel02(
                6, RecordLevel03(EEnum.SEVEN, 8), 9)

        record = NestedRecord()
        encoded_data = self._record_to_data(record)
        assert NestedRecord.frombytes(encoded_data) == record

    def test_encode_nested_record_three_levels(self, backend):
        class EEnum(enum.Enum):
            ONE = 1
            TWO = 2
            SEVEN = 7

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel03:
            field_001: EEnum = bpack.field(size=4, default=EEnum.ONE)
            field_002: int = bpack.field(size=4, default=2)

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel02:
            field_01: int = bpack.field(size=4, default=1)
            field_02: RecordLevel03 = RecordLevel03(EEnum.TWO, 3)
            field_03: int = bpack.field(size=4, default=4)

        @backend.codec
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: RecordLevel02 = RecordLevel02()
            field_3: int = bpack.field(size=4, default=5)
            field_4: RecordLevel02 = RecordLevel02(
                6, RecordLevel03(EEnum.SEVEN, 8), 9)

        record = NestedRecord()
        encoded_data = self._record_to_data(record)
        assert record.tobytes() == encoded_data

    def test_decode_nested_record_four_levels(self, backend):
        class EEnum(enum.Enum):
            ONE = 1
            THREE = 3
            TEN = 10

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel04:
            field_0001: EEnum = bpack.field(size=4, default=EEnum.ONE)
            field_0002: int = bpack.field(size=4, default=2)

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel03:
            field_001: int = bpack.field(size=4, default=1)
            field_002: RecordLevel04 = RecordLevel04()
            field_003: int = bpack.field(size=4, default=3)

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel02:
            field_01: int = bpack.field(size=4, default=1)
            field_02: RecordLevel03 = RecordLevel03(
                2, RecordLevel04(EEnum.THREE, 4), 5)
            field_03: int = bpack.field(size=4, default=6)

        @backend.decoder
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: RecordLevel02 = RecordLevel02()
            field_3: int = bpack.field(size=4, default=7)
            field_4: RecordLevel02 = RecordLevel02(
                8, RecordLevel03(9, RecordLevel04(EEnum.TEN, 11), 12), 13)

        record = NestedRecord()
        encoded_data = self._record_to_data(record)
        assert NestedRecord.frombytes(encoded_data) == record

    def test_encode_nested_record_four_levels(self, backend):
        class EEnum(enum.Enum):
            ONE = 1
            THREE = 3
            TEN = 10

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel04:
            field_0001: EEnum = bpack.field(size=4, default=EEnum.ONE)
            field_0002: int = bpack.field(size=4, default=2)

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel03:
            field_001: int = bpack.field(size=4, default=1)
            field_002: RecordLevel04 = RecordLevel04()
            field_003: int = bpack.field(size=4, default=3)

        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class RecordLevel02:
            field_01: int = bpack.field(size=4, default=1)
            field_02: RecordLevel03 = RecordLevel03(
                2, RecordLevel04(EEnum.THREE, 4), 5)
            field_03: int = bpack.field(size=4, default=6)

        @backend.codec
        @bpack.descriptor(baseunits=backend.Decoder.baseunits)
        class NestedRecord:
            field_1: int = bpack.field(size=4, default=0)
            field_2: RecordLevel02 = RecordLevel02()
            field_3: int = bpack.field(size=4, default=7)
            field_4: RecordLevel02 = RecordLevel02(
                8, RecordLevel03(9, RecordLevel04(EEnum.TEN, 11), 12), 13)

        record = NestedRecord()
        encoded_data = self._record_to_data(record)
        assert record.tobytes() == encoded_data

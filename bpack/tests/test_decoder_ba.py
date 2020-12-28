"""Specific tests for the bitarray based decoder."""

import dataclasses
from typing import List, Sequence

import pytest

from . import test_decoder as _test_decoder
from .test_decoder import BitRecordBeMsb, BIT_ENCODED_DATA_BE_MSB

import bpack
bpack_ba = pytest.importorskip('bpack.ba')


def test_backend_ba():
    _test_decoder.test_backend(backend=bpack_ba)


def test_decoder_ba():
    _test_decoder.test_decoder(bpack_ba, BitRecordBeMsb,
                               BIT_ENCODED_DATA_BE_MSB, BitRecordBeMsb())


def test_decoder_func_ba():
    _test_decoder.test_decoder_func(bpack_ba, BitRecordBeMsb,
                                    BIT_ENCODED_DATA_BE_MSB, BitRecordBeMsb())


def test_bit_decoder_decorator_ba():
    _test_decoder.test_bit_decoder_decorator(backend=bpack_ba)


def test_unsupported_type_ba():
    _test_decoder.test_unsupported_type(backend=bpack_ba)


def test_bit_decoder_default_byteorder_ba():
    _test_decoder.test_bit_decoder_default_byteorder(backend=bpack_ba)


def test_wrong_baseunits_bit_ba():
    _test_decoder.test_wrong_baseunits_bit(backend=bpack_ba)


def test_enum_decoding_bytes_ba():
    _test_decoder.test_enum_decoding_bytes(backend=bpack_ba)


@pytest.mark.parametrize(
    'size, data',
    [(16, bytes([0b00111100, 0b00000000])),
     (32, bytes([0b00111111, 0b10000000, 0b00000000, 0b00000000])),
     (64, bytes([0b00111111, 0b11110000, 0b00000000, 0b00000000,
                 0b00000000, 0b00000000, 0b00000000, 0b00000000]))],
    ids=['float16', 'float32', 'float64'])
def test_float(size, data):
    backend = bpack_ba

    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
    @dataclasses.dataclass
    class Record:
        field_1: float = bpack.field(size=size)

    record = Record.from_bytes(data)
    assert record.field_1 == 1.


def test_invalid_float_size():
    backend = bpack_ba

    with pytest.raises(ValueError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
        @dataclasses.dataclass
        class Record:
            field_1: float = bpack.field(size=80)


def test_little_endian():
    backend = bpack_ba

    with pytest.raises(NotImplementedError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                          byteorder=bpack.EByteOrder.LITTLE)
        @dataclasses.dataclass(frozen=True)
        class Record:
            field_1: int = bpack.field(size=8, default=1)


def test_invalid_bitorder():
    backend = bpack_ba

    with pytest.raises(NotImplementedError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                          bitorder=bpack.EBitOrder.LSB)
        @dataclasses.dataclass(frozen=True)
        class Record:
            field_1: int = bpack.field(size=8, default=1)


def test_sequence():
    backend = bpack_ba

    with pytest.raises(TypeError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
        @dataclasses.dataclass
        class Record:
            field_1: List[int] = bpack.field(size=4, signed=False,
                                             repeat=2, default=3)
            field_2: Sequence[int] = bpack.field(size=4, signed=False,
                                                 repeat=2, default=4)

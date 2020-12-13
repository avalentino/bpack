"""Specific tests for the bitarray based decoder."""

import dataclasses
import pytest
import bpack
import bpack.ba


@pytest.mark.parametrize(
    'size, data',
    [(16, bytes([0b00111100, 0b00000000])),
     (32, bytes([0b00111111, 0b10000000, 0b00000000, 0b00000000])),
     (64, bytes([0b00111111, 0b11110000, 0b00000000, 0b00000000,
                 0b00000000, 0b00000000, 0b00000000, 0b00000000]))],
    ids=['float16', 'float32', 'float64'])
def test_ba_decoder_float(size, data):
    backend = bpack.ba

    @backend.decoder
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
    @dataclasses.dataclass
    class Record:
        field_1: float = bpack.field(size=size)

    record = Record.from_bytes(data)
    assert record.field_1 == 1.


def test_ba_decoder_invalid_float_size():
    backend = bpack.ba

    with pytest.raises(ValueError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
        @dataclasses.dataclass
        class Record:
            field_1: float = bpack.field(size=80)


def test_bit_decoder_little_endian_ba():
    backend = bpack.ba

    with pytest.raises(NotImplementedError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                          byteorder=bpack.EByteOrder.LITTLE)
        @dataclasses.dataclass(frozen=True)
        class Record:
            field_1: int = bpack.field(size=8, default=1)


def test_bit_decoder_lsb_ba():
    backend = bpack.ba

    with pytest.raises(NotImplementedError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                          bitorder=bpack.EBitOrder.LSB)
        @dataclasses.dataclass(frozen=True)
        class Record:
            field_1: int = bpack.field(size=8, default=1)

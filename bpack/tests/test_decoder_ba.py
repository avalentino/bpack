"""Specific tests for the bitarray based decoder."""

from typing import List, Sequence

import pytest

import bpack
bpack_ba = pytest.importorskip('bpack.ba')


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
    class Record:
        field_1: float = bpack.field(size=size)

    record = Record.frombytes(data)
    assert record.field_1 == 1.


def test_invalid_float_size():
    backend = bpack_ba

    with pytest.raises(ValueError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
        class Record:                                                   # noqa
            field_1: float = bpack.field(size=80)


def test_little_endian():
    backend = bpack_ba

    with pytest.raises(NotImplementedError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                          byteorder=bpack.EByteOrder.LE,
                          frozen=True)
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=8, default=1)


def test_invalid_bitorder():
    backend = bpack_ba

    with pytest.raises(NotImplementedError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS,
                          bitorder=bpack.EBitOrder.LSB,
                          frozen=True)
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=8, default=1)


def test_sequence():
    backend = bpack_ba

    with pytest.raises(TypeError):
        @backend.decoder
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
        class Record:                                                   # noqa
            field_1: List[int] = bpack.field(size=4, signed=False,
                                             repeat=2, default=3)
            field_2: Sequence[int] = bpack.field(size=4, signed=False,
                                                 repeat=2, default=4)

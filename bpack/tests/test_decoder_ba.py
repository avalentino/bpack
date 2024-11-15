"""Specific tests for the bitarray based decoder."""

from collections.abc import Sequence

import pytest

import bpack

bpack_ba = pytest.importorskip("bpack.ba")


@pytest.mark.parametrize(
    "size, data",
    [
        # fmt: off
        (16, bytes([0b00111100, 0b00000000])),
        (32, bytes([0b00111111, 0b10000000, 0b00000000, 0b00000000])),
        (64, bytes([0b00111111, 0b11110000, 0b00000000, 0b00000000,
                    0b00000000, 0b00000000, 0b00000000, 0b00000000])),
        # fmt: on
    ],
    ids=["float16", "float32", "float64"],
)
def test_float(size, data):
    backend = bpack_ba
    codec = getattr(backend, "codec", backend.decoder)

    @codec
    @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
    class Record:
        field_1: float = bpack.field(size=size)

    record = Record.frombytes(data)
    assert record.field_1 == 1.0


def test_invalid_float_size():
    backend = bpack_ba
    codec = getattr(backend, "codec", backend.decoder)

    with pytest.raises(ValueError):

        @codec
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
        class Record:
            field_1: float = bpack.field(size=80)


def test_little_endian():
    backend = bpack_ba
    codec = getattr(backend, "codec", backend.decoder)

    with pytest.raises(NotImplementedError):

        @codec
        @bpack.descriptor(
            baseunits=bpack.EBaseUnits.BITS,
            byteorder=bpack.EByteOrder.LE,
            frozen=True,
        )
        class Record:
            field_1: int = bpack.field(size=8, default=1)


def test_invalid_bitorder():
    backend = bpack_ba
    codec = getattr(backend, "codec", backend.decoder)

    with pytest.raises(NotImplementedError):

        @codec
        @bpack.descriptor(
            baseunits=bpack.EBaseUnits.BITS,
            bitorder=bpack.EBitOrder.LSB,
            frozen=True,
        )
        class Record:
            field_1: int = bpack.field(size=8, default=1)


def test_sequence():
    backend = bpack_ba
    codec = getattr(backend, "codec", backend.decoder)

    with pytest.raises(TypeError):

        @codec
        @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
        class Record:
            field_1: list[int] = bpack.field(
                size=4, signed=False, repeat=2, default=3
            )
            field_2: Sequence[int] = bpack.field(
                size=4, signed=False, repeat=2, default=4
            )

"""Specific tests for the bitarray based decoder."""

from typing import List, Sequence
import pytest
import bpack


bpack_np = pytest.importorskip('bpack.np')


def test_sequence():
    backend = bpack_np
    bitorder = None
    size = 1
    repeat = 2
    encoded_data = bytes([3, 3, 4, 4])

    @backend.decoder
    @bpack.descriptor(baseunits=backend.Decoder.baseunits, bitorder=bitorder)
    class Record:
        field_1: List[int] = bpack.field(size=size, repeat=repeat)
        field_2: Sequence[int] = bpack.field(size=size, repeat=repeat)

    ref_record = Record([3, 3], (4, 4))
    record = Record.frombytes(encoded_data)
    assert list(record.field_1) == list(ref_record.field_1)
    assert list(record.field_2) == list(ref_record.field_2)

    for field, sequence_type in zip(bpack.fields(Record),
                                    (List[int], Sequence[int])):
        assert field.type == sequence_type

"""Tests bpack with "from __future__ import annotations"."""

from __future__ import annotations

import enum

import pytest

import bpack
from bpack import T


class EEnumType(enum.IntEnum):
    A = 1
    B = 2
    C = 3


@bpack.descriptor
class Record:
    field_1: int = bpack.field(size=4, default=11)
    field_2: float = bpack.field(size=4, default=22.22)
    field_3: EEnumType = bpack.field(size=1, default=EEnumType.A)


@bpack.descriptor
class NestedRecord:
    field_1: str = bpack.field(size=10, default="0123456789")
    field_2: Record = bpack.field(
        size=bpack.calcsize(Record), default_factory=Record
    )
    field_3: int = bpack.field(size=4, default=3)
    field_4: T["f8"] = 0.1  # noqa: F821


def test_nested_records():
    record = Record()
    nested_record = NestedRecord()

    assert nested_record.field_1 == "0123456789"
    assert nested_record.field_2 == record
    assert nested_record.field_2.field_1 == record.field_1
    assert nested_record.field_2.field_2 == record.field_2
    assert nested_record.field_2.field_3 is EEnumType.A
    assert nested_record.field_3 == 3
    assert nested_record.field_4 == 0.1


def test_nested_records_consistency_error():
    with pytest.raises(bpack.descriptors.DescriptorConsistencyError):

        @bpack.descriptor
        class NestedRecord:
            field_1: str = bpack.field(size=10, default="0123456789")
            field_2: Record = bpack.field(
                size=bpack.calcsize(Record) + 1, default_factory=Record
            )
            field_3: int = bpack.field(size=4, default=3)


def test_nested_records_autosize():
    assert bpack.calcsize(NestedRecord) == 31


def test_unexisting_field_type():
    with pytest.raises((TypeError, NameError)):

        @bpack.descriptor
        class Record:
            field_1: "unexisting" = bpack.field(size=4)  # noqa: F821


invalid = True


def test_invalid_field_type():
    with pytest.raises((TypeError, NameError)):

        @bpack.descriptor
        class Record:
            field_1: "invalid" = bpack.field(size=4)  # noqa: F821

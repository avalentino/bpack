"""Test bpack (record) descriptors."""

import dataclasses
from typing import List, Sequence, Tuple

import pytest

import bpack
import bpack.descriptors
from bpack import EBaseUnits, EByteOrder, EBitOrder
from bpack.descriptors import Field as BPackField


def test_base():
    @bpack.descriptor
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert dataclasses.is_dataclass(Record)
    assert len(bpack.fields(Record)) == 2
    assert bpack.baseunits(Record) is EBaseUnits.BYTES  # default
    assert all(isinstance(f, BPackField) for f in bpack.fields(Record))


def test_frozen():
    @bpack.descriptor(frozen=True)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert dataclasses.is_dataclass(Record)
    assert len(bpack.fields(Record)) == 2
    assert bpack.baseunits(Record) is EBaseUnits.BYTES  # default
    assert all(isinstance(f, BPackField) for f in bpack.fields(Record))


def test_dataclass():
    with pytest.warns(DeprecationWarning):
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=8, default=0)
            field_2: float = bpack.field(size=8, default=1/3)


@pytest.mark.parametrize(argnames='baseunits',
                         argvalues=[EBaseUnits.BYTES, EBaseUnits.BITS,
                                    'bits', 'bytes'])
def test_base_units(baseunits):
    @bpack.descriptor(baseunits=baseunits)
    class Record:
        field_1: int = bpack.field(size=8, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert bpack.baseunits(Record) is EBaseUnits(baseunits)
    assert bpack.baseunits(Record()) is EBaseUnits(baseunits)


def test_byte_alignment_warning():
    with pytest.warns(UserWarning,
                      match='bit struct not aligned to bytes'):
        @bpack.descriptor(baseunits=EBaseUnits.BITS)
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)


def test_attrs():
    @bpack.descriptor
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert hasattr(Record, bpack.descriptors.BASEUNITS_ATTR_NAME)
    assert hasattr(Record, bpack.descriptors.BYTEORDER_ATTR_NAME)
    assert hasattr(Record, bpack.descriptors.BITORDER_ATTR_NAME)
    assert hasattr(Record, bpack.descriptors.SIZE_ATTR_NAME)


@pytest.mark.parametrize(argnames='baseunits', argvalues=[None, 8, 'x'])
def test_invalid_baseunits(baseunits):
    with pytest.raises(ValueError):
        @bpack.descriptor(baseunits=baseunits)
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)


@pytest.mark.parametrize(argnames='order',
                         argvalues=[EByteOrder.LE, EByteOrder.BE,
                                    EByteOrder.NATIVE, EByteOrder.DEFAULT,
                                    '<', '>', '=', ''])
def test_byteorder(order):
    @bpack.descriptor(byteorder=order)
    class Record:
        field_1: int = bpack.field(size=8, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    if isinstance(order, str):
        assert bpack.byteorder(Record) is EByteOrder(order)
        assert bpack.byteorder(Record()) is EByteOrder(order)
    else:
        assert bpack.byteorder(Record) is order
        assert bpack.byteorder(Record()) is order


@pytest.mark.parametrize(argnames='order', argvalues=['invalid', None])
def test_invalid_byteorder(order):
    with pytest.raises(ValueError):
        @bpack.descriptor(byteorder=order)
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=8, default=0)


@pytest.mark.parametrize(argnames='order',
                         argvalues=[EBitOrder.LSB, EBitOrder.MSB,
                                    EBitOrder.DEFAULT, '<', '>', ''])
def test_bitorder(order):
    @bpack.descriptor(bitorder=order, baseunits=EBaseUnits.BITS)
    class Record:
        field_1: int = bpack.field(size=8, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    if isinstance(order, str):
        assert bpack.bitorder(Record) is EBitOrder(order)
        assert bpack.bitorder(Record()) is EBitOrder(order)
    else:
        assert bpack.bitorder(Record) is order
        assert bpack.bitorder(Record()) is order


def test_default_bitorder():
    @bpack.descriptor(baseunits=EBaseUnits.BITS)
    class Record:
        field_1: int = bpack.field(size=8, default=0)
        field_2: float = bpack.field(size=8, default=1 / 3)

    assert bpack.bitorder(Record) is EBitOrder.DEFAULT
    assert bpack.bitorder(Record()) is EBitOrder.DEFAULT


def test_invalid_bitorder():
    with pytest.raises(ValueError):
        @bpack.descriptor(byteorder='invalid', baseunits=EBaseUnits.BITS)
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=8, default=0)


def test_bitorder_in_byte_descriptors():
    @bpack.descriptor(baseunits=EBaseUnits.BYTES)
    class Record:
        field_1: int = bpack.field(size=8, default=0)

    assert bpack.byteorder(Record) is EByteOrder.DEFAULT
    assert bpack.byteorder(Record()) is EByteOrder.DEFAULT

    with pytest.raises(ValueError):
        @bpack.descriptor(bitorder=EBitOrder.DEFAULT,
                          baseunits=EBaseUnits.BYTES)
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=8, default=0)


def test_invalid_field_class():
    with pytest.raises(TypeError, match='size not specified'):
        @bpack.descriptor
        class Record:                                                   # noqa
            field_1: int = 0
            field_2: float = 1/3


def test_no_field_type():
    with pytest.raises(TypeError):
        @bpack.descriptor
        class Record:                                                   # noqa
            field_1 = bpack.field(size=4, default=0)


def test_invalid_field_size_type():
    with pytest.raises(TypeError):
        @bpack.descriptor
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=None, default=1/3)


def test_inconsistent_field_offset_and_size():
    with pytest.raises(ValueError):
        @bpack.descriptor
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, offset=1, default=1/3)


def test_inconsistent_field_type_and_signed():
    with pytest.warns(UserWarning, match='ignore'):
        @bpack.descriptor
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3, signed=True)


def test_repeat():
    @bpack.descriptor
    class Record:
        field_1: List[int] = bpack.field(size=4, default=0, repeat=2)
        field_2: float = bpack.field(size=8, default=1/3)

    assert bpack.calcsize(Record()) == 16


def test_no_repeat():
    with pytest.raises(TypeError):
        @bpack.descriptor
        class Record:                                                   # noqa
            field_1: List[int] = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1 / 3)


def test_inconsistent_field_type_and_repeat():
    with pytest.raises(TypeError):
        @bpack.descriptor
        class Record:                                                   # noqa
            field_1: int = bpack.field(size=4, default=0, repeat=2)
            field_2: float = bpack.field(size=8, default=1/3, signed=True)


class TestExplicitSize:
    @staticmethod
    def test_explicit_size():
        size = 16

        @bpack.descriptor(size=size)
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.calcsize(Record) == size
        assert bpack.calcsize(Record()) == size

    @staticmethod
    def test_invalid_explicit_size():
        with pytest.raises(ValueError):
            @bpack.descriptor(size=10)
            class Record:                                               # noqa
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3)

    @staticmethod
    def test_inconsistent_explicit_size_and_offset():
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor(size=16)
            class Record:                                               # noqa
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3, offset=12)

    @staticmethod
    def test_inconsistent_explicit_size_and_repeat():
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor(size=12)
            class Record:                                               # noqa
                field_1: List[int] = bpack.field(size=4, default=0, repeat=2)
                field_2: float = bpack.field(size=8, default=1/3)

    @staticmethod
    def test_inconsistent_explicit_size_offset_and_repeat():
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor(size=20)
            class Record:                                               # noqa
                field_1: int = bpack.field(size=4, default=0)
                field_2: List[float] = bpack.field(size=8, default=1/3,
                                                   offset=8, repeat=2)

    @staticmethod
    def test_invalid_explicit_size_type():
        with pytest.raises(TypeError):
            @bpack.descriptor(size=10.5)
            class Record:                                               # noqa
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3)


class TestSize:
    # NOTE: basic tests are in test_descriptor_utils.test_calcsize.
    #       Here corner cases are addressed

    @staticmethod
    def test_len_with_offset_01():
        @bpack.descriptor
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, offset=10, default=1/3)

        assert bpack.calcsize(Record) == 18

    @staticmethod
    def test_len_with_offset_02():
        @bpack.descriptor
        class Record:
            field_1: int = bpack.field(size=4, offset=10, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.calcsize(Record) == 22

    @staticmethod
    def test_len_with_offset_03():
        @bpack.descriptor
        class Record:
            field_1: int = bpack.field(size=4, offset=10, default=0)
            field_2: float = bpack.field(size=8, offset=20, default=1/3)

        assert bpack.calcsize(Record) == 28

    @staticmethod
    def test_len_with_offset_04():
        size = 30

        @bpack.descriptor(size=size)
        class Record:
            field_1: int = bpack.field(size=4, offset=10, default=0)
            field_2: float = bpack.field(size=8, offset=20, default=1/3)

        assert bpack.calcsize(Record) == size

    @staticmethod
    def test_len_with_repeat_01():
        @bpack.descriptor
        class Record:
            field_1: List[int] = bpack.field(size=4, default=0, repeat=2)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.calcsize(Record) == 16

    @staticmethod
    def test_len_with_repeat_02():
        @bpack.descriptor
        class Record:
            field_1: List[int] = bpack.field(size=4, default=0, repeat=2)
            field_2: List[float] = bpack.field(size=8, default=1/3, repeat=2)

        assert bpack.calcsize(Record) == 24

    @staticmethod
    def test_len_with_repeat_and_offset_01():
        @bpack.descriptor
        class Record:
            field_1: List[int] = bpack.field(size=4, default=0, repeat=2,
                                             offset=6)
            field_2: List[float] = bpack.field(size=8, default=1/3, repeat=2)

        assert bpack.calcsize(Record) == 30

    @staticmethod
    def test_len_with_repeat_and_offset_02():
        @bpack.descriptor
        class Record:
            field_1: List[int] = bpack.field(size=4, default=0, repeat=2)
            field_2: List[float] = bpack.field(size=8, default=1/3, repeat=2,
                                               offset=14)

        assert bpack.calcsize(Record) == 30

    @staticmethod
    def test_len_with_repeat_and_offset_03():
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor
            class Record:                                               # noqa
                field_1: List[int] = bpack.field(size=4, default=0, repeat=2)
                field_2: List[float] = bpack.field(size=8, default=1/3,
                                                   repeat=2, offset=6)


def test_sequence_type():
    @bpack.descriptor
    class Record:
        field_1: List[int] = bpack.field(size=1, repeat=4)

    field_1 = bpack.fields(Record)[0]
    assert field_1.type is List[int]
    assert bpack.calcsize(Record) == 4

    @bpack.descriptor
    class Record:
        field_1: Sequence[int] = bpack.field(size=1, repeat=4)

    field_1 = bpack.fields(Record)[0]
    assert field_1.type is Sequence[int]

    with pytest.raises(TypeError):
        @bpack.descriptor
        class Record:                                                   # noqa
            field_1: Tuple[int, int] = bpack.field(size=1, repeat=2)

    with pytest.raises(TypeError):
        @bpack.descriptor
        class Record:                                                   # noqa
            field_1: Sequence = bpack.field(size=1, repeat=2)


def test_field_auto_size():
    @bpack.descriptor
    class Record:
        field_1: bool

    assert bpack.calcsize(Record) == 1

    with pytest.warns(UserWarning):
        @bpack.descriptor(baseunits=EBaseUnits.BITS)
        class Record:
            field_1: bool

    assert bpack.calcsize(Record) == 1


def test_nested_records():
    @bpack.descriptor
    class Record:
        field_1: int = bpack.field(size=4, default=11)
        field_2: float = bpack.field(size=4, default=22.22)

    @bpack.descriptor
    class NestedRecord:
        field_1: str = bpack.field(size=10, default='0123456789')
        field_2: Record = bpack.field(size=bpack.calcsize(Record),
                                      default=Record())
        field_3: int = bpack.field(size=4, default=3)

    record = Record()
    nested_record = NestedRecord()

    assert nested_record.field_1 == '0123456789'
    assert nested_record.field_2 == record
    assert nested_record.field_2.field_1 == record.field_1
    assert nested_record.field_2.field_2 == record.field_2
    assert nested_record.field_3 == 3

    with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
        @bpack.descriptor
        class NestedRecord:                                             # noqa
            field_1: str = bpack.field(size=10, default='0123456789')
            field_2: Record = bpack.field(size=bpack.calcsize(Record) + 1,
                                          default=Record())
            field_3: int = bpack.field(size=4, default=3)


@pytest.mark.parametrize('baseunits',
                         [EBaseUnits.BYTES, EBaseUnits.BITS])
def test_nested_records_autosize(baseunits):
    @bpack.descriptor(baseunits=baseunits)
    class Record:
        field_1: int = bpack.field(size=4, default=1)
        field_2: int = bpack.field(size=4, default=2)

    @bpack.descriptor(baseunits=baseunits)
    class NestedRecord:
        field_1: int = bpack.field(size=4, default=1)
        field_2: Record = Record()  # auto-size (bytes)
        field_3: int = bpack.field(size=4, default=4)

    nested_record_size = bpack.calcsize(NestedRecord, baseunits)
    record_size = bpack.calcsize(Record, baseunits)
    assert nested_record_size == 8 + record_size

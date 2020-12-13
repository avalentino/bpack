"""Test bpack (record) descriptors."""

import dataclasses

import pytest

import bpack
import bpack.descriptors
from bpack import EBaseUnits, EByteOrder, EBitOrder
from bpack.descriptors import Field as BPackField


class TestRecord:
    @staticmethod
    def test_base():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert dataclasses.is_dataclass(Record)
        assert len(bpack.fields(Record)) == 2
        assert bpack.baseunits(Record) is EBaseUnits.BYTES  # default
        assert all(isinstance(f, BPackField) for f in bpack.fields(Record))

    @staticmethod
    def test_frozen():
        @bpack.descriptor
        @dataclasses.dataclass(frozen=True)
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert dataclasses.is_dataclass(Record)
        assert len(bpack.fields(Record)) == 2
        assert bpack.baseunits(Record) is EBaseUnits.BYTES  # default
        assert all(isinstance(f, BPackField) for f in bpack.fields(Record))

    @staticmethod
    def test_no_dataclass():
        error_msg = 'must be called with a dataclass type or instance'
        with pytest.raises(TypeError, match=error_msg):
            @bpack.descriptor
            class Record:
                field_1: int = bpack.field(size=8, default=0)
                field_2: float = bpack.field(size=8, default=1/3)

    @staticmethod
    @pytest.mark.parametrize(argnames='baseunits',
                             argvalues=[EBaseUnits.BYTES, EBaseUnits.BITS,
                                        'bits', 'bytes'])
    def test_base_units(baseunits):
        @bpack.descriptor(baseunits=baseunits)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=8, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.baseunits(Record) is EBaseUnits(baseunits)
        assert bpack.baseunits(Record()) is EBaseUnits(baseunits)

    @staticmethod
    def test_byte_alignment_warning():
        with pytest.warns(UserWarning,
                          match='bit struct not aligned to bytes'):
            @bpack.descriptor(baseunits=EBaseUnits.BITS)
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3)

    @staticmethod
    def test_baseunits_attrs():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert hasattr(Record, bpack.descriptors.BASEUNITS_ATTR_NAME)
        assert hasattr(Record, bpack.descriptors.BYTEORDER_ATTR_NAME)
        assert hasattr(Record, bpack.descriptors.BITORDER_ATTR_NAME)

    @staticmethod
    @pytest.mark.parametrize(argnames='baseunits', argvalues=[None, 8, 'x'])
    def test_invalid_baseunits(baseunits):
        with pytest.raises(ValueError):
            @bpack.descriptor(baseunits=baseunits)
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3)

    @staticmethod
    @pytest.mark.parametrize(argnames='order',
                             argvalues=[EByteOrder.LITTLE, EByteOrder.BIG,
                                        EByteOrder.NATIVE, EByteOrder.DEFAULT,
                                        '<', '>', '=', ''])
    def test_byteorder(order):
        @bpack.descriptor(byteorder=order)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=8, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        if isinstance(order, str):
            assert bpack.byteorder(Record) is EByteOrder(order)
            assert bpack.byteorder(Record()) is EByteOrder(order)
        else:
            assert bpack.byteorder(Record) is order
            assert bpack.byteorder(Record()) is order

    @staticmethod
    @pytest.mark.parametrize(argnames='order', argvalues=['invalid', None])
    def test_invalid_byteorder(order):
        with pytest.raises(ValueError):
            @bpack.descriptor(byteorder=order)
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=8, default=0)

    @staticmethod
    @pytest.mark.parametrize(argnames='order',
                             argvalues=[EBitOrder.LSB, EBitOrder.MSB,
                                        EBitOrder.DEFAULT, '<', '>', ''])
    def test_bitorder(order):
        @bpack.descriptor(bitorder=order, baseunits=EBaseUnits.BITS)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=8, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        if isinstance(order, str):
            assert bpack.bitorder(Record) is EBitOrder(order)
            assert bpack.bitorder(Record()) is EBitOrder(order)
        else:
            assert bpack.bitorder(Record) is order
            assert bpack.bitorder(Record()) is order

    @staticmethod
    def test_default_bitorder():
        @bpack.descriptor(baseunits=EBaseUnits.BITS)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=8, default=0)
            field_2: float = bpack.field(size=8, default=1 / 3)

        assert bpack.bitorder(Record) is EBitOrder.DEFAULT
        assert bpack.bitorder(Record()) is EBitOrder.DEFAULT

    @staticmethod
    def test_invalid_bitorder():
        with pytest.raises(ValueError):
            @bpack.descriptor(byteorder='invalid', baseunits=EBaseUnits.BITS)
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=8, default=0)

    @staticmethod
    def test_bitorder_in_byte_descriptors():
        @bpack.descriptor(baseunits=EBaseUnits.BYTES)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=8, default=0)

        assert bpack.byteorder(Record) is EByteOrder.DEFAULT
        assert bpack.byteorder(Record()) is EByteOrder.DEFAULT

        with pytest.raises(ValueError):
            @bpack.descriptor(bitorder=EBitOrder.DEFAULT,
                              baseunits=EBaseUnits.BYTES)
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=8, default=0)

    @staticmethod
    def test_invalid_field_class():
        with pytest.raises(TypeError, match='size not specified'):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = 0
                field_2: float = 1/3

    @staticmethod
    def test_no_field_type():
        with pytest.raises(TypeError):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1 = bpack.field(size=4, default=0)

    @staticmethod
    def test_invalid_field_size_type():
        with pytest.raises(TypeError):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=None, default=1/3)

    @staticmethod
    def test_inconsistent_field_offset_and_size():
        with pytest.raises(ValueError):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, offset=1, default=1/3)

    @staticmethod
    def test_inconsistent_field_type_and_signed():
        with pytest.warns(UserWarning, match='ignore'):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3, signed=True)

    @staticmethod
    def test_explicit_size():
        size = 16

        @bpack.descriptor(size=size)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.calcsize(Record) == size
        assert bpack.calcsize(Record()) == size
        assert len(Record()) == size

    @staticmethod
    def test_invalid_explicit_size():
        with pytest.raises(ValueError):
            @bpack.descriptor(size=10)
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3)

    @staticmethod
    def test_inconsistent_explicit_size_and_offset():
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor(size=16)
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3, offset=12)

    @staticmethod
    def test_invalid_explicit_size_type():
        with pytest.raises(TypeError):
            @bpack.descriptor(size=10.5)
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3)

    @staticmethod
    def test_len():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert len(Record()) == 12

    @staticmethod
    def test_len_with_offset_01():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, offset=10, default=1/3)

        assert len(Record()) == 18

    @staticmethod
    def test_len_with_offset_02():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=10, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert len(Record()) == 22

    @staticmethod
    def test_len_with_offset_03():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=10, default=0)
            field_2: float = bpack.field(size=8, offset=20, default=1/3)

        assert len(Record()) == 28

    @staticmethod
    def test_len_with_offset_04():
        size = 30

        @bpack.descriptor(size=size)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=10, default=0)
            field_2: float = bpack.field(size=8, offset=20, default=1/3)

        assert len(Record()) == 30
"""Test bpack descriptors."""

import dataclasses

import pytest

import bpack
from bpack import EBaseUnits
from bpack.descriptors import get_field_descriptor
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
        assert bpack.get_baseunits(Record) is EBaseUnits.BYTES  # default
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
        assert bpack.get_baseunits(Record) is EBaseUnits.BYTES  # default
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

        assert bpack.get_baseunits(Record) is EBaseUnits(baseunits)

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
    @pytest.mark.parametrize(argnames='baseunits', argvalues=[None, 8, 'x'])
    def test_invalid_baseunits(baseunits):
        with pytest.raises(ValueError):
            @bpack.descriptor(baseunits=baseunits)
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3)

    @staticmethod
    def test_invalid_field_class():
        with pytest.raises(TypeError, match='size not specified'):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = 0
                field_2: float = 1/3

    @staticmethod
    def test_missing_field_size():
        with pytest.raises(TypeError):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(default=1/3)

    @staticmethod
    @pytest.mark.parametrize(argnames='size', argvalues=[None, 1.3, 'x'])
    def test_invalid_field_size_type(size):
        with pytest.raises(TypeError):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=size, default=1./3)

    @staticmethod
    @pytest.mark.parametrize(argnames='size', argvalues=[0, -8])
    def test_invalid_field_size(size):
        with pytest.raises(ValueError):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=size, default=1/3)

    @staticmethod
    @pytest.mark.parametrize(argnames='offset', argvalues=[1.3, 'x'])
    def test_invalid_field_offset_type(offset):
        with pytest.raises(TypeError):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3,
                                             offset=offset)

    @staticmethod
    @pytest.mark.parametrize(argnames='offset', argvalues=[0, -8])
    def test_invalid_field_offset(offset):
        with pytest.raises(ValueError):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, default=1/3,
                                             offset=offset)

    @staticmethod
    def test_invalid_inconsistent_field_offset_and_size():
        with pytest.raises(ValueError):
            @bpack.descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = bpack.field(size=4, default=0)
                field_2: float = bpack.field(size=8, offset=1, default=1/3)

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
        assert Record.__len__() == 12

    @staticmethod
    def test_len_with_offset_01():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, offset=10, default=1/3)

        assert len(Record()) == 18
        assert Record.__len__() == 18

    @staticmethod
    def test_len_with_offset_02():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=10, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert len(Record()) == 22
        assert Record.__len__() == 22

    @staticmethod
    def test_len_with_offset_03():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=10, default=0)
            field_2: float = bpack.field(size=8, offset=20, default=1/3)

        assert len(Record()) == 28
        assert Record.__len__() == 28

    @staticmethod
    def test_len_with_offset_04():
        size = 30

        @bpack.descriptor(size=size)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=10, default=0)
            field_2: float = bpack.field(size=8, offset=20, default=1/3)

        assert len(Record()) == 30
        assert Record.__len__() == 30


class TestFields:
    @staticmethod
    def test_field_size_01():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        # name, type, size, offset
        field_data = [('field_1', int, 4, 0), ('field_2', float, 8, 4)]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.size == size
            assert field_descr.offset == offset

    @staticmethod
    def test_field_size_02():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=1, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        # name, type, size, offset
        field_data = [('field_1', int, 4, 1), ('field_2', float, 8, 5)]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.size == size
            assert field_descr.offset == offset

    @staticmethod
    def test_field_size_03():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=1, default=0)
            field_2: float = bpack.field(size=8, offset=6, default=1/3)

        # name, type, size, offset
        field_data = [('field_1', int, 4, 1), ('field_2', float, 8, 6)]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.size == size
            assert field_descr.offset == offset


class TestUtils:
    @staticmethod
    def test_is_record():
        assert not bpack.is_descriptor(1)
        assert not bpack.is_descriptor('x')

        class C:
            pass

        assert not bpack.is_descriptor(C)
        assert not bpack.is_descriptor(C())

        @dataclasses.dataclass
        class D:
            field_1: int = 0

        assert not bpack.is_descriptor(D)
        assert not bpack.is_descriptor(D())

        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.is_descriptor(Record)
        assert bpack.is_descriptor(Record())

    @staticmethod
    def test_is_field():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        for field_ in bpack.fields(Record):
            assert bpack.is_field(field_)

        for field_ in bpack.fields(Record()):
            assert bpack.is_field(field_)

    @staticmethod
    def test_calcsize():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1./3)

        assert bpack.calcsize(Record) == 12
        assert bpack.calcsize(Record()) == 12

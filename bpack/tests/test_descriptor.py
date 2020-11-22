# -*- coding: utf-8 -*-

import dataclasses

import pytest

from bpack.descriptor import (
    Field, descriptor, EBaseUnits, is_descriptor, calcsize, is_field,
)


class TestRecord:
    @staticmethod
    def test_base():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, default=0)
            field_2: float = Field(size=8, default=1./3)

        assert dataclasses.is_dataclass(Record)
        assert len(dataclasses.fields(Record)) == 2
        assert Record._BASEUNITS is EBaseUnits.BYTES  # default
        assert all(isinstance(f, Field) for f in dataclasses.fields(Record))

    @staticmethod
    def test_frozen():
        @descriptor
        @dataclasses.dataclass(frozen=True)
        class Record:
            field_1: int = Field(size=4, default=0)
            field_2: float = Field(size=8, default=1./3)

        assert dataclasses.is_dataclass(Record)
        assert len(dataclasses.fields(Record)) == 2
        assert Record._BASEUNITS is EBaseUnits.BYTES  # default
        assert all(isinstance(f, Field) for f in dataclasses.fields(Record))

    @staticmethod
    @pytest.mark.parametrize(argnames='baseunits',
                             argvalues=[EBaseUnits.BYTES, EBaseUnits.BITS,
                                        'bits', 'bytes'])
    def test_baseunits(baseunits):
        @descriptor(baseunits=baseunits)
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=8, default=0)
            field_2: float = Field(size=8, default=1./3)

        assert Record._BASEUNITS is EBaseUnits(baseunits)

    @staticmethod
    def test_byte_alignment_warning():
        with pytest.warns(UserWarning, match='bit struct not aligned to bytes'):
            @descriptor(baseunits=EBaseUnits.BITS)
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(size=8, default=1./3)

    @staticmethod
    @pytest.mark.parametrize(argnames='baseunits', argvalues=[None, 8, 'x'])
    def test_invalid_baseunits(baseunits):
        with pytest.raises(ValueError):
            @descriptor(baseunits=baseunits)
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(size=8, default=1./3)

    @staticmethod
    def test_missing_field_size():
        with pytest.raises(TypeError):
            @descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(default=1./3)

    @staticmethod
    @pytest.mark.parametrize(argnames='size', argvalues=[None, 1.3, 'x'])
    def test_invalid_field_size_type(size):
        with pytest.raises(TypeError):
            @descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(size=size, default=1./3)

    @staticmethod
    @pytest.mark.parametrize(argnames='size', argvalues=[0, -8])
    def test_invalid_field_size(size):
        with pytest.raises(ValueError):
            @descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(size=size, default=1./3)

    @staticmethod
    @pytest.mark.parametrize(argnames='offset', argvalues=[1.3, 'x'])
    def test_invalid_field_offset_type(offset):
        with pytest.raises(TypeError):
            @descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(size=8, offset=offset, default=1./3)

    @staticmethod
    @pytest.mark.parametrize(argnames='offset', argvalues=[0, -8])
    def test_invalid_field_offset(offset):
        with pytest.raises(ValueError):
            @descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(size=8, offset=offset, default=1./3)

    @staticmethod
    def test_invalid_inconsistent_field_offset_and_size():
        with pytest.raises(ValueError):
            @descriptor
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(size=8, offset=1, default=1./3)

    @staticmethod
    def test_explicit_size():
        size = 16
        @descriptor(size=size)
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, default=0)
            field_2: float = Field(size=8, default=1./3)

        assert calcsize(Record) == size
        assert calcsize(Record()) == size
        assert len(Record()) == size

    @staticmethod
    def test_invalid_explicit_size():
        with pytest.raises(ValueError):
            @descriptor(size=10)
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(size=8, default=1./3)

    @staticmethod
    def test_invalid_explicit_size_type():
        with pytest.raises(TypeError):
            @descriptor(size=10.5)
            @dataclasses.dataclass
            class Record:
                field_1: int = Field(size=4, default=0)
                field_2: float = Field(size=8, default=1./3)

    @staticmethod
    def test_len():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, default=0)
            field_2: float = Field(size=8, default=1./3)

        assert len(Record()) == 12
        assert Record.__len__() == 12

    @staticmethod
    def test_len_with_offset_01():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, default=0)
            field_2: float = Field(size=8, offset=10, default=1./3)

        assert len(Record()) == 18
        assert Record.__len__() == 18

    @staticmethod
    def test_len_with_offset_02():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, offset=10, default=0)
            field_2: float = Field(size=8, default=1./3)

        assert len(Record()) == 22
        assert Record.__len__() == 22

    @staticmethod
    def test_len_with_offset_03():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, offset=10, default=0)
            field_2: float = Field(size=8, offset=20, default=1./3)

        assert len(Record()) == 28
        assert Record.__len__() == 28


    @staticmethod
    def test_len_with_offset_04():
        size = 30
        @descriptor(size=size)
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, offset=10, default=0)
            field_2: float = Field(size=8, offset=20, default=1./3)

        assert len(Record()) == 30
        assert Record.__len__() == 30


class TestFields:
    @staticmethod
    def test_field_size_01():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, default=0)
            field_2: float = Field(size=8, default=1./3)

        # name, type, size, offset
        field_data = [('field_1', int, 4, 0), ('field_2', float, 8, 4)]

        for field, data in zip(dataclasses.fields(Record), field_data):
            name, type, size, offset = data
            assert field.name == name
            assert field.type == type
            assert field.size == size
            assert field.offset == offset

    @staticmethod
    def test_field_size_02():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, offset=1, default=0)
            field_2: float = Field(size=8, default=1./3)

        # name, type, size, offset
        field_data = [('field_1', int, 4, 1), ('field_2', float, 8, 5)]

        for field, data in zip(dataclasses.fields(Record), field_data):
            name, type, size, offset = data
            assert field.name == name
            assert field.type == type
            assert field.size == size
            assert field.offset == offset

    @staticmethod
    def test_field_size_03():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, offset=1, default=0)
            field_2: float = Field(size=8, offset=6, default=1./3)

        # name, type, size, offset
        field_data = [('field_1', int, 4, 1), ('field_2', float, 8, 6)]

        for field, data in zip(dataclasses.fields(Record), field_data):
            name, type, size, offset = data
            assert field.name == name
            assert field.type == type
            assert field.size == size
            assert field.offset == offset


class TestUtils:
    @staticmethod
    def test_is_record():
        assert not is_descriptor(1)
        assert not is_descriptor('x')

        class C:
            pass

        assert not is_descriptor(C)
        assert not is_descriptor(C())

        @dataclasses.dataclass
        class D:
            field_1: int = 0

        assert not is_descriptor(D)
        assert not is_descriptor(D())

        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, default=0)
            field_2: float = Field(size=8, default=1./3)

        assert is_descriptor(Record)
        assert is_descriptor(Record())

    @staticmethod
    def test_is_field():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, default=0)
            field_2: float = Field(size=8, default=1./3)

        for field in dataclasses.fields(Record):
            assert is_field(field)

        for field in dataclasses.fields(Record()):
            assert is_field(field)

    @staticmethod
    def test_calcsize():
        @descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = Field(size=4, default=0)
            field_2: float = Field(size=8, default=1./3)

        assert calcsize(Record) == 12
        assert calcsize(Record()) == 12

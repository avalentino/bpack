"""Test bpack field descriptors."""

import dataclasses

import pytest

import bpack
from bpack.descriptors import get_field_descriptor


class TestFieldFactory:
    @staticmethod
    def test_base():
        bpack.field(size=1, offset=0, signed=False, default=0)

    @staticmethod
    def test_field():
        with pytest.raises(TypeError):
            bpack.field()

    @staticmethod
    def test_field_vs_field_class():
        field_ = bpack.field(size=1)
        assert bpack.descriptors.is_field(field_)
        assert isinstance(field_, bpack.descriptors.Field)

    @staticmethod
    def test_missing_size():
        with pytest.raises(TypeError):
            bpack.field(default=1/3)

    @staticmethod
    @pytest.mark.parametrize(argnames='size', argvalues=[1.3, 'x'])
    def test_invalid_size_type(size):
        with pytest.raises(TypeError):
            bpack.field(size=size, default=1/3)

    @staticmethod
    @pytest.mark.parametrize(argnames='size', argvalues=[0, -8])
    def test_invalid_size(size):
        with pytest.raises(ValueError):
            bpack.field(size=size, default=1/3)

    @staticmethod
    @pytest.mark.parametrize(argnames='offset', argvalues=[1.3, 'x'])
    def test_invalid_offset_type(offset):
        with pytest.raises(TypeError):
            bpack.field(size=8, default=1/3, offset=offset)

    @staticmethod
    def test_invalid_offset():
        with pytest.raises(ValueError):
            bpack.field(size=8, default=1/3, offset=-8)

    @staticmethod
    @pytest.mark.parametrize('value', [-8, 'a'])
    def test_invalid_signed_type(value):
        with pytest.raises(TypeError):
            bpack.field(size=8, default=1, signed=value)

    @staticmethod
    def test_metadata_key():
        field_ = bpack.field(size=1)
        assert bpack.descriptors.METADATA_KEY in field_.metadata


class TestFields:
    @staticmethod
    def test_field_size_01():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0, signed=True)
            field_2: float = bpack.field(size=8, default=1/3)

        # name, type, size, offset
        field_data = [
            ('field_1', int, 4, 0, True),
            ('field_2', float, 8, 4, None),
        ]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset, signed = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.type == type_
            assert field_descr.size == size
            assert field_descr.offset == offset
            assert field_descr.signed == signed

    @staticmethod
    def test_field_size_02():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=1, default=0,
                                       signed=False)
            field_2: float = bpack.field(size=8, default=1/3)

        # name, type, size, offset
        field_data = [
            ('field_1', int, 4, 1, False),
            ('field_2', float, 8, 5, None),
        ]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset, signed = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.type == type_
            assert field_descr.size == size
            assert field_descr.offset == offset
            assert field_descr.signed == signed

    @staticmethod
    def test_field_size_03():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, offset=1, default=0)
            field_2: float = bpack.field(size=8, offset=6, default=1/3)

        # name, type, size, offset
        field_data = [
            ('field_1', int, 4, 1, None),
            ('field_2', float, 8, 6, None),
        ]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset, signed = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.type == type_
            assert field_descr.size == size
            assert field_descr.offset == offset
            assert field_descr.signed == signed


class TestFieldDescriptor:
    @staticmethod
    def test_empty_init():
        descr = bpack.descriptors.BinFieldDescriptor()
        assert descr.type is None
        assert descr.size is None
        assert descr.offset is None
        assert descr.signed is None
        assert len(vars(descr)) == 4

    @staticmethod
    def test_init():
        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2, True)
        assert descr.type is int
        assert descr.size == 1
        assert descr.offset == 2
        assert descr.signed is True
        assert len(vars(descr)) == 4

    @staticmethod
    def test_init_kw():
        descr = bpack.descriptors.BinFieldDescriptor(type=int, size=1,
                                                     offset=2, signed=True)
        assert descr.type is int
        assert descr.size == 1
        assert descr.offset == 2
        assert descr.signed is True
        assert len(vars(descr)) == 4

    @staticmethod
    def test_init_invalid_type():
        with pytest.raises(TypeError):
            bpack.descriptors.BinFieldDescriptor(size=1.1)

        with pytest.raises(TypeError):
            bpack.descriptors.BinFieldDescriptor(offset=2.1)

        with pytest.raises(TypeError):
            bpack.descriptors.BinFieldDescriptor(signed=complex(3.1, 0))

    @staticmethod
    def test_init_invalid_value():
        with pytest.raises(ValueError):
            bpack.descriptors.BinFieldDescriptor(size=-1)

        with pytest.raises(ValueError):
            bpack.descriptors.BinFieldDescriptor(size=0)

        with pytest.raises(ValueError):
            bpack.descriptors.BinFieldDescriptor(offset=-1)

    @staticmethod
    def test_validate():
        descr = bpack.descriptors.BinFieldDescriptor(int, 1)
        descr.validate()

        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2)
        descr.validate()

        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2, True)
        descr.validate()

    @staticmethod
    def test_validation_warning():
        descr = bpack.descriptors.BinFieldDescriptor(type=float, size=4,
                                                     signed=True)
        with pytest.warns(UserWarning, match='ignore'):
            descr.validate()

    @staticmethod
    def test_validation_error():
        descr = bpack.descriptors.BinFieldDescriptor()
        with pytest.raises(TypeError):
            descr.validate()

        descr = bpack.descriptors.BinFieldDescriptor(type=int)
        with pytest.raises(TypeError):
            descr.validate()

        descr = bpack.descriptors.BinFieldDescriptor(size=1)
        with pytest.raises(TypeError):
            descr.validate()

    @staticmethod
    def test_post_validation_error_on_type():
        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2)
        descr.validate()
        descr.type = None
        with pytest.raises(TypeError):
            descr.validate()

    @staticmethod
    @pytest.mark.parametrize('size, error_type',
                             [(None, TypeError),
                              (0, ValueError),
                              (-1, ValueError),
                              (1.1, TypeError)],
                             ids=['None', 'zero', 'negative', 'float'])
    def test_post_validation_error_on_size(size, error_type):
        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2)
        descr.validate()
        descr.size = size
        with pytest.raises(error_type):
            descr.validate()

    @staticmethod
    @pytest.mark.parametrize('offset, error_type',
                             [(-1, ValueError),
                              (1.1, TypeError)],
                             ids=['negative', 'float'])
    def test_post_validation_error_on_offset(offset, error_type):
        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2)
        descr.validate()
        descr.offset = offset
        with pytest.raises(error_type):
            descr.validate()

    @staticmethod
    def test_post_validation_warning_on_signed():
        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2, signed=True)
        descr.validate()
        descr.type = float
        with pytest.warns(UserWarning, match='ignore'):
            descr.validate()
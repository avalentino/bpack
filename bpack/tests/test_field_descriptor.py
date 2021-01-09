"""Test bpack field descriptors."""

import sys
import enum

from typing import List

import pytest

import bpack
from bpack.descriptors import get_field_descriptor


class TestFieldFactory:
    @staticmethod
    def test_base():
        bpack.field(size=1, offset=0, signed=False, default=0, repeat=1)

    @staticmethod
    def test_field_vs_field_class():
        field_ = bpack.field(size=1)
        assert bpack.descriptors.is_field(field_)
        assert isinstance(field_, bpack.descriptors.Field)

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
            bpack.field(size=8, default=1, signed=value)                # noqa

    @staticmethod
    @pytest.mark.parametrize(argnames='repeat', argvalues=[1.3, 'x'])
    def test_invalid_repeat_type(repeat):
        with pytest.raises(TypeError):
            bpack.field(size=8, default=1/3, repeat=repeat)

    @staticmethod
    def test_invalid_repeat():
        with pytest.raises(ValueError):
            bpack.field(size=8, default=1/3, repeat=0)

    @staticmethod
    def test_metadata_key():
        field_ = bpack.field(size=1)
        assert bpack.descriptors.METADATA_KEY in field_.metadata


class TestRecordFields:
    @staticmethod
    def test_field_properties_01():
        @bpack.descriptor
        class Record:
            field_1: int = bpack.field(size=4, default=0, signed=True)
            field_2: float = bpack.field(size=8, default=1/3)
            field_3: List[int] = bpack.field(size=1, default=1, repeat=1)

        # name, type, size, offset, repeat
        field_data = [
            ('field_1', int, 4, 0, True, None),
            ('field_2', float, 8, 4, None, None),
            ('field_3', List[int], 1, 12, None, 1),
        ]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset, signed, repeat = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.type == type_
            assert field_descr.size == size
            assert field_descr.offset == offset
            assert field_descr.signed == signed
            assert field_descr.repeat == repeat

    @staticmethod
    def test_field_properties_02():
        @bpack.descriptor
        class Record:
            field_1: int = bpack.field(size=4, offset=1, default=0,
                                       signed=False)
            field_2: float = bpack.field(size=8, default=1/3)
            field_3: List[int] = bpack.field(size=1, default=1, repeat=1)

        # name, type, size, offset, repeat
        field_data = [
            ('field_1', int, 4, 1, False, None),
            ('field_2', float, 8, 5, None, None),
            ('field_3', List[int], 1, 13, None, 1),
        ]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset, signed, repeat = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.type == type_
            assert field_descr.size == size
            assert field_descr.offset == offset
            assert field_descr.signed == signed
            assert field_descr.repeat == repeat

    @staticmethod
    def test_field_properties_03():
        @bpack.descriptor
        class Record:
            field_1: int = bpack.field(size=4, offset=1, default=0)
            field_2: float = bpack.field(size=8, offset=6, default=1/3)

        # name, type, size, offset, repeat
        field_data = [
            ('field_1', int, 4, 1, None, None),
            ('field_2', float, 8, 6, None, None),
        ]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset, signed, repeat = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.type == type_
            assert field_descr.size == size
            assert field_descr.offset == offset
            assert field_descr.signed == signed
            assert field_descr.repeat == repeat

    @staticmethod
    def test_finvalid_field_type():
        with pytest.raises(TypeError):
            @bpack.descriptor
            class Record:                                       # noqa
                field_1: 'invalid' = bpack.field(size=4)        # noqa: F821


class TestEnumFields:
    @staticmethod
    def test_enum():
        class EEnumType(enum.Enum):
            A = 'a'
            B = 'b'
            C = 'c'

        @bpack.descriptor
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: EEnumType = bpack.field(size=1, default=EEnumType.A)

        field_2 = bpack.fields(Record)[1]
        assert field_2.name == 'field_2'
        assert field_2.type is EEnumType
        assert field_2.default is EEnumType.A
        assert isinstance(Record().field_2, EEnumType)

    @staticmethod
    def test_int_enum():
        class EEnumType(enum.IntEnum):
            A = 1
            B = 2
            C = 4

        @bpack.descriptor
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: EEnumType = bpack.field(size=1, signed=True,
                                             default=EEnumType.A)

        field_2 = bpack.fields(Record)[1]
        assert field_2.name == 'field_2'
        assert field_2.type is EEnumType
        assert field_2.default is EEnumType.A
        assert isinstance(Record().field_2, EEnumType)

    @staticmethod
    def test_intflag_enum():
        class EEnumType(enum.IntFlag):
            A = 1
            B = 2
            C = 4

        @bpack.descriptor
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: EEnumType = bpack.field(size=1, default=EEnumType.A)

        field_2 = bpack.fields(Record)[1]
        assert field_2.name == 'field_2'
        assert field_2.type is EEnumType
        assert field_2.default is EEnumType.A
        assert isinstance(Record().field_2, EEnumType)

    @staticmethod
    def test_invalid_enum():
        class EEnumType(enum.Enum):
            A = 1
            B = 'b'
            C = 4

        with pytest.raises(TypeError):
            @bpack.descriptor
            class Record:                                               # noqa
                field_1: int = bpack.field(size=4, default=0)
                field_2: EEnumType = bpack.field(size=1, default=EEnumType.A)

    @staticmethod
    def test_invalid_signed_qualifier():
        class EEnumType(enum.Enum):
            A = 'a'
            B = 'b'
            C = 'c'

        with pytest.warns(UserWarning):
            @bpack.descriptor
            class Record:                                               # noqa
                field_1: int = bpack.field(size=4, default=0)
                field_2: EEnumType = bpack.field(size=1, signed=True,
                                                 default=EEnumType.A)


class TestFieldDescriptor:
    @staticmethod
    def test_empty_init():
        descr = bpack.descriptors.BinFieldDescriptor()
        assert descr.type is None
        assert descr.size is None
        assert descr.offset is None
        assert descr.signed is None
        assert descr.repeat is None
        assert len(vars(descr)) == 5

    @staticmethod
    def test_init():
        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2, True, 1)
        assert descr.type is int
        assert descr.size == 1
        assert descr.offset == 2
        assert descr.signed is True
        assert descr.repeat == 1
        assert len(vars(descr)) == 5

    @staticmethod
    def test_init_kw():
        descr = bpack.descriptors.BinFieldDescriptor(type=int, size=1,
                                                     offset=2, signed=True,
                                                     repeat=1)
        assert descr.type is int
        assert descr.size == 1
        assert descr.offset == 2
        assert descr.signed is True
        assert descr.repeat == 1
        assert len(vars(descr)) == 5

    @staticmethod
    def test_init_invalid_type():
        with pytest.raises(TypeError):
            bpack.descriptors.BinFieldDescriptor(size=1.1)              # noqa

        with pytest.raises(TypeError):
            bpack.descriptors.BinFieldDescriptor(offset=2.1)            # noqa

        with pytest.raises(TypeError):
            bpack.descriptors.BinFieldDescriptor(
                signed=complex(3.1, 0))                                 # noqa

        with pytest.raises(TypeError):
            bpack.descriptors.BinFieldDescriptor(repeat=1.1)            # noqa

    @staticmethod
    def test_init_invalid_value():
        with pytest.raises(ValueError):
            bpack.descriptors.BinFieldDescriptor(size=-1)

        with pytest.raises(ValueError):
            bpack.descriptors.BinFieldDescriptor(size=0)

        with pytest.raises(ValueError):
            bpack.descriptors.BinFieldDescriptor(offset=-1)

        with pytest.raises(ValueError):
            bpack.descriptors.BinFieldDescriptor(repeat=0)

    @staticmethod
    def test_validate():
        descr = bpack.descriptors.BinFieldDescriptor(int, 1)
        descr.validate()

        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2)
        descr.validate()

        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2, True)
        descr.validate()

        descr = bpack.descriptors.BinFieldDescriptor(List[int], 1, 2, True, 1)
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

        descr = bpack.descriptors.BinFieldDescriptor(type=int, size=1,
                                                     repeat=2)
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

    @staticmethod
    def test_post_validation_error_on_repeat():
        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2, signed=True)
        descr.validate()
        descr.repeat = 2
        with pytest.raises(TypeError):
            descr.validate()

        descr = bpack.descriptors.BinFieldDescriptor(List[int], 1, 2,
                                                     signed=True, repeat=2)
        descr.validate()
        descr.repeat = 0
        with pytest.raises(ValueError):
            descr.validate()

    def test_methods(self):
        descr = bpack.descriptors.BinFieldDescriptor(int, 1)
        descr.validate()
        assert descr.is_int_type()
        assert not descr.is_sequence_type()
        assert not descr.is_enum_type()

        descr = bpack.descriptors.BinFieldDescriptor(float, 1)
        descr.validate()
        assert not descr.is_int_type()
        assert not descr.is_sequence_type()
        assert not descr.is_enum_type()

        descr = bpack.descriptors.BinFieldDescriptor(List[int], 1, repeat=10)
        descr.validate()
        assert descr.is_int_type()
        assert descr.is_sequence_type()
        assert not descr.is_enum_type()

        descr = bpack.descriptors.BinFieldDescriptor(List[float], 1, repeat=10)
        descr.validate()
        assert not descr.is_int_type()
        assert descr.is_sequence_type()
        assert not descr.is_enum_type()

        class EEnumType(enum.Enum):
            A = 'a'

        descr = bpack.descriptors.BinFieldDescriptor(EEnumType, 1)
        descr.validate()
        assert not descr.is_int_type()
        assert not descr.is_sequence_type()
        assert descr.is_enum_type()

        class EEnumType(enum.IntEnum):
            A = 1

        descr = bpack.descriptors.BinFieldDescriptor(EEnumType, 1)
        descr.validate()
        assert descr.is_int_type()
        assert not descr.is_sequence_type()
        assert descr.is_enum_type()

        class EEnumType(enum.IntFlag):
            A = 1

        descr = bpack.descriptors.BinFieldDescriptor(EEnumType, 1)
        descr.validate()
        assert descr.is_int_type()
        assert not descr.is_sequence_type()
        assert descr.is_enum_type()


class TestAnnotatedType:
    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''],
                             ids=['>', '<', '|', 'None'])
    def test_annotated_type(byteorder):
        @bpack.descriptor(byteorder=byteorder if byteorder != '|' else '')
        class Record:
            field_1: bpack.T[f'{byteorder}i4']                  # noqa: F821
            field_2: bpack.T[f'{byteorder}u4']                  # noqa: F821
            field_3: bpack.T[f'{byteorder}f4']                  # noqa: F821
            field_4: bpack.T[f'{byteorder}c4']                  # noqa: F821
            field_5: bpack.T[f'{byteorder}S4']                  # noqa: F821

        fields = dict(
            (field.name, get_field_descriptor(field))
            for field in bpack.fields(Record)
        )

        assert fields['field_1'].type == int
        assert fields['field_1'].size == 4
        assert fields['field_1'].signed is True
        assert fields['field_1'].repeat is None

        assert fields['field_2'].type == int
        assert fields['field_2'].size == 4
        assert fields['field_2'].signed is False
        assert fields['field_2'].repeat is None

        assert fields['field_3'].type == float
        assert fields['field_3'].size == 4
        assert fields['field_3'].signed is None
        assert fields['field_3'].repeat is None

        assert fields['field_4'].type == complex
        assert fields['field_4'].size == 4
        assert fields['field_4'].signed is None
        assert fields['field_4'].repeat is None

        assert fields['field_5'].type == bytes
        assert fields['field_5'].size == 4
        assert fields['field_5'].signed is None
        assert fields['field_5'].repeat is None

    @staticmethod
    def test_list_with_annotated_type():
        typestr = 'i4'

        @bpack.descriptor
        class Record:
            field_1: List[bpack.T[typestr]] = bpack.field(repeat=2)

        field = bpack.fields(Record)[0]
        assert field.type == List[bpack.T[typestr]]

        field_descr = get_field_descriptor(field)
        assert field_descr.type == List[int]
        assert field_descr.size == 4
        assert field_descr.signed is True
        assert field_descr.repeat == 2

    @staticmethod
    def test_byteorder_consistency():
        typestr = '>i8'
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor(byteorder=bpack.EByteOrder.LE)
            class Record:                                       # noqa
                field: bpack.T[typestr]

        typestr = '<i8'
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor(byteorder=bpack.EByteOrder.BE)   # noqa: F811
            class Record:                                       # noqa
                field: bpack.T[typestr]

        typestr = '>i8' if sys.byteorder == 'little' else '<i8'
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor                                   # noqa: F811
            class Record:                                       # noqa
                field: bpack.T[typestr]

        typestr = '<i8' if sys.byteorder == 'little' else '>i8'

        @bpack.descriptor                                       # noqa: F811
        class Record:                                           # noqa
            field: bpack.T[typestr]

        typestr = '|i8'

        @bpack.descriptor(byteorder=bpack.EByteOrder.BE)       # noqa: F811
        class Record:                                           # noqa
            field: bpack.T[typestr]

    @staticmethod
    def test_size_consistency():
        typestr = 'i8'

        @bpack.descriptor
        class Record:
            field: bpack.T[typestr] = bpack.field(size=8, signed=True)

        descr = get_field_descriptor(bpack.fields(Record)[0])
        assert descr.type is int
        assert descr.size == 8
        assert descr.repeat is None
        assert descr.signed is True

        typestr = 'u8'

        @bpack.descriptor
        class Record:
            field: bpack.T[typestr] = bpack.field(size=8, signed=False)

        descr = get_field_descriptor(bpack.fields(Record)[0])
        assert descr.type is int
        assert descr.size == 8
        assert descr.repeat is None
        assert descr.signed is False

        typestr = 'f8'

        @bpack.descriptor
        class Record:
            field: bpack.T[typestr] = bpack.field(size=8)

        descr = get_field_descriptor(bpack.fields(Record)[0])
        assert descr.type is float
        assert descr.size == 8
        assert descr.repeat is None
        assert descr.signed is None

    @staticmethod
    def test_size_consistency_error():
        typestr = 'i8'
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor
            class Record:                                               # noqa
                field: bpack.T[typestr] = bpack.field(size=3)

    @staticmethod
    def test_signed_consistency_error():
        typestr = 'i8'
        with pytest.raises(bpack.descriptors.DescriptorConsistencyError):
            @bpack.descriptor
            class Record:                                               # noqa
                field: bpack.T[typestr] = bpack.field(size=8, signed=False)

    @staticmethod
    @pytest.mark.parametrize('typestr',
                             ['invalid', '@i8', '|x8', '|i0', '|ii'])
    def test_invalid_typestr(typestr):
        with pytest.raises(ValueError):
            @bpack.descriptor
            class Record:                                               # noqa
                field: bpack.T[typestr] = bpack.field(size=1)

"""Test bpack.utils."""

import enum

import pytest

import bpack.utils


class TestEnumType:
    @staticmethod
    @pytest.mark.parametrize('value', [1, 1.1, None, 'a', b'a'])
    def test_enum_type(value):
        class EEnumType(enum.Enum):
            A = value

        assert bpack.utils.enum_item_type(EEnumType) is type(value)

    @staticmethod
    def test_invalid_enum_type():
        class EInvalidEnumType:
            A = 'a'

        with pytest.raises(TypeError):
            assert bpack.utils.enum_item_type(EInvalidEnumType)

    @staticmethod
    def test_unsupported_enum_type():
        class EEnumType(enum.Enum):
            A = 'a'
            B = 'b'
            c = 1

        with pytest.raises(TypeError):
            assert bpack.utils.enum_item_type(EEnumType)

    @staticmethod
    def test_int_enum_type():
        class EEnumType(enum.IntEnum):
            A = 1

        assert bpack.utils.enum_item_type(EEnumType) is int

    @staticmethod
    def test_flag_enum_type():
        class EEnumType(enum.IntFlag):
            A = 1

        assert bpack.utils.enum_item_type(EEnumType) is int

    @staticmethod
    def test_subclass_types():
        class EFlagEnumType(enum.IntFlag):
            A = 1
            B = 2

        class EEnumType(enum.Enum):
            A = EFlagEnumType.A
            B = 0
            c = EFlagEnumType.B

        assert bpack.utils.enum_item_type(EEnumType) is int


def test_effective_type():
    assert bpack.utils.effective_type(None) is None
    assert bpack.utils.effective_type(int) is int
    assert bpack.utils.effective_type(str) is str
    assert bpack.utils.effective_type(bytes) is bytes
    assert bpack.utils.effective_type(float) is float

    class EStrEnumType(enum.Enum):
        A = 'a'
        B = 'b'

    assert bpack.utils.effective_type(EStrEnumType) is str

    class EBytesEnumType(enum.Enum):
        A = b'a'
        B = b'b'

    assert bpack.utils.effective_type(EBytesEnumType) is bytes

    class EIntEnumType(enum.Enum):
        A = 1
        B = 2

    assert bpack.utils.effective_type(EIntEnumType) is int

    class EFlagEnumType(enum.Enum):
        A = 1
        B = 2

    assert bpack.utils.effective_type(EFlagEnumType) is int

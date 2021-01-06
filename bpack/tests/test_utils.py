"""Test bpack.utils."""

import enum
import typing

import pytest

import bpack
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
            assert bpack.utils.enum_item_type(EInvalidEnumType)         # noqa

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
    assert bpack.utils.effective_type(bool) is bool
    assert bpack.utils.effective_type(int) is int
    assert bpack.utils.effective_type(str) is str
    assert bpack.utils.effective_type(bytes) is bytes
    assert bpack.utils.effective_type(float) is float
    assert bpack.utils.effective_type(None) is None                     # noqa

    for type_ in (typing.Type[typing.Any], typing.Tuple[int, float],
                  typing.Tuple[int]):
        assert bpack.utils.effective_type(type_) == type_


def test_effective_enum():
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


def test_effective_type_from_seq():
    assert bpack.utils.effective_type(typing.List[bool]) is bool
    assert bpack.utils.effective_type(typing.List[int]) is int
    assert bpack.utils.effective_type(typing.List[str]) is str
    assert bpack.utils.effective_type(typing.List[bytes]) is bytes
    assert bpack.utils.effective_type(typing.List[float]) is float


def test_effective_type_from_annotated_type():
    assert bpack.utils.effective_type(bpack.T['i']) is int
    assert bpack.utils.effective_type(bpack.T['u']) is int
    assert bpack.utils.effective_type(bpack.T['f']) is float
    assert bpack.utils.effective_type(bpack.T['c']) is complex
    assert bpack.utils.effective_type(bpack.T['S']) is bytes


def test_invalid_effective_type():
    with pytest.raises(TypeError):
        bpack.utils.effective_type('i8')                                # noqa


def test_effective_type_keep_annotations():
    atype = bpack.T['i8']
    etype = bpack.utils.effective_type(atype, keep_annotations=True)
    assert etype == atype


def test_get_sequence_type():
    type_ = typing.List[int]
    assert bpack.utils.sequence_type(type_) is list

    type_ = typing.Sequence[int]
    assert bpack.utils.sequence_type(type_) is tuple

    type_ = typing.Tuple[int, int]
    assert bpack.utils.sequence_type(type_) is None
    with pytest.raises(TypeError):
        bpack.utils.sequence_type(type_, error=True)

    assert bpack.utils.sequence_type(list) is None
    assert bpack.utils.sequence_type(typing.List) is None
    assert bpack.utils.sequence_type(typing.Sequence) is None
    assert bpack.utils.sequence_type(typing.Tuple) is None
    assert bpack.utils.sequence_type(typing.Type[typing.Any]) is None


def test_get_sequence_type_from_annotated_type():
    typestr = 'i8'

    type_ = typing.List[bpack.T[typestr]]
    assert bpack.utils.sequence_type(type_) is list

    type_ = typing.Sequence[bpack.T[typestr]]
    assert bpack.utils.sequence_type(type_) is tuple


def test_is_sequence_type():
    type_ = typing.List[int]
    assert bpack.utils.is_sequence_type(type_)

    type_ = typing.Sequence[int]
    assert bpack.utils.is_sequence_type(type_)

    type_ = typing.Tuple[int, int]
    assert not bpack.utils.is_sequence_type(type_)
    with pytest.raises(TypeError):
        bpack.utils.is_sequence_type(type_, error=True)

    assert not bpack.utils.is_sequence_type(list)
    assert not bpack.utils.is_sequence_type(typing.List)
    assert not bpack.utils.is_sequence_type(typing.Sequence)
    assert not bpack.utils.is_sequence_type(typing.Tuple)


def test_is_sequence_type_from_annotated_type():
    typestr = 'i8'

    type_ = typing.List[bpack.T[typestr]]
    assert bpack.utils.is_sequence_type(type_)

    type_ = typing.Sequence[bpack.T[typestr]]
    assert bpack.utils.is_sequence_type(type_)

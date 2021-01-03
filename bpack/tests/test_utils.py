"""Test bpack.utils."""

import enum
import string
import typing

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
    assert bpack.utils.effective_type(bool) is bool
    assert bpack.utils.effective_type(int) is int
    assert bpack.utils.effective_type(str) is str
    assert bpack.utils.effective_type(bytes) is bytes
    assert bpack.utils.effective_type(float) is float

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


def test_effective_type_from_typestr():
    assert bpack.utils.effective_type('i') is int
    assert bpack.utils.effective_type('u') is int
    assert bpack.utils.effective_type('f') is float
    assert bpack.utils.effective_type('c') is complex
    assert bpack.utils.effective_type('S') is bytes

    for type_ in ('invalid', '>x2'):
        assert bpack.utils.effective_type(type_) == type_


def test_effective_type_keep_typestr():
    assert bpack.utils.effective_type('i8', keep_typestr=True) == 'i8'


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


def test_get_sequence_type_from_typestr():
    type_ = typing.List['i8']  # noqa
    assert bpack.utils.sequence_type(type_) is list

    type_ = typing.Sequence['i8']  # noqa
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


def test_is_sequence_type_from_typestr():
    type_ = typing.List['i8']  # noqa
    assert bpack.utils.is_sequence_type(type_)

    type_ = typing.Sequence['i8']  # noqa
    assert bpack.utils.is_sequence_type(type_)


class TestStrToTypeParams:
    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    def test_byteorder(byteorder):
        s = f'{byteorder}i4'
        if byteorder in ('', '|'):
            byteorder = None
        else:
            byteorder = bpack.EByteOrder(byteorder if byteorder != '|' else '')
        params = bpack.utils.str_to_type_params(s)
        assert params.byteorder is byteorder

    @staticmethod
    @pytest.mark.parametrize('size', [1, 2, 4, 8, 3, 120])
    def test_size(size):
        s = f'i{size}'
        params = bpack.utils.str_to_type_params(s)
        assert params.size == size
        assert isinstance(params.size, int)

    @staticmethod
    @pytest.mark.parametrize('size', [0, -1])
    def test_invalid_size(size):
        s = f'i{size}'
        with pytest.raises(ValueError):
            bpack.utils.str_to_type_params(s)

    @staticmethod
    def test_no_size():
        s = 'i'
        params = bpack.utils.str_to_type_params(s)
        assert params.size is None

    TYPE_CODES = 'iufcS'
    UNSUPPORTED_TYPE_CODES = '?bBOatmMUV'
    INVALID_TYPE_CODES = (
            set(string.printable) - set(TYPE_CODES + UNSUPPORTED_TYPE_CODES)
    )

    @staticmethod
    @pytest.mark.parametrize('typecode', INVALID_TYPE_CODES)
    def test_invalid_typecode(typecode):
        s = f'{typecode}4'
        with pytest.raises(ValueError, match='invalid'):
            bpack.utils.str_to_type_params(s)

    @staticmethod
    @pytest.mark.parametrize('typecode', UNSUPPORTED_TYPE_CODES)
    def test_unsupported_typecode(typecode):
        s = f'{typecode}4'
        with pytest.raises(TypeError, match='not supported'):
            bpack.utils.str_to_type_params(s)

    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    @pytest.mark.parametrize('typecode', ['S'])
    @pytest.mark.parametrize('size', ['2', '4', '8'])
    def test_bytes_typecode(byteorder, typecode, size):
        s = f'{byteorder}{typecode}{size}'
        params = bpack.utils.str_to_type_params(s)
        assert params.type is bytes
        assert params.signed is None

    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    @pytest.mark.parametrize('typecode', ['f'])
    @pytest.mark.parametrize('size', ['2', '4', '8'])
    def test_float_typecode(byteorder, typecode, size):
        s = f'{byteorder}{typecode}{size}'
        params = bpack.utils.str_to_type_params(s)
        assert params.type is float
        assert params.signed is None

    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    @pytest.mark.parametrize('typecode', ['c'])
    @pytest.mark.parametrize('size', ['4', '8', '16'])
    def test_complex_typecode(byteorder, typecode, size):
        s = f'{byteorder}{typecode}{size}'
        params = bpack.utils.str_to_type_params(s)
        assert params.type is complex
        assert params.signed is None

    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    @pytest.mark.parametrize('typecode', ['i', 'u'])
    @pytest.mark.parametrize('size', ['2', '4', '8'])
    def test_int_typecode(byteorder, typecode, size):
        s = f'{byteorder}{typecode}{size}'
        signed = bool(typecode == 'i')
        params = bpack.utils.str_to_type_params(s)
        assert params.type is int
        assert params.signed == signed

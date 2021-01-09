"""Test bpack.typing."""

import string

import pytest

import bpack.typing


TYPE_CODES = 'iufcS'
UNSUPPORTED_TYPE_CODES = '?bBOatmMUV'
INVALID_TYPE_CODES = (
    set(string.printable) - set(TYPE_CODES + UNSUPPORTED_TYPE_CODES)
)


class TestStrToTypeParams:
    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    def test_byteorder(byteorder):
        s = f'{byteorder}i4'
        if byteorder in ('', '|'):
            byteorder = None
        else:
            byteorder = bpack.EByteOrder(byteorder if byteorder != '|' else '')
        params = bpack.typing.str_to_type_params(s)
        assert params.byteorder is byteorder

    @staticmethod
    @pytest.mark.parametrize('size', [1, 2, 4, 8, 3, 120])
    def test_size(size):
        s = f'i{size}'
        params = bpack.typing.str_to_type_params(s)
        assert params.size == size
        assert isinstance(params.size, int)

    @staticmethod
    @pytest.mark.parametrize('size', [0, -1])
    def test_invalid_size(size):
        s = f'i{size}'
        with pytest.raises(ValueError):
            bpack.typing.str_to_type_params(s)

    @staticmethod
    def test_no_size():
        s = 'i'
        params = bpack.typing.str_to_type_params(s)
        assert params.size is None

    @staticmethod
    @pytest.mark.parametrize('typecode', INVALID_TYPE_CODES)
    def test_invalid_typecode(typecode):
        s = f'{typecode}4'
        with pytest.raises(ValueError, match='invalid'):
            bpack.typing.str_to_type_params(s)

    @staticmethod
    @pytest.mark.parametrize('typecode', UNSUPPORTED_TYPE_CODES)
    def test_unsupported_typecode(typecode):
        s = f'{typecode}4'
        with pytest.raises(TypeError, match='not supported'):
            bpack.typing.str_to_type_params(s)

    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    @pytest.mark.parametrize('typecode', ['S'])
    @pytest.mark.parametrize('size', ['2', '4', '8'])
    def test_bytes_typecode(byteorder, typecode, size):
        s = f'{byteorder}{typecode}{size}'
        params = bpack.typing.str_to_type_params(s)
        assert params.type is bytes
        assert params.signed is None

    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    @pytest.mark.parametrize('typecode', ['f'])
    @pytest.mark.parametrize('size', ['2', '4', '8'])
    def test_float_typecode(byteorder, typecode, size):
        s = f'{byteorder}{typecode}{size}'
        params = bpack.typing.str_to_type_params(s)
        assert params.type is float
        assert params.signed is None

    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    @pytest.mark.parametrize('typecode', ['c'])
    @pytest.mark.parametrize('size', ['4', '8', '16'])
    def test_complex_typecode(byteorder, typecode, size):
        s = f'{byteorder}{typecode}{size}'
        params = bpack.typing.str_to_type_params(s)
        assert params.type is complex
        assert params.signed is None

    @staticmethod
    @pytest.mark.parametrize('byteorder', ['>', '<', '|', ''])
    @pytest.mark.parametrize('typecode', ['i', 'u'])
    @pytest.mark.parametrize('size', ['2', '4', '8'])
    def test_int_typecode(byteorder, typecode, size):
        s = f'{byteorder}{typecode}{size}'
        signed = bool(typecode == 'i')
        params = bpack.typing.str_to_type_params(s)
        assert params.type is int
        assert params.signed == signed


@pytest.mark.parametrize(
    'typestr, type_, params',
    [('i4', int, bpack.typing.TypeParams(None, int, 4, True)),
     ('u2', int, bpack.typing.TypeParams(None, int, 2, False)),
     ('f8', float, bpack.typing.TypeParams(None, float, 8, None)),
     ('c16', complex, bpack.typing.TypeParams(None, complex, 16, None)),
     ('S128', bytes, bpack.typing.TypeParams(None, bytes, 128, None)),
     ('>i8', int, bpack.typing.TypeParams(bpack.EByteOrder.BE, int, 8, True)),
     ('f', float, bpack.typing.TypeParams(None, float, None, None))],
    ids=['i4', 'u2', 'f8', 'c16', 'S128', '>i8', 'f'])
def test_type_annotation(typestr, type_, params):
    T = bpack.typing.T[typestr]                                         # noqa
    assert isinstance(T(), type_)
    atype, metadata = bpack.typing.get_args(T)
    assert metadata == params
    assert atype == type_ == metadata.type

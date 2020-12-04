"""Test bpack descriptors."""

import dataclasses
import collections.abc

import pytest

import bpack
import bpack.descriptors
from bpack import EBaseUnits, EOrder
from bpack.descriptors import get_field_descriptor, is_field
from bpack.descriptors import Field as BPackField


class TestFieldFactory:
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
        assert bpack.get_baseunits(Record()) is EBaseUnits(baseunits)

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
    def test_baseunits_attr():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert hasattr(Record, bpack.descriptors.BASEUNITS_ATTR_NAME)

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
                             argvalues=[EOrder.LSB, EOrder.MSB,
                                        EOrder.NATIVE, EOrder.DEFAULT,
                                        '<', '>', '=', '', None])
    def test_order(order):
        @bpack.descriptor(order=order)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=8, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        if isinstance(order, str):
            assert bpack.order(Record) is EOrder(order)
            assert bpack.order(Record()) is EOrder(order)
        else:
            assert bpack.order(Record) is order
            assert bpack.order(Record()) is order

    @staticmethod
    def test_invalid_order():
        with pytest.raises(ValueError):
            @bpack.descriptor(order='invalid')
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
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        # name, type, size, offset
        field_data = [('field_1', int, 4, 0), ('field_2', float, 8, 4)]

        for field_, data in zip(bpack.fields(Record), field_data):
            name, type_, size, offset = data
            assert field_.name == name
            assert field_.type == type_
            field_descr = get_field_descriptor(field_)
            assert field_descr.type == type_
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
            assert field_descr.type == type_
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
            assert field_descr.type == type_
            assert field_descr.size == size
            assert field_descr.offset == offset


class TestUtils:
    @staticmethod
    def test_is_descriptor():
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

        @dataclasses.dataclass
        class Record:
            field_1: int = 0

        setattr(Record, bpack.descriptors.BASEUNITS_ATTR_NAME, 'dummy')

        assert not bpack.is_descriptor(Record)
        assert not bpack.is_descriptor(Record())

        @dataclasses.dataclass
        class Record:
            pass

        setattr(Record, bpack.descriptors.BASEUNITS_ATTR_NAME, 'dummy')

        assert not bpack.is_descriptor(Record)
        assert not bpack.is_descriptor(Record())

        class Record:
            pass

        setattr(Record, bpack.descriptors.BASEUNITS_ATTR_NAME, 'dummy')

        assert not bpack.is_descriptor(Record)
        assert not bpack.is_descriptor(Record())

    @staticmethod
    def test_is_field():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        for field_ in bpack.fields(Record):
            assert is_field(field_)

        for field_ in bpack.fields(Record()):
            assert is_field(field_)

        dataclasses_field_ = dataclasses.field()
        assert not is_field(dataclasses_field_)

    @staticmethod
    def test_calcsize():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.calcsize(Record) == 12
        assert bpack.calcsize(Record()) == 12

        @dataclasses.dataclass
        class Record:
            field_1: int = 0

        with pytest.raises(TypeError):
            bpack.calcsize(Record)

        with pytest.raises(TypeError):
            bpack.calcsize(Record())

        class Record:
            pass

        with pytest.raises(TypeError):
            bpack.calcsize(Record)

        with pytest.raises(TypeError):
            bpack.calcsize(Record())

    @staticmethod
    def test_fields():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert isinstance(bpack.fields(Record), tuple)
        assert len(bpack.fields(Record)) == 2
        assert isinstance(bpack.fields(Record()), tuple)
        assert len(bpack.fields(Record())) == 2

    @staticmethod
    def test_get_baseunits():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.get_baseunits(Record) == EBaseUnits.BYTES
        assert bpack.get_baseunits(Record()) == EBaseUnits.BYTES

        @bpack.descriptor(baseunits=EBaseUnits.BYTES)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.get_baseunits(Record) == EBaseUnits.BYTES
        assert bpack.get_baseunits(Record()) == EBaseUnits.BYTES

        @bpack.descriptor(baseunits=EBaseUnits.BITS, size=16)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.get_baseunits(Record) == EBaseUnits.BITS
        assert bpack.get_baseunits(Record()) == EBaseUnits.BITS

        @dataclasses.dataclass
        class Record:
            field_1: int = 0

        with pytest.raises(TypeError):
            bpack.get_baseunits(Record)

    @staticmethod
    def test_order():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        assert bpack.order(Record) is None
        assert bpack.order(Record()) is None


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
                              (1.1, TypeError)])
    def test_post_validation_error_on_size(size, error_type):
        descr = bpack.descriptors.BinFieldDescriptor(int, 1, 2)
        descr.validate()
        descr.size = size
        with pytest.raises(error_type):
            descr.validate()

    @staticmethod
    @pytest.mark.parametrize('offset, error_type',
                             [(-1, ValueError),
                              (1.1, TypeError)])
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


class TestFieldDescriptorUtils:
    @staticmethod
    def test_field_descriptors_iter():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3)

        BinFieldDescriptor = bpack.descriptors.BinFieldDescriptor

        field_descriptors = bpack.descriptors.field_descriptors(Record)
        assert isinstance(field_descriptors, collections.abc.Iterable)
        field_descriptors = list(field_descriptors)
        assert all(isinstance(field_descr, BinFieldDescriptor)
                   for field_descr in field_descriptors)
        assert len(field_descriptors) == 2

        field_descriptors = bpack.descriptors.field_descriptors(Record())
        assert isinstance(field_descriptors, collections.abc.Iterable)
        field_descriptors = list(field_descriptors)
        assert all(isinstance(field_descr, BinFieldDescriptor)
                   for field_descr in field_descriptors)
        assert len(field_descriptors) == 2

    @staticmethod
    def test_field_descriptors_iter_with_pad():
        @bpack.descriptor(size=24)
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=4, default=0)
            field_2: float = bpack.field(size=8, default=1/3, offset=8)

        types_ = [int, None, float, None]
        BinFieldDescriptor = bpack.descriptors.BinFieldDescriptor

        field_descriptors = bpack.descriptors.field_descriptors(Record,
                                                                pad=True)
        assert isinstance(field_descriptors, collections.abc.Iterable)
        field_descriptors = list(field_descriptors)
        assert all(isinstance(field_descr, BinFieldDescriptor)
                   for field_descr in field_descriptors)
        assert len(field_descriptors) == 4
        assert [descr.type for descr in field_descriptors] == types_
        assert sum(descr.size for descr in field_descriptors) == 24
        assert bpack.calcsize(Record) == 24

        field_descriptors = bpack.descriptors.field_descriptors(Record(),
                                                                pad=True)
        assert isinstance(field_descriptors, collections.abc.Iterable)
        field_descriptors = list(field_descriptors)
        assert all(isinstance(field_descr, BinFieldDescriptor)
                   for field_descr in field_descriptors)
        assert len(field_descriptors) == 4
        assert [descr.type for descr in field_descriptors] == types_
        assert sum(descr.size for descr in field_descriptors) == 24
        assert bpack.calcsize(Record()) == 24

    @staticmethod
    def test_get_field_descriptor_01():
        field = bpack.field(size=1, offset=2, signed=True)
        with pytest.raises(TypeError):
            bpack.descriptors.get_field_descriptor(field)

        descr = bpack.descriptors.get_field_descriptor(field, validate=False)
        assert descr.type is None
        assert descr.size == 1
        assert descr.offset == 2
        assert descr.signed is True

        field.type = int
        descr = bpack.descriptors.get_field_descriptor(field)
        assert descr.type is int
        assert descr.size == 1
        assert descr.offset == 2
        assert descr.signed is True

    @staticmethod
    def test_get_field_descriptor_02():
        @bpack.descriptor
        @dataclasses.dataclass
        class Record:
            field_1: int = bpack.field(size=1, offset=2, default=0,
                                       signed=True)
            field_2: float = bpack.field(size=3, offset=4, default=0.1)

        data = [(int, 1, 2, True), (float, 3, 4, None)]
        for field, (type_, size, offset, signed) in zip(bpack.fields(Record),
                                                        data):
            descr = bpack.descriptors.get_field_descriptor(field)
            assert descr.type is type_
            assert descr.size == size
            assert descr.offset == offset
            assert descr.signed is signed

        record = Record()
        for field, (type_, size, offset, signed) in zip(bpack.fields(record),
                                                        data):
            descr = bpack.descriptors.get_field_descriptor(field)
            assert descr.type is type_
            assert descr.size == size
            assert descr.offset == offset
            assert descr.signed is signed

    @staticmethod
    def test_set_field_descriptor():
        field = dataclasses.field()
        assert not is_field(field)

        descr = bpack.descriptors.BinFieldDescriptor()
        with pytest.raises(TypeError):
            bpack.descriptors.set_field_descriptor(field, descr)

        bpack.descriptors.set_field_descriptor(field, descr, validate=False)
        assert is_field(field)

    @staticmethod
    def test_set_field_descriptor_type_mismatch():
        field = dataclasses.field()
        field.type = int

        descr = bpack.descriptors.BinFieldDescriptor(type=float, size=1)
        with pytest.raises(TypeError, match='mismatch'):
            bpack.descriptors.set_field_descriptor(field, descr)

    @staticmethod
    def test_set_field_descriptor_values():
        field = dataclasses.field()
        field.type = int
        assert not is_field(field)

        descr = bpack.descriptors.BinFieldDescriptor(type=field.type,
                                                     size=1, offset=2,
                                                     signed=True)
        bpack.descriptors.set_field_descriptor(field, descr)
        assert is_field(field)

        descr_out = bpack.descriptors.get_field_descriptor(field)
        assert descr_out.type is field.type
        assert descr_out.size == 1
        assert descr_out.offset == 2
        assert descr_out.signed is True

    @staticmethod
    def test_field_descriptor_metadata():
        field = dataclasses.field()
        field.type = int
        descr = bpack.descriptors.BinFieldDescriptor(type=field.type,
                                                     size=1, offset=2,
                                                     signed=True)
        bpack.descriptors.set_field_descriptor(field, descr)
        assert field.metadata is not None

        METADATA_KEY = bpack.descriptors.METADATA_KEY
        assert METADATA_KEY in field.metadata

        descr_metadata = field.metadata[METADATA_KEY]
        assert isinstance(descr_metadata, collections.abc.Mapping)
        with pytest.raises(TypeError):
            # immutable (types.MappingProxyType)
            descr_metadata['new_key'] = 'new_value'

        assert 'type' not in descr_metadata
        assert 'size' in descr_metadata
        assert descr_metadata['size'] == 1
        assert 'offset' in descr_metadata
        assert descr_metadata['offset'] == 2
        assert 'signed' in descr_metadata
        assert descr_metadata['signed'] is True
        assert len(descr_metadata) == 3

    @staticmethod
    def test_field_descriptor_minimal_metadata():
        field = dataclasses.field()
        field.type = int

        descr = bpack.descriptors.BinFieldDescriptor(type=field.type, size=1)
        bpack.descriptors.set_field_descriptor(field, descr)
        descr_metadata = field.metadata[bpack.descriptors.METADATA_KEY]

        assert 'type' not in descr_metadata
        assert 'size' in descr_metadata
        assert descr_metadata['size'] == 1
        assert len(descr_metadata) == 1

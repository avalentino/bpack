"""Test utility functions for descriptors."""

import dataclasses
import collections.abc
from typing import List

import pytest

import bpack
from bpack import EBaseUnits, EByteOrder, EBitOrder
from bpack.descriptors import BinFieldDescriptor, METADATA_KEY


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
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert bpack.is_descriptor(Record)
    assert bpack.is_descriptor(Record())

    class Record:
        field_1: int = 0

    setattr(Record, bpack.descriptors.BASEUNITS_ATTR_NAME, 'dummy')

    assert not bpack.is_descriptor(Record)
    assert not bpack.is_descriptor(Record())

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


def test_is_field():
    @bpack.descriptor
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    for field_ in bpack.fields(Record):
        assert bpack.is_field(field_)

    for field_ in bpack.fields(Record()):
        assert bpack.is_field(field_)

    dataclasses_field_ = dataclasses.field()
    assert not bpack.is_field(dataclasses_field_)


def test_calcsize():
    @bpack.descriptor
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1 / 3)
        field_3: List[int] = bpack.field(size=1, default=0, repeat=4)

    assert bpack.baseunits(Record) is EBaseUnits.BYTES
    assert bpack.calcsize(Record) == 16
    assert bpack.calcsize(Record()) == 16
    assert bpack.calcsize(Record, EBaseUnits.BYTES) == 16
    assert bpack.calcsize(Record, EBaseUnits.BITS) == 16 * 8

    @bpack.descriptor(baseunits=EBaseUnits.BITS)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=16, default=1/3)
        field_3: int = bpack.field(size=4, default=3)
        field_4: List[int] = bpack.field(size=4, default=0, repeat=2)

    assert bpack.baseunits(Record) is EBaseUnits.BITS
    assert bpack.calcsize(Record) == 4 * 8
    assert bpack.calcsize(Record()) == 4 * 8
    assert bpack.calcsize(Record, EBaseUnits.BYTES) == 4
    assert bpack.calcsize(Record, EBaseUnits.BITS) == 4 * 8

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


def test_fields():
    @bpack.descriptor
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert isinstance(bpack.fields(Record), tuple)
    assert len(bpack.fields(Record)) == 2
    assert isinstance(bpack.fields(Record()), tuple)
    assert len(bpack.fields(Record())) == 2


def test_get_baseunits():
    @bpack.descriptor
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert bpack.baseunits(Record) == EBaseUnits.BYTES
    assert bpack.baseunits(Record()) == EBaseUnits.BYTES

    @bpack.descriptor(baseunits=EBaseUnits.BYTES)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert bpack.baseunits(Record) == EBaseUnits.BYTES
    assert bpack.baseunits(Record()) == EBaseUnits.BYTES

    @bpack.descriptor(baseunits=EBaseUnits.BITS, size=16)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert bpack.baseunits(Record) == EBaseUnits.BITS
    assert bpack.baseunits(Record()) == EBaseUnits.BITS

    @dataclasses.dataclass
    class Record:
        field_1: int = 0

    with pytest.raises(TypeError):
        bpack.baseunits(Record)


@pytest.mark.parametrize('byteorder',
                         [EByteOrder.LE, EByteOrder.BE, EByteOrder.NATIVE,
                          EByteOrder.DEFAULT])
def test_byteorder_explicit(byteorder):
    @bpack.descriptor(byteorder=byteorder)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert bpack.byteorder(Record) is byteorder
    assert bpack.byteorder(Record()) is byteorder


def test_byteorder():
    @bpack.descriptor
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

    assert bpack.byteorder(Record) is EByteOrder.DEFAULT
    assert bpack.byteorder(Record()) is EByteOrder.DEFAULT

    @dataclasses.dataclass
    class Dummy:
        x: int = 0

    with pytest.raises(TypeError):
        bpack.byteorder(Dummy)

    class Dummy:
        pass

    with pytest.raises(TypeError):
        bpack.byteorder(Dummy)


@pytest.mark.parametrize('bitorder',
                         [EBitOrder.MSB, EBitOrder.LSB, EBitOrder.DEFAULT])
def test_bitorder(bitorder):
    @bpack.descriptor(bitorder=bitorder, baseunits=EBaseUnits.BITS)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)
        field_3: int = bpack.field(size=4, default=0)

    assert bpack.bitorder(Record) is bitorder
    assert bpack.bitorder(Record()) is bitorder


def test_bitorder_error():
    @dataclasses.dataclass
    class Dummy:
        x: int = 0

    with pytest.raises(TypeError):
        bpack.bitorder(Dummy)

    class Dummy:
        pass

    with pytest.raises(TypeError):
        bpack.bitorder(Dummy)


def test_field_descriptors_iter():
    @bpack.descriptor
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3)

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


def test_field_descriptors_iter_with_pad():
    @bpack.descriptor(size=24)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: float = bpack.field(size=8, default=1/3, offset=8)

    types_ = [int, None, float, None]

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


def test_get_field_descriptor_02():
    @bpack.descriptor
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


def test_set_field_descriptor():
    field = dataclasses.field()
    assert not bpack.is_field(field)

    descr = bpack.descriptors.BinFieldDescriptor()
    with pytest.raises(TypeError):
        bpack.descriptors.set_field_descriptor(field, descr)

    bpack.descriptors.set_field_descriptor(field, descr, validate=False)
    assert bpack.is_field(field)


def test_set_field_descriptor_type_mismatch():
    field = bpack.field()
    field.type = int

    descr = bpack.descriptors.BinFieldDescriptor(type=float, size=1)
    with pytest.raises(TypeError, match='mismatch'):
        bpack.descriptors.set_field_descriptor(field, descr)


def test_set_field_descriptor_values():
    field = dataclasses.field()
    field.type = int
    assert not bpack.is_field(field)

    descr = bpack.descriptors.BinFieldDescriptor(type=field.type,
                                                 size=1, offset=2,
                                                 signed=True)
    bpack.descriptors.set_field_descriptor(field, descr)
    assert bpack.is_field(field)

    descr_out = bpack.descriptors.get_field_descriptor(field)
    assert descr_out.type is field.type
    assert descr_out.size == 1
    assert descr_out.offset == 2
    assert descr_out.signed is True


def test_field_descriptor_metadata():
    field = bpack.field()
    field.type = int
    descr = bpack.descriptors.BinFieldDescriptor(type=field.type,
                                                 size=1, offset=2,
                                                 signed=True)
    bpack.descriptors.set_field_descriptor(field, descr)
    assert field.metadata is not None
    assert METADATA_KEY in field.metadata

    descr_metadata = field.metadata[METADATA_KEY]
    assert isinstance(descr_metadata, collections.abc.Mapping)
    with pytest.raises(TypeError):
        # immutable (types.MappingProxyType)
        descr_metadata['new_key'] = 'new_value'                         # noqa

    assert 'type' not in descr_metadata
    assert 'size' in descr_metadata
    assert descr_metadata['size'] == 1
    assert 'offset' in descr_metadata
    assert descr_metadata['offset'] == 2
    assert 'signed' in descr_metadata
    assert descr_metadata['signed'] is True
    assert len(descr_metadata) == 3


def test_field_descriptor_minimal_metadata():
    field = bpack.field()
    field.type = int

    descr = bpack.descriptors.BinFieldDescriptor(type=field.type, size=1)
    bpack.descriptors.set_field_descriptor(field, descr)
    descr_metadata = field.metadata[bpack.descriptors.METADATA_KEY]

    assert 'type' not in descr_metadata
    assert 'size' in descr_metadata
    assert descr_metadata['size'] == 1
    assert len(descr_metadata) == 1

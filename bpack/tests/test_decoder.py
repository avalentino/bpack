# -*- coding: utf-8 -*-

import dataclasses
from bpack.descriptor import descriptor, Field, EBaseUnits
from bpack import ba_decoder as ba
from bpack import bs_decoder as bs

import pytest


# TODO: test records with offsets and pad bit/bytes
# TODO: add support for enums


@descriptor(baseunits=EBaseUnits.BITS)
@dataclasses.dataclass(frozen=True)
class BitUnitsRecord:
    field_1: int = Field(size=3, default=0b101)
    field_2: bool = Field(size=1, default=False)
    field_3: int = Field(size=12, default=2048)
    field_4: float = Field(size=32, default=1.)


# Big Endian
BIT_ENCODED_DATA_BE = bytes(
    [0b10101000, 0b00000000, 0b00111111, 0b10000000, 0b00000000, 0b00000000]
)


@pytest.mark.parametrize('backend', [ba, bs])
@pytest.mark.parametrize(
    'Record, encoded_data, decoded_data',
    [(BitUnitsRecord, BIT_ENCODED_DATA_BE, BitUnitsRecord())])
def test_decoder(backend, Record, encoded_data, decoded_data):
    d = backend.Decoder(Record)
    record = d.decode(encoded_data)
    assert record == decoded_data


@pytest.mark.parametrize('backend', [ba, bs])
@pytest.mark.parametrize(
    'Record, encoded_data, decoded_data',
    [(BitUnitsRecord, BIT_ENCODED_DATA_BE, BitUnitsRecord())])
def test_decoder_func(backend, Record, encoded_data, decoded_data):
    record_type = backend.decoder(Record)
    record = record_type.from_bytes(encoded_data)
    assert record == decoded_data


@pytest.mark.parametrize('backend', [ba, bs])
def test_decoder_decorator(backend):
    @backend.decoder
    @descriptor(baseunits=EBaseUnits.BITS)
    @dataclasses.dataclass(frozen=True)
    class Record:
        field_1: int = Field(size=3, default=0b101)
        field_2: bool = Field(size=1, default=False)
        field_3: int = Field(size=12, default=2048)
        field_4: float = Field(size=32, default=1.)

    decoded_data = Record()
    encoded_data = BIT_ENCODED_DATA_BE
    record = Record.from_bytes(encoded_data)

    assert record.field_1 == decoded_data.field_1
    assert record.field_2 == decoded_data.field_2
    assert record.field_3 == decoded_data.field_3
    assert record.field_4 == decoded_data.field_4

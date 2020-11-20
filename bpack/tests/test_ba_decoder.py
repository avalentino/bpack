# -*- coding: utf-8 -*-

import dataclasses
from bpack.descriptor import descriptor, Field, EBaseUnits
from bpack.ba_decoder import Decoder, decoder


@descriptor(baseunits=EBaseUnits.BITS)
@dataclasses.dataclass(frozen=True)
class Record:
    field_1: int = Field(size=3, default=0b101)
    field_2: bool = Field(size=1, default=False)
    field_3: int = Field(size=12, default=2048)
    field_4: float = Field(size=32, default=1.)


# Little Endian
ENCODED_DATA = bytes(
    [0b10101000, 0b00000000, 0b00000000, 0b00000000, 0b10000000, 0b00111111]
)
DECODED_DATA = Record()


def test_decoder():
    d = Decoder(Record)
    record = d.decode(ENCODED_DATA)
    assert record == DECODED_DATA


def test_decoder_func():
    RecordType = decoder(Record)
    record = RecordType.from_bytes(ENCODED_DATA)
    assert record == DECODED_DATA


def test_decoder_func():
    @decoder
    @descriptor(baseunits=EBaseUnits.BITS)
    @dataclasses.dataclass(frozen=True)
    class Record2:
        field_1: int = Field(size=3, default=0b101)
        field_2: bool = Field(size=1, default=False)
        field_3: int = Field(size=12, default=2048)
        field_4: float = Field(size=32, default=1.)

    record = Record2.from_bytes(ENCODED_DATA)

    assert record.field_1 == DECODED_DATA.field_1
    assert record.field_2 == DECODED_DATA.field_2
    assert record.field_3 == DECODED_DATA.field_3
    assert record.field_4 == DECODED_DATA.field_4

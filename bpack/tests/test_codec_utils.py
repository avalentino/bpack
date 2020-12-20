"""Tests for codec utils."""

import dataclasses

import bpack
import bpack.ba
import bpack.bs
import bpack.st

from bpack.codec_utils import is_decoder, get_decoder, get_decoder_type


def test_decoder_helpers():
    backend = bpack.st

    @backend.decoder
    @bpack.descriptor
    @dataclasses.dataclass
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: int = bpack.field(size=4, default=0)

    assert is_decoder(Record)
    assert get_decoder_type(Record) is backend.Decoder
    assert type(get_decoder(Record)) is backend.Decoder

    record = Record()
    assert is_decoder(record)
    assert get_decoder_type(record) is backend.Decoder
    assert type(get_decoder(record)) is backend.Decoder

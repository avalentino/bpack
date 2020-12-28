"""Tests for codec utils."""

import dataclasses

import pytest

import bpack
import bpack.bs
import bpack.st

from bpack.codec_utils import is_decoder, get_decoder, get_decoder_type


@pytest.mark.parametrize('backend', [bpack.bs, bpack.st], ids=['bs', 'st'])
def test_decoder_helpers(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=backend.Decoder.baseunits)
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

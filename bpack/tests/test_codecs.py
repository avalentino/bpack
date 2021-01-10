"""Tests for codec utils."""

import pytest

import bpack
import bpack.st

from bpack.codecs import has_codec, get_codec, get_codec_type

try:
    import bpack.bs as bpack_bs
except ImportError:                                         # pragma: no cover
    bpack_bs = None


@pytest.mark.parametrize('backend',
                         [pytest.param(bpack.st, id='st'),
                          pytest.param(bpack_bs, id='bs',
                                       marks=pytest.mark.skipif(
                                           not bpack_bs,
                                           reason='not available'))])
def test_decoder_helpers(backend):
    @backend.decoder
    @bpack.descriptor(baseunits=backend.Decoder.baseunits)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: int = bpack.field(size=4, default=0)

    assert has_codec(Record)
    assert has_codec(Record, bpack.codecs.Decoder)
    assert has_codec(Record, backend.Decoder)
    assert get_codec_type(Record) is backend.Decoder
    assert isinstance(get_codec(Record), backend.Decoder)
    assert isinstance(get_codec(Record), bpack.codecs.Decoder)

    record = Record()
    assert has_codec(record)
    assert has_codec(record, bpack.codecs.Decoder)
    assert has_codec(record, backend.Decoder)
    assert get_codec_type(record) is backend.Decoder
    assert isinstance(get_codec(record), backend.Decoder)
    assert isinstance(get_codec(record), bpack.codecs.Decoder)

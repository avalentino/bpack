"""Tests for codec utils."""

import pytest

import bpack
import bpack.st

from bpack.codecs import has_codec, get_codec, get_codec_type

try:
    import bpack.bs as bpack_bs
except ImportError:  # pragma: no cover
    bpack_bs = None


@pytest.mark.parametrize(
    "backend",
    [
        pytest.param(bpack.st, id="st"),
        pytest.param(
            bpack_bs,
            id="bs",
            marks=pytest.mark.skipif(not bpack_bs, reason="not available"),
        ),
    ],
)
def test_codec_helpers(backend):
    @backend.codec
    @bpack.descriptor(baseunits=backend.Decoder.baseunits)
    class Record:
        field_1: int = bpack.field(size=4, default=0)
        field_2: int = bpack.field(size=4, default=0)

    assert has_codec(Record)
    assert has_codec(Record, bpack.codecs.Decoder)
    assert has_codec(Record, backend.Decoder)
    assert has_codec(Record, bpack.codecs.Encoder)
    assert has_codec(Record, backend.Encoder)
    assert has_codec(Record, bpack.codecs.Codec)
    assert has_codec(Record, backend.Codec)
    assert get_codec_type(Record) is backend.Codec
    assert isinstance(get_codec(Record), backend.Codec)
    assert isinstance(get_codec(Record), bpack.codecs.Codec)

    record = Record()
    assert has_codec(record)
    assert has_codec(record, bpack.codecs.Decoder)
    assert has_codec(record, backend.Decoder)
    assert has_codec(record, bpack.codecs.Encoder)
    assert has_codec(record, backend.Encoder)
    assert has_codec(record, bpack.codecs.Codec)
    assert has_codec(record, backend.Codec)
    assert get_codec_type(record) is backend.Codec
    assert isinstance(get_codec(record), backend.Codec)
    assert isinstance(get_codec(record), bpack.codecs.Codec)

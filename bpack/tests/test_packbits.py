"""Unit tests for packbit and unpackbut functions."""

import math
from collections.abc import Sequence

import pytest

try:
    import bpack.ba as bpack_ba
except ImportError:  # pragma: no cover
    bpack_ba = None

try:
    import bitstruct

    import bpack.bs as bpack_bs
except ImportError:  # pragma: no cover
    bitstruct = None
    bpack_bs = None

try:
    import numpy as np

    import bpack.np as bpack_np
except ImportError:  # pragma: no cover
    np = None
    bpack_np = None


def _sample_data(
    bits_per_sample: int, nsamples: int = 256
) -> tuple[bytes, Sequence[int]]:
    """Generate a packed data block having spb samples bps bits each."""
    # fmt: off
    elementary_range = {
        2: bytes([0b00011011]),
        3: bytes([0b00000101, 0b00111001, 0b01110111]),
        4: bytes([0b00000001, 0b00100011, 0b01000101, 0b01100111,
                  0b10001001, 0b10101011, 0b11001101, 0b11101111]),
        5: bytes([0b00000000, 0b01000100, 0b00110010, 0b00010100, 0b11000111,
                  0b01000010, 0b01010100, 0b10110110, 0b00110101, 0b11001111,
                  0b10000100, 0b01100101, 0b00111010, 0b01010110, 0b11010111,
                  0b11000110, 0b01110101, 0b10111110, 0b01110111, 0b11011111]),
        6: bytes([0b00000000, 0b00010000, 0b10000011, 0b00010000, 0b01010001,
                  0b10000111, 0b00100000, 0b10010010, 0b10001011, 0b00110000,
                  0b11010011, 0b10001111, 0b01000001, 0b00010100, 0b10010011,
                  0b01010001, 0b01010101, 0b10010111, 0b01100001, 0b10010110,
                  0b10011011, 0b01110001, 0b11010111, 0b10011111, 0b10000010,
                  0b00011000, 0b10100011, 0b10010010, 0b01011001, 0b10100111,
                  0b10100010, 0b10011010, 0b10101011, 0b10110010, 0b11011011,
                  0b10101111, 0b11000011, 0b00011100, 0b10110011, 0b11010011,
                  0b01011101, 0b10110111, 0b11100011, 0b10011110, 0b10111011,
                  0b11110011, 0b11011111, 0b10111111]),
        7: bytes([0b00000000, 0b00000100, 0b00010000, 0b00110000, 0b10000001,
                  0b01000011, 0b00000111, 0b00010000, 0b00100100, 0b01010000,
                  0b10110001, 0b10000011, 0b01000111, 0b00001111, 0b00100000,
                  0b01000100, 0b10010001, 0b00110010, 0b10000101, 0b01001011,
                  0b00010111, 0b00110000, 0b01100100, 0b11010001, 0b10110011,
                  0b10000111, 0b01001111, 0b00011111, 0b01000000, 0b10000101,
                  0b00010010, 0b00110100, 0b10001001, 0b01010011, 0b00100111,
                  0b01010000, 0b10100101, 0b01010010, 0b10110101, 0b10001011,
                  0b01010111, 0b00101111, 0b01100000, 0b11000101, 0b10010011,
                  0b00110110, 0b10001101, 0b01011011, 0b00110111, 0b01110000,
                  0b11100101, 0b11010011, 0b10110111, 0b10001111, 0b01011111,
                  0b00111111, 0b10000001, 0b00000110, 0b00010100, 0b00111000,
                  0b10010001, 0b01100011, 0b01000111, 0b10010001, 0b00100110,
                  0b01010100, 0b10111001, 0b10010011, 0b01100111, 0b01001111,
                  0b10100001, 0b01000110, 0b10010101, 0b00111010, 0b10010101,
                  0b01101011, 0b01010111, 0b10110001, 0b01100110, 0b11010101,
                  0b10111011, 0b10010111, 0b01101111, 0b01011111, 0b11000001,
                  0b10000111, 0b00010110, 0b00111100, 0b10011001, 0b01110011,
                  0b01100111, 0b11010001, 0b10100111, 0b01010110, 0b10111101,
                  0b10011011, 0b01110111, 0b01101111, 0b11100001, 0b11000111,
                  0b10010111, 0b00111110, 0b10011101, 0b01111011, 0b01110111,
                  0b11110001, 0b11100111, 0b11010111, 0b10111111, 0b10011111,
                  0b01111111, 0b01111111]),
        8: bytes(range(2 ** 8)),
    }
    # fmt: on
    assert (nsamples * bits_per_sample) % 8 == 0
    base_range = elementary_range[bits_per_sample]
    nreplica = math.ceil(nsamples / 2**bits_per_sample)
    nbytes = nsamples * bits_per_sample // 8
    data = (base_range * nreplica)[:nbytes]

    base_range = list(range(2**bits_per_sample))
    values = (base_range * nreplica)[:nsamples]

    return data, values


@pytest.mark.parametrize(
    "backend",
    [
        pytest.param(
            bpack_bs,
            id="bs",
            marks=pytest.mark.skipif(not bpack_bs, reason="not available"),
        )
    ],
)
@pytest.mark.parametrize("bits_per_sample", [2, 3, 4, 5, 6, 7, 8])
@pytest.mark.parametrize("nsamples", [256])
def test_packbits(backend, bits_per_sample, nsamples):
    data, values = _sample_data(bits_per_sample, nsamples)
    odata = backend.packbits(values, bits_per_sample)
    assert odata == data


@pytest.mark.parametrize(
    "backend",
    [
        pytest.param(
            bpack_bs,
            id="bs",
            marks=pytest.mark.skipif(not bpack_bs, reason="not available"),
        )
    ],
)
@pytest.mark.parametrize("bits_per_sample", [3])
@pytest.mark.parametrize("nsamples", [256])
def test_packbits_bad_values(backend, bits_per_sample, nsamples):
    values = [2**bits_per_sample] * nsamples
    with pytest.raises(Exception):  # TODO: improve error handling
        backend.packbits(values, bits_per_sample)


@pytest.mark.parametrize(
    "backend",
    [
        pytest.param(
            bpack_bs,
            id="bs",
            marks=pytest.mark.skipif(not bpack_bs, reason="not available"),
        )
    ],
)
@pytest.mark.parametrize("bits_per_sample", [3])
def test_packbits_nsanples_requires_pad(backend, bits_per_sample):
    values = [1]
    nsamples = len(values)
    # the number of samples does not fits an integer number of bytes
    assert (nsamples * bits_per_sample % 8) != 0
    with pytest.warns(UserWarning):
        backend.packbits(values, bits_per_sample)


@pytest.mark.parametrize(
    "backend",
    [
        pytest.param(
            bpack_ba,
            id="ba",
            marks=pytest.mark.skipif(not bpack_ba, reason="not available"),
        ),
        pytest.param(
            bpack_bs,
            id="bs",
            marks=pytest.mark.skipif(not bpack_bs, reason="not available"),
        ),
        pytest.param(
            bpack_np,
            id="np",
            marks=pytest.mark.skipif(not bpack_np, reason="not available"),
        ),
    ],
)
@pytest.mark.parametrize("bits_per_sample", [2, 3, 4, 5, 6, 7, 8])
@pytest.mark.parametrize("nsamples", [256])
def test_unpackbits(backend, bits_per_sample, nsamples):
    data, values = _sample_data(bits_per_sample, nsamples)
    ovalues = backend.unpackbits(data, bits_per_sample)
    assert list(ovalues) == values


@pytest.mark.parametrize(
    "backend",
    [
        pytest.param(
            bpack_ba,
            id="ba",
            marks=pytest.mark.skipif(not bpack_ba, reason="not available"),
        ),
        pytest.param(
            bpack_bs,
            id="bs",
            marks=pytest.mark.skipif(not bpack_bs, reason="not available"),
        ),
        pytest.param(
            bpack_np,
            id="np",
            marks=pytest.mark.skipif(not bpack_np, reason="not available"),
        ),
    ],
)
def test_unpackbits_1_bit_per_sample(backend):
    bits_per_sample = 1
    values = [1, 0, 1, 0, 1, 0, 1, 0]
    data = bytes([0b10101010])
    ovalues = backend.unpackbits(data, bits_per_sample)
    assert list(ovalues) == values


@pytest.mark.skipif(not bpack_bs, reason="bitstruct not available")
@pytest.mark.parametrize(
    "backend",
    [
        pytest.param(
            bpack_ba,
            id="ba",
            marks=pytest.mark.skipif(not bpack_ba, reason="not available"),
        ),
        pytest.param(
            bpack_bs,
            id="bs",
            marks=pytest.mark.skipif(not bpack_bs, reason="not available"),
        ),
        pytest.param(
            bpack_np,
            id="np",
            marks=pytest.mark.skipif(not bpack_np, reason="not available"),
        ),
    ],
)
@pytest.mark.parametrize("bits_per_sample", [10, 12, 14, 16, 32, 64])
@pytest.mark.parametrize("nsamples", [256])
def test_unpackbits_large(backend, bits_per_sample, nsamples):
    values = [item % (2**bits_per_sample) for item in range(nsamples)]
    data = bpack_bs.packbits(values, bits_per_sample)
    ovalues = backend.unpackbits(data, bits_per_sample)
    assert list(ovalues) == values


def _make_sample_data_block(
    header_size,
    bits_per_sample,
    samples_per_block,
    bit_offset=0,
    nblocks=1,
    sign_mode=0,
):
    bits_per_block = header_size + bits_per_sample * samples_per_block
    nbytes = math.ceil((bit_offset + bits_per_block) / 8)

    typechar = "s" if sign_mode == 1 else "u"
    block_fmt = f"{typechar}{bits_per_sample}" * samples_per_block
    if header_size > 0:
        block_fmt = f"u{header_size}" + block_fmt

    leading_pad = f"p{bit_offset}" if bit_offset > 0 else ""
    trailing_pad = nbytes * 8 - bits_per_block * nblocks - bit_offset
    trailing_pad = f"p{trailing_pad}" if trailing_pad > 0 else ""
    fmt = f"{leading_pad}{block_fmt * nblocks}{trailing_pad}"

    n = 2**bits_per_sample
    if sign_mode == 0:
        ramp_values = list(range(n)) * math.ceil(samples_per_block / n)
        out_values = ramp_values
    elif sign_mode == 1:
        hs = 2 ** (bits_per_sample - 1)
        ramp_values = list(range(-hs, hs)) * math.ceil(samples_per_block / n)
        out_values = ramp_values
    elif sign_mode == 2:
        hs = 2 ** (bits_per_sample - 1)
        ramp_values = list(range(hs))
        out_values = ramp_values + [-item for item in ramp_values]
        out_values *= math.ceil(samples_per_block / n)
        sign_mask = 2 ** (bits_per_sample - 1)
        ramp_values += [item | sign_mask for item in ramp_values]
        ramp_values *= math.ceil(samples_per_block / n)
    else:
        raise ValueError(f"Unexpected 'sign_mode': {sign_mode}")
    values = ramp_values[:samples_per_block]
    out_values = out_values[:samples_per_block]
    if header_size > 0:
        values = [113] + values
        out_values = [113] + out_values
    values *= nblocks
    out_values *= nblocks
    data = bitstruct.pack(fmt, *values)

    return data, out_values


@pytest.mark.skipif(not bitstruct, reason="bitstruct not available")
@pytest.mark.skipif(not np, reason="numpy not available")
@pytest.mark.parametrize("bit_offset", [0, 1, 2])
@pytest.mark.parametrize("header_size", [9, 13])
@pytest.mark.parametrize("bits_per_sample", [3, 4, 5, 6, 12, 13, 14])
@pytest.mark.parametrize("samples_per_block", [64, 128, 256])
@pytest.mark.parametrize("nblocks", [1, 3, 20])
def test_headers(
    bit_offset, header_size, bits_per_sample, samples_per_block, nblocks
):
    data, values = _make_sample_data_block(
        header_size,
        bits_per_sample,
        samples_per_block,
        bit_offset,
        nblocks=nblocks,
    )

    block_size = header_size + bits_per_sample * samples_per_block

    headers = bpack_np.unpackbits(
        data,
        bits_per_sample=header_size,
        samples_per_block=1,
        bit_offset=bit_offset,
        blockstride=block_size,
    )
    assert len(headers) == nblocks
    assert all(headers == values[0])


@pytest.mark.skipif(not bitstruct, reason="bitstruct not available")
@pytest.mark.skipif(not np, reason="numpy not available")
@pytest.mark.parametrize("bit_offset", [0, 1, 2])
@pytest.mark.parametrize("header_size", [0, 9, 13])
@pytest.mark.parametrize("bits_per_sample", [3, 4, 5, 8, 13])
@pytest.mark.parametrize("samples_per_block", [64, 128])
@pytest.mark.parametrize("nblocks", [1, 3, 20])
@pytest.mark.parametrize("sign_mode", [0, 1, 2])
def test_data(
    bit_offset,
    header_size,
    bits_per_sample,
    samples_per_block,
    nblocks,
    sign_mode,
):
    data, values = _make_sample_data_block(
        header_size,
        bits_per_sample,
        samples_per_block,
        bit_offset,
        nblocks=nblocks,
        sign_mode=sign_mode,
    )

    assert len(values) == (
        samples_per_block * nblocks + (nblocks if header_size else 0)
    )

    block_size = header_size + bits_per_sample * samples_per_block

    odata = bpack_np.unpackbits(
        data,
        bits_per_sample,
        samples_per_block,
        bit_offset=bit_offset + header_size,
        blockstride=block_size,
        sign_mode=sign_mode,
    )

    extra_bits = len(data) * 8 - bit_offset - block_size * nblocks
    extra_bits = max(extra_bits - header_size, 0)
    extra_samples = extra_bits // bits_per_sample
    assert len(odata) == nblocks * samples_per_block + extra_samples
    k = 1 if header_size > 0 else 0
    for idx in range(nblocks):
        oslice = slice(samples_per_block * idx, samples_per_block * (idx + 1))
        vslice = slice(
            k + (samples_per_block + k) * idx,
            k + (samples_per_block + k) * idx + samples_per_block,
        )
        assert all(odata[oslice] == values[vslice])


@pytest.mark.skipif(not bitstruct, reason="bitstruct not available")
@pytest.mark.skipif(not np, reason="numpy not available")
@pytest.mark.parametrize(
    "header_size, dtype",
    [
        (7, ">u1"),
        (8, ">u1"),
        (9, ">u2"),
        (15, ">u2"),
        (16, ">u2"),
        (17, ">u4"),
    ],
)
def test_headers_dtype(header_size, dtype):
    bits_per_sample = 8
    samples_per_block = 64

    data, _ = _make_sample_data_block(
        header_size, bits_per_sample, samples_per_block
    )

    headers = bpack_np.unpackbits(
        data, bits_per_sample=header_size, samples_per_block=1
    )
    assert headers.dtype == np.dtype(dtype)


@pytest.mark.skipif(not bitstruct, reason="bitstruct not available")
@pytest.mark.skipif(not np, reason="numpy not available")
@pytest.mark.parametrize(
    "bits_per_sample, dtype",
    [
        (7, ">u1"),
        (8, ">u1"),
        (9, ">u2"),
        (15, ">u2"),
        (16, ">u2"),
        (17, ">u4"),
    ],
)
def test_data_dtype(bits_per_sample, dtype):
    header_size = 0
    samples_per_block = 64

    data, _ = _make_sample_data_block(
        header_size, bits_per_sample, samples_per_block
    )

    odata = bpack_np.unpackbits(data, bits_per_sample, samples_per_block)
    assert odata.dtype == np.dtype(dtype)


@pytest.mark.skipif(not bitstruct, reason="bitstruct not available")
@pytest.mark.skipif(not np, reason="numpy not available")
def test_auto_sample_per_block():
    header_size = 0
    samples_per_block = 64
    bits_per_sample = 3

    data, _ = _make_sample_data_block(
        header_size, bits_per_sample, samples_per_block
    )
    odata = bpack_np.unpackbits(data, bits_per_sample)
    assert len(odata) == samples_per_block

    with pytest.raises(ValueError):
        bpack_np.unpackbits(
            data,
            bits_per_sample,
            blockstride=bits_per_sample * samples_per_block,
        )


@pytest.mark.skipif(not np, reason="numpy not available")
@pytest.mark.parametrize(
    ["bits_per_sample", "mode", "ref_mask"],
    [
        (3, 0, 0b00000111),
        (20, 0, 0b000011111111111111111111),
        (34, 0, 0b0000001111111111111111111111111111111111),
        (3, 1, 0b11111000),
        (3, 2, 0b00000100),
    ],
)
def test_make_bitmask(bits_per_sample, mode, ref_mask):
    mask = bpack_np.make_bitmask(bits_per_sample, mode=mode)
    assert mask == ref_mask

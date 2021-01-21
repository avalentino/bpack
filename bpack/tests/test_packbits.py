"""Unit tests for packbit and unpackbut functions."""

import math
from typing import Sequence, Tuple

import pytest


bpack_ba = pytest.importorskip('bpack.ba')
bpack_bs = pytest.importorskip('bpack.bs')
bpack_np = pytest.importorskip('bpack.np')


def sample_data(bits_per_sample: int,
                nsamples: int = 256) -> Tuple[bytes, Sequence[int]]:
    """Generate a packed data block having spb samples bps bits each."""
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
        8: bytes(range(2**8)),
    }
    assert (nsamples * bits_per_sample) % 8 == 0
    base_range = elementary_range[bits_per_sample]
    nreplica = math.ceil(nsamples / 2**bits_per_sample)
    nbytes = nsamples * bits_per_sample // 8
    data = (base_range * nreplica)[:nbytes]

    base_range = list(range(2**bits_per_sample))
    values = (base_range * nreplica)[:nsamples]

    return data, values


@pytest.mark.parametrize('packfunc', [bpack_bs.packbits], ids=['bs'])
@pytest.mark.parametrize('bits_per_sample', [2, 3, 4, 5, 6, 7, 8])
@pytest.mark.parametrize('nsamples', [256])
def test_packbits(packfunc, bits_per_sample, nsamples):
    data, values = sample_data(bits_per_sample, nsamples)
    odata = packfunc(values, bits_per_sample)
    assert odata == data


@pytest.mark.parametrize('packfunc', [bpack_bs.packbits], ids=['bs'])
@pytest.mark.parametrize('bits_per_sample', [3])
@pytest.mark.parametrize('nsamples', [256])
def test_packbits_bad_values(packfunc, bits_per_sample, nsamples):
    values = [2 ** bits_per_sample] * nsamples
    with pytest.raises(Exception):  # TODO: improve error handling
        packfunc(values, bits_per_sample)


@pytest.mark.parametrize('packfunc', [bpack_bs.packbits], ids=['bs'])
@pytest.mark.parametrize('bits_per_sample', [3])
def test_packbits_nsanples_requires_pad(packfunc, bits_per_sample):
    values = [1]
    nsamples = len(values)
    # the number of samples does not fits an integer number of bytes
    assert (nsamples * bits_per_sample % 8) != 0
    with pytest.warns(UserWarning):
        packfunc(values, bits_per_sample)


@pytest.mark.parametrize('unpackfunc',
                         [bpack_ba.unpackbits, bpack_bs.unpackbits,
                          bpack_np.unpackbits],
                         ids=['ba', 'bs', 'np'])
@pytest.mark.parametrize('bits_per_sample', [2, 3, 4, 5, 6, 7, 8])
@pytest.mark.parametrize('nsamples', [256])
def test_unpackbits(unpackfunc, bits_per_sample, nsamples):
    data, values = sample_data(bits_per_sample, nsamples)
    ovalues = unpackfunc(data, bits_per_sample)
    assert list(ovalues) == values

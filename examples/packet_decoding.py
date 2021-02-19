import dataclasses
from typing import Tuple

import numpy as np

from bpack.np import unpackbits


@dataclasses.dataclass(frozen=True)
class PacketDescriptor:
    header_size: int
    bits_per_sample: int
    nsamples: int

    @property
    def packet_size(self):
        return self.header_size + self.bits_per_sample * self.nsamples


def decode_packet(data: bytes,
                  descr: PacketDescriptor) -> Tuple[np.ndarray, np.ndarray]:
    if descr.header_size > 0:
        headers = unpackbits(data, descr.header_size,
                             samples_per_block=1,
                             blockstride=descr.packet_size)
    else:
        headers = np.empty(shape=(), dtype='u1')

    samples = unpackbits(data, descr.bits_per_sample,
                         samples_per_block=descr.nsamples,
                         bit_offset=descr.header_size,
                         blockstride=descr.packet_size)

    return samples, headers


def test():
    from bpack.tests.test_packbits import (
        _make_sample_data_block as mk_sample_data
    )

    descr = PacketDescriptor(header_size=13, bits_per_sample=5, nsamples=64)
    print('descr', descr)

    data, values = mk_sample_data(descr.header_size, descr.bits_per_sample,
                                  descr.nsamples, nblocks=2)

    values_per_block = 1 + descr.nsamples
    header_values = np.asarray(values[::values_per_block])
    sample_values = np.asarray([
        values[start:start + descr.nsamples]
        for start in range(1, len(values), values_per_block)
    ]).ravel()
    print('header_values:', header_values)
    print('sample_values:', sample_values)

    samples, headers = decode_packet(data, descr)
    print('headers:', headers)
    print('samples:', samples)

    assert (headers == header_values).all()
    assert (samples == sample_values).all()


if __name__ == '__main__':
    test()

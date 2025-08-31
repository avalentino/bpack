"""Numpy based codec for binary data structures."""

import enum
import functools
import collections
from typing import NamedTuple

import numpy as np

import bpack
import bpack.utils
import bpack.codecs

from .enums import EBaseUnits
from .descriptors import (
    field_descriptors,
    get_field_descriptor,
    BinFieldDescriptor,
)

__all__ = [
    "Decoder",
    "decoder",
    "Encoder",
    "encoder",
    "Codec",
    "codec",
    "BACKEND_NAME",
    "BACKEND_TYPE",
    "descriptor_to_dtype",
    "unpackbits",
    "ESignMode",
]


BACKEND_NAME = "numpy"
BACKEND_TYPE = EBaseUnits.BYTES


def bin_field_descripor_to_dtype(field_descr: BinFieldDescriptor) -> np.dtype:
    """Convert a field descriptor into a :class:`numpy.dtype`.

    .. seealso:: :class:`bpack.descriptors.BinFieldDescriptor`.
    """
    # TODO: add byteorder
    size = field_descr.size
    etype = bpack.utils.effective_type(field_descr.type)
    typecode = np.dtype(etype).kind

    if etype in (bytes, str):
        typecode = "S"
    elif etype is int and not field_descr.signed:
        typecode = "u"

    if typecode == "O":
        raise TypeError(f"unsupported type: {field_descr.type:!r}")

    repeat = field_descr.repeat
    repeat = repeat if repeat and repeat > 1 else ""

    return np.dtype(f"{repeat}{typecode}{size}")


def descriptor_to_dtype(descriptor) -> np.dtype:
    """Convert the descriptor of a binary record into a :class:`numpy.dtype`.

    Please note that (unicode) strings are treated as "utf-8" encoded
    byte strings.
    UCS4 encoded strings are not supported.

    Sequences (:class:`typing.Sequence` and :class:`typing.List`) are
    always converted into :class:`numpy.ndarray`.

    .. seealso:: :func:`bpack.descriptors.descriptor`.
    """
    params = collections.defaultdict(list)
    for field in bpack.fields(descriptor):
        field_descr = get_field_descriptor(field)
        if bpack.is_descriptor(field_descr.type):
            dtype = descriptor_to_dtype(field_descr.type)
        else:
            dtype = bin_field_descripor_to_dtype(field_descr)
        params["names"].append(field.name)
        params["formats"].append(dtype)
        params["offsets"].append(field_descr.offset)
        # params['titles'].append('...')

    params = dict(params)  # numpy do not accept defaultdict
    params["itemsize"] = bpack.calcsize(descriptor)

    dt = np.dtype(params)

    byteorder = bpack.byteorder(descriptor).value
    if byteorder:
        dt = dt.newbyteorder(byteorder)

    return dt


def _decode_converter_factory(type_):
    etype = bpack.utils.effective_type(type_)
    if bpack.utils.is_enum_type(type_):
        if etype is str:

            def converter(x, cls=type_):
                # TODO: harmonize with other backends that use 'ascii'
                return cls(x.tobytes().decode("utf-8"))

        else:

            def converter(x, cls=type_):
                return cls(x)

    elif etype is str:

        def converter(x):
            # TODO: harmonize with other backends that use 'ascii'
            return x.tobytes().decode("utf-8")

    elif bpack.is_descriptor(type_):

        def converter(x, cls=type_):
            return cls(*x)

    else:
        converter = None

    return converter


def _encode_converter_factory(type_):
    etype = bpack.utils.effective_type(type_)
    if bpack.utils.is_enum_type(type_):
        if etype is str:

            def converter(x):
                # TODO: harmonize with other backends that use 'ascii'
                return x.value.encode("utf-8")

        elif not issubclass(type_, int):

            def converter(x):
                return x.value

    elif etype is str:

        def converter(x):
            # TODO: harmonize with other backends that use 'ascii'
            return x.encode("utf-8")

    else:
        converter = None

    # TODO: cleanup
    # elif bpack.is_descriptor(type_):
    #     # astuple works recursively so nested descriptors have been
    #     # already converted into sequences
    #     #
    #     # def converter(x):
    #     #     return bpack.astuple(x, tuple_factory=list)
    #     pass

    return converter


class Codec(bpack.codecs.Codec):
    """Numpy based codec.

    (Unicode) strings are treated as "utf-8" encoded byte strings.
    UCS4 encoded strings are not supported.
    """

    baseunits = EBaseUnits.BYTES

    def __init__(self, descriptor):
        """Initialize the codec.

        The *descriptor* parameter* is a bpack record descriptor.
        """
        super().__init__(descriptor)

        assert bpack.bitorder(descriptor) is None

        decode_converters = [
            (idx, _decode_converter_factory(field_descr.type))
            for idx, field_descr in enumerate(field_descriptors(descriptor))
        ]
        encode_converters = [
            (idx, _encode_converter_factory(field_descr.type))
            for idx, field_descr in enumerate(field_descriptors(descriptor))
        ]
        self._dtype = descriptor_to_dtype(descriptor)
        self._decode_converters = [
            (idx, func) for idx, func in decode_converters if func
        ]
        self._encode_converters = [
            (idx, func) for idx, func in encode_converters if func
        ]

    @property
    def dtype(self):
        """Return the numpy `dtype` corresponding to the `codec.descriptor`."""
        return self._dtype

    def decode(self, data: bytes, count: int = 1):
        """Decode binary data and return a record object."""
        v = np.frombuffer(data, dtype=self._dtype, count=count)
        if self._decode_converters:
            out = []
            for item in v:
                item = list(item)  # fields of the np record
                for idx, func in self._decode_converters:
                    item[idx] = func(item[idx])
                out.append(self.descriptor(*item))
        else:
            out = [self.descriptor(*item) for item in v]
        if len(v) == 1:
            out = out[0]
        return out

    def encode(self, record):
        """Encode record (Python object) into binary data."""
        # exploit the recursive behaviour of astuple
        values = bpack.astuple(record)  # , tuple_factory=list)
        values = list(values)  # nested record and sequences stay tuples
        for idx, func in self._encode_converters:
            values[idx] = func(values[idx])
        return np.array(tuple(values), dtype=self.dtype).tobytes()


codec = bpack.codecs.make_codec_decorator(Codec)
Decoder = Encoder = Codec
decoder = encoder = codec


# --- bits packing/unpacking --------------------------------------------------
class EMaskMode(enum.Enum):
    """Mask mode.

    :STANDARD:
        mask the lower nbits, e.g. 0b00001111 for nbit=4
    :COMPLEMENT:
        mask the upper bits by complementing the STANDARD mask,
        e.g. 0b11110000 for nbit=4 and dtype"unit8"
    :SINGLE_BIT:
        mask only the n-th bit (conunting form zero),
        e.g. 0b00001000 form nbit=4
    """

    STANDARD = 0
    COMPLEMENT = 1
    SINGLE_BIT = 2


def _get_item_size(bits_per_sample: int) -> int:
    """Item size of the integer type that can take requested bits."""
    if bits_per_sample > 64 or bits_per_sample < 1:
        raise ValueError(f"bits_per_sample: {bits_per_sample}")
    elif bits_per_sample <= 8:
        return 1
    else:
        return 2 ** int(np.ceil(np.log2(bits_per_sample)) - 3)


def _get_buffer_size(bits_per_sample: int) -> int:
    """Item size of the integer type that can take requested bits and shift."""
    return _get_item_size(bits_per_sample + 7)


@functools.lru_cache
def make_bitmask(
    bits_per_sample: int,
    dtype=None,
    mode: EMaskMode = EMaskMode.STANDARD,
) -> np.ndarray:
    """Return a mask for dtype according to the specified nbits and mask mode.

    .. sealso:: :class:`EMaskMode`.
    """
    mode = EMaskMode(mode)
    assert 0 < bits_per_sample <= 64
    if dtype is None:
        dtype = f"u{_get_item_size(bits_per_sample)}"

    if mode == EMaskMode.SINGLE_BIT:
        mask = 2 ** (bits_per_sample - 1) if bits_per_sample > 0 else 0
        mask = np.asarray(mask)
    else:
        shift = np.array(64 - bits_per_sample, dtype=np.uint32)
        mask = np.array(0xFFFFFFFFFFFFFFFF) >> shift
        if mode == EMaskMode.COMPLEMENT:
            mask = np.invert(mask)
    return mask.astype(dtype)


class BitUnpackParams(NamedTuple):
    samples: int
    dtype: str
    buf_itemsize: int
    buf_dtype: str
    index_map: np.ndarray
    shifts: np.ndarray
    mask: np.ndarray


@functools.lru_cache
def _unpackbits_params(
    nbits: int,
    bits_per_sample: int,
    samples_per_block: int,
    bit_offset: int,
    blockstride: int,
    signed: bool = False,
    byteorder: str = ">",
) -> BitUnpackParams:
    assert nbits >= bit_offset
    if samples_per_block is None:
        if blockstride is not None:
            raise ValueError(
                "'samples_per_block' cannot be computed automatically "
                "when 'blockstride' is provided"
            )
        samples_per_block = (nbits - bit_offset) // bits_per_sample
    blocksize = bits_per_sample * samples_per_block
    if blockstride is None:
        blockstride = blocksize
    else:
        assert blockstride >= blocksize
    nstrides = (nbits - bit_offset) // blockstride
    extrabits = nbits - bit_offset - nstrides * blockstride
    if extrabits >= blocksize:
        nblocks = nstrides + 1
        extra_samples = 0
    else:
        nblocks = nstrides
        extra_samples = extrabits // bits_per_sample
    assert nblocks >= 0
    pad = blockstride - blocksize

    sizes = [bit_offset]
    if nblocks > 0:
        sizes.extend([bits_per_sample] * (samples_per_block - 1))
        block_sizes = [bits_per_sample + pad] + [bits_per_sample] * (
            samples_per_block - 1
        )
        sizes.extend(block_sizes * (nblocks - 1))
    if extra_samples:
        sizes.append(bits_per_sample + pad)
        sizes.extend([bits_per_sample] * (extra_samples - 1))

    bit_offsets = np.cumsum(sizes)
    byte_offsets = bit_offsets // 8
    samples = len(bit_offsets)

    itemsize = _get_item_size(bits_per_sample)
    buf_itemsize = _get_buffer_size(bits_per_sample)
    dtype = f"{byteorder}{'i' if signed else 'u'}{itemsize}"
    buf_dtype = f"{byteorder}u{buf_itemsize}"

    index = np.arange(buf_itemsize) + byte_offsets[:, None]
    index = np.clip(index, 0, nbits // 8 - 1)

    mask = make_bitmask(bits_per_sample, buf_dtype)
    shifts = bit_offsets - byte_offsets * 8 + bits_per_sample
    shifts = buf_itemsize * 8 - shifts

    return BitUnpackParams(
        samples=samples,
        dtype=dtype,
        buf_itemsize=buf_itemsize,
        buf_dtype=buf_dtype,
        index_map=index,
        shifts=shifts,
        mask=mask,
    )


class ESignMode(enum.IntEnum):
    """Enumeration for sign encoding convention."""

    UNSIGNED = 0
    SIGNED = 1
    SIGN_AND_MOD = 2


def unsigned_to_signed(
    data,
    bits_per_sample: int,
    dtype=None,
    sign_mode: ESignMode = ESignMode.SIGNED,
    inplace: bool = False,
) -> np.ndarray:
    """Convert unpacked unsigned integers into signed integers.

    .. sealso:: :class:`ESignMode`.
    """
    if dtype is None:
        dtype = f"i{_get_item_size(bits_per_sample)}"

    sign_mode = ESignMode(sign_mode)

    if inplace:
        if not isinstance(data, np.ndarray):
            raise TypeError(
                f"The input 'data' ({data!r}) parameter is not a "
                "'numpy.ndarray'"
            )
        out = data
    else:
        out = np.array(data)

    out = out.astype(dtype)

    sign_mask = make_bitmask(bits_per_sample, dtype, EMaskMode.SINGLE_BIT)
    is_negative = (out & sign_mask).astype(bool)

    if sign_mode == ESignMode.SIGNED:
        cmask = make_bitmask(
            bits_per_sample - 1, dtype, mode=EMaskMode.COMPLEMENT
        )
        out[is_negative] = out[is_negative] | cmask
    elif sign_mode == ESignMode.SIGN_AND_MOD:
        mask = make_bitmask(bits_per_sample - 1, dtype)
        sign = (-1) ** is_negative
        out = sign * (out & mask)

    return out


@functools.lru_cache
def make_unsigned_to_signed_lut(
    bits_per_sample: int,
    dtype=None,
    sign_mode: ESignMode = ESignMode.SIGNED,
) -> np.ndarray:
    """Build a look-up table (LUT) for unsigned to signed integer conversion.

    .. sealso:: :class:`ESignMode`.
    """
    assert bits_per_sample <= 16
    idtype = f"u{_get_item_size(bits_per_sample)}"
    data = np.arange(2**bits_per_sample, dtype=idtype)
    return unsigned_to_signed(
        data, bits_per_sample, dtype, sign_mode, inplace=True
    )


def unpackbits(  # noqa: CCR001
    data: bytes,
    bits_per_sample: int,
    samples_per_block: int | None = None,
    bit_offset: int = 0,
    blockstride: int | None = None,
    sign_mode: ESignMode = ESignMode.UNSIGNED,
    byteorder: str = ">",
    use_lut: bool = True,
) -> np.ndarray:
    """Unpack packed (integer) values form a string of bytes.

    Takes in input a string of bytes in which (integer) samples have been
    stored using ``bits_per_sample`` bit for each sample, and returns
    the sequence of corresponding Python integers.

    Example::

                 3 bytes                            4 samples

      |------|------|------|------| --> [samp_1, samp_2, samp_3, samp_4]

      4 samples (6 bits per sample)

    :param data: bytes
        string of bytes containing the packed data
    :param bits_per_sample: int
        the number of bits used to encode each sample
    :param samples_per_block: int, optional
        the number of samples in each data block contained in the input
        string of bytes.
        This parameter is mostly relevant if the data block contains other
        information (or padding bits) in addition to the data samples.
        The number of blocks is deduced from the length of the input string
        of bytes, the number of samples per block and the number of bits
        per sample.
        If `samples_per_block` is not provided it is assumed a single block,
        and the number of samples is derived from the length of the input
        string of bytes and the number of bits per sample.
    :param bit_offset: int, optional
        the number of bits after which the sequence of samples (data blocks)
        starts (default: 0).
        It can be used e.g. to take into account of a possible binary header
        at the beginning of the sequence of samples.
    :param blockstride: int, optional
        the number of bits between the start of a data block and the start
        of the following one.
        This parameter is mostly relevant if the data block contains other
        information (or padding bits) in addition to the data samples.
        If not provided the `blockstride` is assumed to be equal to the
        size of the data block i.e. `bits_per_sample * samples_per_block`.
    :param sign_mode: ESignMode, optional
        specifies how the sign of the integer samples shall is encoded.
        Dy default unsigned samples are assumed.
        .. seealso:: :class:`ESignMode`.
    :param byteorder: str, optional
        Byte order of the encoded integers.
        Only relevant for multi byte samples.
        Default: ">" (big endian).
    :param use_lut: bool, optional
        specifies whenever the decoding of signed samples shall exploit
        look-up tables (typically faster).
        Default: True.
    """
    signed = bool(sign_mode in {ESignMode.SIGNED, ESignMode.SIGN_AND_MOD})
    if bit_offset == 0 and blockstride is None:
        if bits_per_sample == 1 and sign_mode == ESignMode.UNSIGNED:
            return np.unpackbits(np.frombuffer(data, dtype="uint8"))
        elif (
            bits_per_sample in {8, 16, 32, 64}
            and sign_mode != ESignMode.SIGN_AND_MOD
        ):
            size = bits_per_sample // 8
            kind = "i" if signed else "u"
            typestr = f"{byteorder}{kind}{size}"
            return np.frombuffer(data, dtype=np.dtype(typestr))

    nbits = len(data) * 8

    params = _unpackbits_params(
        nbits,
        bits_per_sample,
        samples_per_block,
        bit_offset,
        blockstride,
        signed,
        byteorder,
    )
    samples, dtype, buf_itemsize, buf_dtype, index_map, shifts, mask = params

    npdata = np.frombuffer(data, dtype="u1")
    buf = np.empty(samples, dtype=buf_dtype)
    bytesview = buf.view(dtype="u1").reshape(samples, buf_itemsize)
    bytesview[...] = npdata[index_map]
    outdata = ((buf >> shifts) & mask).astype(dtype)

    if sign_mode == ESignMode.UNSIGNED:
        pass
    elif sign_mode in {ESignMode.SIGNED, ESignMode.SIGN_AND_MOD}:
        if not use_lut:
            outdata = unsigned_to_signed(
                outdata, bits_per_sample, dtype, sign_mode, inplace=True
            )
        else:
            lut = make_unsigned_to_signed_lut(
                bits_per_sample, dtype, sign_mode
            )
            outdata = lut[outdata]
    else:
        raise ValueError(f"Invalid 'sign_mode' parameter: '{sign_mode}'")

    return outdata

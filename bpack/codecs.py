"""Base classes and utility functions for codecs."""

import abc
from typing import Callable, NamedTuple, Optional, Union

import bpack.utils
import bpack.descriptors

from .enums import EBaseUnits
from .descriptors import field_descriptors

__all__ = [
    "Codec",
    "Encoder",
    "Decoder",
    "has_codec",
]


CODEC_ATTR_NAME = "__bpack_decoder__"


class BaseCodec:
    """Base class for codecs, encoders and decoders."""

    baseunits: EBaseUnits

    @classmethod
    def _check_descriptor(cls, descriptor):
        if bpack.baseunits(descriptor) is not cls.baseunits:
            raise ValueError(
                f"{cls.__module__}.{cls.__name__} "
                f"only accepts descriptors with base units "
                f"'{cls.baseunits.value}'"
            )

    def __init__(self, descriptor):
        self._check_descriptor(descriptor)
        self._descriptor = descriptor

    @property
    def descriptor(self):
        """Return the descriptor associated to the codec."""
        return self._descriptor


class Decoder(BaseCodec, abc.ABC):
    """Base class for decoders."""

    @abc.abstractmethod
    def decode(self, data: bytes):
        """Decode binary data and return Python object."""
        pass


class Encoder(BaseCodec, abc.ABC):
    """Base class for encoders."""

    @abc.abstractmethod
    def encode(self, record) -> bytes:
        """Encode python objects into binary data."""
        pass


class Codec(Decoder, Encoder, abc.ABC):
    """Base class for codecs."""

    pass


CodecType = Union[Decoder, Encoder, Codec]


def make_codec_decorator(codec_type: type[CodecType]):
    """Generate a codec decorator for the input decoder class."""

    @bpack.utils.classdecorator
    def codec(cls):
        """Class decorator to add (de)coding methods to a descriptor class.

        The decorator automatically generates a *Codec* object form the
        input descriptor class and attach to it methods for conversion
        form/to bytes.
        """
        codec_ = codec_type(descriptor=cls)
        bpack.utils.set_new_attribute(cls, CODEC_ATTR_NAME, codec_)

        if isinstance(codec_, Decoder):
            bpack.utils.add_function_to_class(
                cls,
                name="frombytes",
                args=("cls", "data"),
                body=[f"return cls.{CODEC_ATTR_NAME}.decode(data)"],
                is_classmethod=True,
            )

        if isinstance(codec_, Encoder):
            bpack.utils.add_function_to_class(
                cls,
                name="tobytes",
                args=("self",),
                body=[f"return self.{CODEC_ATTR_NAME}.encode(self)"],
            )

        return cls

    return codec


def has_codec(
    descriptor, codec_type: Optional[type[CodecType]] = None
) -> bool:
    """Return True if the input descriptor has a codec attached.

    A descriptor decorated with a *codec* decorator has an attached codec
    instance and "frombytes"/"tobytes" methods (depending on the kind of
    codec).

    The *codec_type* parameter can be used to query for specific codec
    features:

    * codec_type = None: return True for any kind of codec
    * codec_type = :class:`Decoder`: return True if the attached coded has
      decoding capabilities
    * codec_type = :class:`Encoder`: return True if the attached coded has
      encoding capabilities
    * codec_type = :class:`Codec`: return True if the attached coded has
      both encoding and decoding capabilities
    """
    if hasattr(descriptor, CODEC_ATTR_NAME):
        assert isinstance(get_codec(descriptor), (Codec, Decoder, Encoder))
        if codec_type is None:
            return True
        elif issubclass(codec_type, Codec):
            return hasattr(descriptor, "frombytes") and hasattr(
                descriptor, "tobytes"
            )
        elif issubclass(codec_type, Decoder):
            return hasattr(descriptor, "frombytes")
        elif issubclass(codec_type, Encoder):
            return hasattr(descriptor, "tobytes")
    return False


def get_codec(descriptor) -> CodecType:
    """Return the codec instance attached to the input descriptor."""
    return getattr(descriptor, CODEC_ATTR_NAME, None)


# TODO: remove
def get_codec_type(descriptor) -> type[CodecType]:
    """Return the type of the codec attached to the input descriptor."""
    codec_ = getattr(descriptor, CODEC_ATTR_NAME, None)
    if codec_ is not None:
        return type(codec_)


def _get_flat_len(descriptor):
    count = 0
    for field_descr in field_descriptors(descriptor):
        if bpack.is_descriptor(field_descr.type):
            count += _get_flat_len(field_descr.type)
        elif field_descr.repeat is not None:
            count += field_descr.repeat
        else:
            count += 1
    return count


class ConverterInfo(NamedTuple):
    func: Callable
    src: Union[int, slice]
    dst: Union[int, slice]


class BaseStructCodec(Codec):
    """Base class for codecs base on struct like backends."""

    @staticmethod
    @abc.abstractmethod
    def _get_base_codec(descriptor):
        pass

    def __init__(
        self,
        descriptor,
        codec=None,
        decode_converters=None,
        encode_converters=None,
    ):
        """Initialize the BaseStructCodec.

        The *descriptor* parameter* is a bpack record descriptor.
        """
        super().__init__(descriptor)

        if codec is None:
            codec = self._get_base_codec(descriptor)
        if decode_converters is None:
            decode_converters = self._get_decode_converters(descriptor)
        if encode_converters is None:
            encode_converters = self._get_encode_converters(descriptor)

        self._codec = codec
        self._decode_converters = decode_converters
        self._encode_converters = encode_converters
        self._flat_len = _get_flat_len(descriptor)

    @property
    def format(self) -> str:  # noqa: A003
        """Return the format string."""
        return self._codec.format

    @classmethod
    def _get_decoder(cls, descr):
        assert (
            bpack.is_descriptor(descr)
            and bpack.baseunits(descr) is cls.baseunits
        )

        if has_codec(descr, Decoder):
            decoder_ = get_codec(descr)
            return decoder_

        decoder_ = cls(descr)
        return decoder_

    @staticmethod
    def _get_decode_converters_map(descriptor):
        return {}

    @classmethod
    def _get_decode_converters(cls, descriptor):
        converters_map = cls._get_decode_converters_map(descriptor)

        converters = []
        for idx, field_descr in enumerate(field_descriptors(descriptor)):
            if field_descr.type in converters_map:
                func = converters_map[field_descr.type]
                converters.append(ConverterInfo(func, idx, idx))
            elif bpack.is_descriptor(field_descr.type):
                decoder_ = cls._get_decoder(field_descr.type)
                n_items = decoder_._flat_len
                src = slice(idx, idx + n_items)
                func = decoder_._from_flat_list
                converters.append(ConverterInfo(func, src, idx))
            elif field_descr.repeat is not None:
                sequence_type = bpack.utils.sequence_type(
                    field_descr.type, error=True
                )
                src = slice(idx, idx + field_descr.repeat)
                converters.append(ConverterInfo(sequence_type, src, idx))

        return converters

    def _from_flat_list(self, values):
        for func, src, dst in self._decode_converters:
            if isinstance(src, int):
                values[dst] = func(values[src])
            else:
                value = func(values[src])
                del values[src]
                values.insert(dst, value)
        return self.descriptor(*values)

    def decode(self, data: bytes):
        """Decode binary data and return a record object."""
        values = list(self._codec.unpack(data))
        return self._from_flat_list(values)

    @classmethod
    def _get_encoder(cls, descr):
        assert (
            bpack.is_descriptor(descr)
            and bpack.baseunits(descr) is cls.baseunits
        )

        if has_codec(descr, Encoder):
            encoder_ = get_codec(descr)
            return encoder_

        encoder_ = cls(descr)
        return encoder_

    @staticmethod
    def _get_encode_converters_map(descriptor):
        return {}

    @classmethod
    def _get_encode_converters(cls, descriptor):
        converters_map = cls._get_encode_converters_map(descriptor)

        def nullop(x):
            return x

        converters = []
        for idx, field_descr in enumerate(field_descriptors(descriptor)):
            if field_descr.type in converters_map:
                func = converters_map[field_descr.type]
                converters.append(ConverterInfo(func, idx, idx))

            elif bpack.is_descriptor(field_descr.type):
                encoder_ = cls._get_encoder(field_descr.type)
                func = encoder_._to_flat_list
                slice_ = slice(idx, idx + 1)
                converters.append(ConverterInfo(func, idx, slice_))

            elif field_descr.repeat is not None:
                slice_ = slice(idx, idx + 1)
                converters.append(ConverterInfo(nullop, idx, slice_))

        return converters

    def _to_flat_list(self, record):
        values = [
            getattr(record, field.name) for field in bpack.fields(record)
        ]
        for func, src, dst in self._encode_converters[::-1]:
            values[dst] = func(values[src])

        return values

    def encode(self, record) -> bytes:
        """Encode a record object into binary data."""
        values = self._to_flat_list(record)
        return self._codec.pack(*values)

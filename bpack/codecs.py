"""Base classes and utility functions for codecs."""

import abc
from typing import Optional, Type, Union

import bpack.utils
import bpack.descriptors

from .enums import EBaseUnits
from .descriptors import field_descriptors


CODEC_ATTR_NAME = '__bpack_decoder__'


class BaseCodec:
    baseunits: EBaseUnits

    def __init__(self, descriptor):
        self._descriptor = descriptor

        if bpack.baseunits(descriptor) is not self.baseunits:
            raise ValueError(
                f'{self.__class__.__module__}.{self.__class__.__name__} '
                f'only accepts descriptors with base units '
                f'"{self.baseunits.value}"')

    @property
    def descriptor(self):
        return self._descriptor


class Decoder(BaseCodec, abc.ABC):
    @abc.abstractmethod
    def decode(self, data: bytes):
        pass


class Encoder(BaseCodec, abc.ABC):
    @abc.abstractmethod
    def encode(self, record) -> bytes:
        pass


class Codec(Decoder, Encoder, abc.ABC):
    pass


CodecType = Union[Decoder, Encoder, Codec]


def make_codec_decorator(codec_type: Type[CodecType]):
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
            decode_func = bpack.utils.create_fn(
                name='frombytes',
                args=('cls', 'data'),
                body=[f'return cls.{CODEC_ATTR_NAME}.decode(data)'],
            )
            decode_func = classmethod(decode_func)
            bpack.utils.set_new_attribute(cls, 'frombytes', decode_func)

        if isinstance(codec_, Encoder):
            encode_func = bpack.utils.create_fn(
                name='tobytes',
                args=('self',),
                body=[f'return self.{CODEC_ATTR_NAME}.encode(self)'],
            )
            bpack.utils.set_new_attribute(cls, 'tobytes', encode_func)

        return cls

    return codec


def has_codec(descriptor,
              codec_type: Optional[Type[CodecType]] = None) -> bool:
    """Return True if the input descriptor has a codec attached.

    A descriptor decorated with a *codec* decorator has an attached codec
    instance and "frombytes"/"tobytes" methods (depending on the kind of
    codec).

    The *codec_type* parameter can be used to query for specific codec
    features:

    * codec_type=None: return True for any king of codec
    * codec_type=:class:`Decoder`: return True if the attached coded has
      decoding capabilities
    * codec_type=:class:`Encoder`: return True if the attached coded has
      encoding capabilities
    * codec_type=:class:`Codec`: return True if the attached coded has
      both encoding and decoding capabilities
    """
    if hasattr(descriptor, CODEC_ATTR_NAME):
        assert isinstance(get_codec(descriptor), (Codec, Decoder, Encoder))
        if codec_type is None:
            return True
        elif issubclass(codec_type, Codec):
            return (hasattr(descriptor, 'frombytes') and
                    hasattr(descriptor, 'tobytes'))
        elif issubclass(codec_type, Decoder):
            return hasattr(descriptor, 'frombytes')
        elif issubclass(codec_type, Encoder):
            return hasattr(descriptor, 'tobytes')
    return False


def get_codec(descriptor) -> CodecType:
    """Return the codec instance attached to the input descriptor."""
    return getattr(descriptor, CODEC_ATTR_NAME, None)


def get_codec_type(descriptor) -> Type[CodecType]:
    """Return the type of the codec attached to the input descriptor."""
    codec_ = getattr(descriptor, CODEC_ATTR_NAME, None)
    if codec_ is not None:
        return type(codec_)


def get_sequence_groups(descriptor):
    """Return slices to group values belonging to sequence fields.

    If the descriptor contains sequence fields this function returns a
    list of slices that can be used to extract values belonging to
    sequence fields from a flat list of all decoded values of the
    record.

    An empty list is returned if no sequence field is present in the
    descriptor.
    """
    groups = []
    offset = 0
    for descr in field_descriptors(descriptor):
        if bpack.is_descriptor(descr.type):
            nfields = len(bpack.fields(descr.type))                     # noqa
            slice_ = slice(offset, offset + nfields)

            def to_record(values, func=descr.type):
                return func(*values)

            groups.append((to_record, slice_))
            offset += nfields
        elif descr.repeat is not None:
            sequence_type = bpack.utils.sequence_type(descr.type, error=True)
            slice_ = slice(offset, offset + descr.repeat)
            groups.append((sequence_type, slice_))
            offset += descr.repeat
        else:
            offset += 1
    return groups

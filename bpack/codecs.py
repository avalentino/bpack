"""Utility functions for codecs."""

from typing import Type

import bpack.utils
from bpack.descriptors import field_descriptors, DECODER_ATTR_NAME


def make_decoder_decorator(decoder_type):
    """Generate a decoder decorator for the input decoder class."""
    @bpack.utils.classdecorator
    def decoder(cls):
        """Class decorator to add decoding methods to a descriptor classes.

        The decorator automatically generates a :class:`Decoder` object
        form the input descriptor class and attach a "from_bytes" method
        using the decoder to the descriptor class itself.
        """
        decoder_ = decoder_type(descriptor=cls)

        bpack.utils.set_new_attribute(cls, DECODER_ATTR_NAME, decoder_)

        decode_func = bpack.utils.create_fn(
            name='decode',
            args=('cls', 'data'),
            body=[f'return cls.{DECODER_ATTR_NAME}.decode(data)'],
        )
        decode_func = classmethod(decode_func)
        bpack.utils.set_new_attribute(cls, 'from_bytes', decode_func)

        return cls

    return decoder


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


def is_decoder(descriptor) -> bool:
    """Return True if the input descriptor is also a decoder."""
    return (hasattr(descriptor, DECODER_ATTR_NAME) and
            hasattr(descriptor, 'from_bytes'))


def get_decoder(descriptor) -> Type:
    """Return the decoder instance attached to the input descriptor."""
    return getattr(descriptor, DECODER_ATTR_NAME, None)


def get_decoder_type(descriptor) -> Type:
    """Return the type of the decoder attached to the input descriptor."""
    decoder_ = getattr(descriptor, DECODER_ATTR_NAME, None)
    if decoder_ is not None:
        return type(decoder_)

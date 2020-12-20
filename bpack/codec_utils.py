"""Utility functions for codecs."""

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
        if descr.repeat is not None:
            sequence_type = bpack.utils.sequence_type(descr.type,
                                                      error=True)
            slice_ = slice(offset, offset + descr.repeat)
            groups.append((sequence_type, slice_))
            offset += descr.repeat
        else:
            offset += 1
    return groups

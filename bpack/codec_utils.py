"""Utility functions for codecs."""

import bpack.utils
from bpack.descriptors import field_descriptors


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
            sequence_type = bpack.utils.get_sequence_type(descr.type,
                                                          error=True)
            slice_ = slice(offset, offset + descr.repeat)
            groups.append((sequence_type, slice_))
            offset += descr.repeat
        else:
            offset += 1
    return groups

"""Binary data structures (un-)Packing library.

bpack provides tools to describe, in a *delcarative* way, and
encode/decode binary data.
"""

__version__ = '0.5.0'

from .descriptors import (                                          # noqa
    descriptor, field, fields, is_descriptor, is_field,
    baseunits, byteorder, bitorder, calcsize,
    EBaseUnits, EByteOrder, EBitOrder,
)

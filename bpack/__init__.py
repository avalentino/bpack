"""Binary data structures (un-)Packing library.

bpack provides tools to describe, in a *declarative* way, and
encode/decode binary data.
"""

from .descriptors import (                                              # noqa
    descriptor, field, fields, is_descriptor, is_field,
    baseunits, byteorder, bitorder, calcsize,
)
from .enums import EBaseUnits, EByteOrder, EBitOrder                    # noqa


__version__ = '0.6.0.dev2'

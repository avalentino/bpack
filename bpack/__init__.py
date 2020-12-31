"""Binary data structures (un-)Packing library.

bpack provides tools to describe, in a *declarative* way, and
encode/decode binary data.
"""

__version__ = '0.6.0.dev0'

from .descriptors import (                                          # noqa
    descriptor, field, fields, is_descriptor, is_field,
    baseunits, byteorder, bitorder, calcsize,
)
from .utils import EBaseUnits, EByteOrder, EBitOrder                # noqa

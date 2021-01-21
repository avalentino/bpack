"""Binary data structures (un-)Packing library.

bpack provides tools to describe, in a *declarative* way, and
encode/decode binary data.
"""

from .descriptors import (                                      # noqa: F401
    descriptor, field, fields, asdict, is_descriptor, is_field,
    baseunits, byteorder, bitorder, calcsize,
)
from .enums import EBaseUnits, EByteOrder, EBitOrder            # noqa: F401
from .typing import T                                           # noqa: F401


__version__ = '0.7.0'

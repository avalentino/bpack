"""Binary data structures (un-)Packing library.

bpack provides tools to describe, in a *declarative* way, and
encode/decode binary data.
"""

from .enums import EBaseUnits, EByteOrder, EBitOrder  # noqa: F401
from .typing import T  # noqa: F401
from .descriptors import (  # noqa: F401
    descriptor,
    field,
    fields,
    asdict,
    astuple,
    is_descriptor,
    is_field,
    baseunits,
    byteorder,
    bitorder,
    calcsize,
)

__version__ = "1.1.0.dev0"

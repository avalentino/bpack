"""Enumeration types for the bpack package."""

import sys
import enum


class EBaseUnits(enum.Enum):
    """Base units used to specify size and offset parameters in descriptors."""

    BITS = 'bits'
    BYTES = 'bytes'


class EByteOrder(enum.Enum):
    """Enumeration for byte order (endianess).

    .. note::

        the :data:`EByteOrder.DEFAULT` is equivalent to
        :data:`EByteOrder.NATIVE` for binary structures having
        :data:`EBaseUnits.BYTE` base units, and :data:`EByteOrder.BIG`
        for binary structures having :data:`EBaseUnits.BIT` base units.
    """

    BIG = '>'
    LITTLE = '<'
    NATIVE = '='
    DEFAULT = ''

    @classmethod
    def get_native(cls):
        if sys.byteorder == 'little':
            return cls.LITTLE
        else:
            return cls.BIG


class EBitOrder(enum.Enum):
    """Enumeration for bit order."""

    MSB = '>'
    LSB = '<'
    DEFAULT = ''

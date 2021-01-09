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
        :data:`EBaseUnits.BYTE` base units, and :data:`EByteOrder.BE`
        for binary structures having :data:`EBaseUnits.BIT` base units.
    """

    BE = '>'
    LE = '<'
    NATIVE = '='
    DEFAULT = ''

    @classmethod
    def get_native(cls):
        return cls.LE if sys.byteorder == 'little' else cls.BE


class EBitOrder(enum.Enum):
    """Enumeration for bit order."""

    MSB = '>'
    LSB = '<'
    DEFAULT = ''

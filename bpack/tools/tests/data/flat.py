import bpack
from bpack import EBaseUnits, T
from bpack.enums import EByteOrder


@bpack.descriptor(baseunits=EBaseUnits.BITS)
class Flat:
    """Docstring."""

    magic: T["u24"] = b"abc"
    count: T["u8"] = 0
    byteorder: T["S8"] = EByteOrder.NATIVE
    field_a_1: T["u3"] = 0
    field_a_2: T["i5"] = 0
    field_a_3: T["f16"] = 0.0
    field_b_1: T["f16"] = 1.1
    field_b_2: T["u5"] = 1
    field_b_3: T["u3"] = 2

    # === Header ===
    def header_method(self):
        pass

    # === TypeA ===
    def type_a_method(self):
        pass

    # === TypeB ===
    def type_b_method(self):
        pass

    # === Nested ===
    def nested_method(self):
        pass

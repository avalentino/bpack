import bpack
from bpack import EBaseUnits, T
from bpack.enums import EByteOrder


@bpack.descriptor(baseunits=EBaseUnits.BITS)
class Header:
    magic: T["u24"] = b"abc"
    count: T["u8"] = 0
    byteorder: T["S8"] = EByteOrder.NATIVE

    def header_method(self):
        pass


@bpack.descriptor(baseunits=EBaseUnits.BITS)
class TypeA:
    field_a_1: T["u3"] = 0
    field_a_2: T["i5"] = 0
    field_a_3: T["f16"] = 0.0

    def type_a_method(self):
        pass


@bpack.descriptor(baseunits=EBaseUnits.BITS)
class TypeB:
    field_b_1: T["f16"] = 1.1
    field_b_2: T["u5"] = 1
    field_b_3: T["u3"] = 2

    def type_b_method(self):
        pass


@bpack.descriptor(baseunits=EBaseUnits.BITS)
class Nested:
    """Docstring."""

    header: Header = bpack.field(default_factory=Header)
    field_1: TypeA = bpack.field(default_factory=TypeB)
    field_2: TypeB = bpack.field(default_factory=TypeB)

    def nested_method(self):
        pass

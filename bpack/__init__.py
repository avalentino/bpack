"""Binary data structures (un-)packing library.

The bpack Python package provides tools to describe and encode/decode
binary data.

Binary data are assumed to be organised in *records*, each composed by a
sequence of fields. Fields are characterised by a known size, offset
(w.r.t. the beginning of the record) and datatype. Records can be nested::

  |------------------------------ Record ------------------------------|
  |-- Field-1 --|---- Field-2 ----|------- Field-3 (sub-record) -------|
        (4)             (8)       |-- Field 3.1 --|---- Field-3.2 -----|
                                        (4)               (12)

The package provides classes and functions that can be used to:

* create binary data descriptors in a declarative way (structures can
  be specified up to the bit level)
* automatically generate encoders/decoders for a specified data descriptor

Encoders/decoders rely on well known Python packages like:

* struct (form the standard library)
* numpy (optional)
* bitstruct (optional)
* bitarray (optional)

Currently only fixed size records are supported.
"""

__version__ = '0.1.0.dev1'

from .descriptors import (                                          # noqa
    descriptor, field, fields, is_descriptor, is_field,
    baseunits, byteorder, bitorder, calcsize,
    EBaseUnits, EByteOrder, EBitOrder,
)

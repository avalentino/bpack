"""bpack: binary data packing and unpacking.

The bpack package provides support tools for describing and encoding/decoding
binary data.

Binary data are assumed to be organized in *records*, each composed by a
sequence of fields characterized by a known size, offset (w.r.t. the
beginning of the record) and datatype. Records can be nested.

  |------------------------------ Record ------------------------------|
  |-- Field-1 --|---- Field-2 ----|------- Field-3 (sub-record) -------|
        (4)             (8)       |-- Field 3.1 --|---- Field-3.2 -----|
                                        (4)               (12)

The package provides support tools to:

* create binary data descriptors in a declarative way (up to the bit level)
* automatically generate encoders/decoders for a specified data descriptor

Encoders/decoders rely on well known Python packages like:

* struct (form the standard library)
* numpy
* bitstruct
* bitarray (optional)

Limitations: currently only fixed size records are supported.
"""

__version__ = '1.0.0.dev0'

from .descriptors import *

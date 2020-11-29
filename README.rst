bpack - Binary data structures (un-)packing library
===================================================

:HomePage:  https://github.com/avalentino/bpack
:Author:    Antonio Valentino
:Contact:   antonio.valentino@tiscali.it
:Copyright: 2020, Antonio Valentino <antonio.valentino@tiscali.it>
:Version:   0.1.0

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

* struct_ (form the standard library)
* numpy_ (optional)
* bitstruct_ (optional)
* bitarray_ (optional)

Currently only fixed size records are supported.

.. _struct: https://docs.python.org/3/library/struct.html
.. _numpy: https://numpy.org
.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray

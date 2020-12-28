===========================================
Binary data structures (un-)Packing library
===========================================

:HomePage:  https://github.com/avalentino/bpack
:Author:    Antonio Valentino
:Contact:   antonio.valentino@tiscali.it
:Copyright: 2020, Antonio Valentino <antonio.valentino@tiscali.it>
:Version:   0.5.0

.. description

The *bpack* Python package provides tools to describe and encode/decode
binary data.

Binary data are assumed to be organised in *records*, each composed by a
sequence of fields. Fields are characterised by a known size, offset
(w.r.t. the beginning of the record) and datatype.

The package provides classes and functions that can be used to:

* create binary data descriptors in a declarative way (structures can
  be specified up to the bit level)
* automatically generate encoders/decoders for a specified data descriptor

Encoders/decoders rely on well known Python packages like:

* struct_ (form the standard library)
* bitstruct_ (optional)
* bitarray_ (optional)
* numpy_ (optional) - **TODO**

Currently only fixed size records are supported.

.. _struct: https://docs.python.org/3/library/struct.html
.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray
.. _numpy: https://numpy.org

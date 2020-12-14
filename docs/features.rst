Features
========

* declarative data description for binary data structures
* description of binary data structures at *bit* level
* data decoding (of byte and bit based structures)
* backend:

  - **st** backend based on the standard Python library :mod:`struct` module
  - **ba** backend based on bitarray_ (only included for benchmarking purposes)
  - **bs** backend based on bitstruct_

* support for signed integer types
* support for :class:`enum.Enum` types
* both bit and byte order can be specified by the user
* comprehensive test suite

.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray


Limitations
-----------

* only fixed size binary records are supported by design, the size of the
  record shall be known at the moment of the record descriptor definition.
  It is should be easy for the user to leverage tools provided by the *bpack*
  Python package to support more complex decoding scenarios.
* currently it is assumed that all fields in a binary record share the
  same bit/byte order. The management of different byte order in the same
  binary record is, in principle, possible but not planned at the moment.


Possible additional features still not implemented
--------------------------------------------------

* support for list fields (including list length specification)
* record nesting (the field of a descriptor cna be another descriptor)
* numpy based backend
* automatic size determination for data type
* user defined converters
* extended type specification based typing
* possibility to specify data types using string specifiers with
  the native backend syntax (struct, bitstruct, numpy, ...)
* support for data encoding (packing)


Miscellanea *To Do* list
------------------------

* improve documentation
* benchmarks

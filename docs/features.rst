Features
========

* declarative data description for binary data structures
* description of binary data structures at *bit* level
* data decoding (byte and bit based structures)
* backend:

  - **st** backend based on the standard Python library :mod:`struct` module
  - **ba** backend based on bitarray_
  - **bs** backend based on bitstruct_


.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray


Limitations
-----------

* only fixed size binary records are supported by design, the size of the
  record shall be known at the moment of the record descriptor definition.
  It is should be easy for the user to leverage tools provided by the *bpack*
  Python package to support more complex decoding scenarios.
* currently it is assumed that all fields in a binary record share the
  same byte order. The management of different byte order in the same
  binary record is, in principle, possible but not planned at the moment.
* currently it is not possible to specify the bit order.


Possible additional features still not implemented
--------------------------------------------------

* support for signed/unsigned integer specification
* support byte order specification at descriptor level
  (and at field level TBD)
* support for bit order specification (TBD)
* support for list fields (including list length specification)
* record nesting (the field of a descriptor cna be another descriptor)
* support for enums
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
* CI
* coverage testing
* benchmarks

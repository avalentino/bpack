Features
========

* basic support for declarative data description for binary data structures
* basic support for description of binary data structures at *bit* level
* basic decoding infrastructure (byte and bit based structures)
* backend:

  - **st** backend based on the standard Python library :mod:`struct` module
  - **ba** backend based on bitarray_
  - **bs** backend based on bitstruct_


.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray


Possible additional features still not implemented
--------------------------------------------------

* record nesting (the field of a descriptor cna be another descriptor)
* support for enums
* support for signed/unsigned integer specification
* support for list fields (including list length specification)
* numpy based backend
* automatic size determination for data type
* support for *units* specification in fields descriptors
* support for *doc* description in fields descriptors
* support bit/byte order specification at descriptor level and at field level
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

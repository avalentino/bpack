Features
========

* declarative description of binary data structures
* specification of data structures up to *bit* level
* automatic codec generation form data descriptors
* data decoding
* backend:

  - **st** backend based on the standard Python library :mod:`struct` module
  - **bs** backend based on bitstruct_
  - **ba** backend based on bitarray_ (only included for benchmarking purposes)

* support for signed/unsigned integer types
* support for :class:`enum.Enum` types
* support for sequence types, i.e. fields with multiple (homogeneous) items
* both bit and byte order can be specified by the user
* automatic size determination for some data types
* record nesting (the field in a record descriptor can be another record)
* comprehensive test suite

.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray


Limitations
-----------

* only fixed size binary records are supported by design, the size of the
  record shall be known at the moment of the record descriptor definition.
  It should be easy for the user to leverage tools provided by the *bpack*
  Python package to support more complex decoding scenarios.
* currently it is assumed that all fields in a binary record share the
  same bit/byte order. The management of different byte order in the same
  binary record is, in principle, possible but not planned at the moment.
* record nesting is only possible for records having the same base-units,
  bits or bytes, and compatible decoder types eventually.


Possible additional features still not implemented
--------------------------------------------------

* numpy based backend
* possibility to specify data types using string specifiers with
  the native backend syntax (struct, bitstruct, numpy, ...)
* data encoding (packing)
* user defined converters


Miscellanea *To Do* list
------------------------

* improve documentation
* benchmarks

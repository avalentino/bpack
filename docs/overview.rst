Overview
========

What is bpack?
--------------

.. include:: ../README.rst
   :start-after: .. description
   :end-before: .. local-definitions

.. |struct| replace:: :mod:`struct`


Features
--------

* declarative description of binary data structures
* specification of data structures up to *bit* level
* automatic codec generation form data descriptors
* data decoding
* backend:

  - :mod:`bpack.st` backend based on the :mod:`struct` module of
    standard Python_ library
  - :mod:`bpack.bs` backend based on bitstruct_
  - :mod:`bpack.np` backend based on numpy_
  - :mod:`bpack.ba` backend based on bitarray_
    (only included for benchmarking purposes)

* support for signed/unsigned integer types
* support for :class:`enum.Enum` types
* support for sequence types, i.e. fields with multiple (homogeneous) items
* both bit and byte order can be specified by the user
* automatic size determination for some data types
* record nesting (the field in a record descriptor can be another record)
* possibility to specify data types using the special type annotation class
  :class:`bpack.typing.T` that accepts annotations and string specifiers
  compatible with the numpy_ "Array Interface" and ``dtype``
* comprehensive test suite


.. _limitations-label:

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
* Sequence types can only contain basic numeric types; nested sequences,
  sequences of enums or sequences of records are not allowed at the moment.


Possible additional features still not implemented
--------------------------------------------------

* data encoding (packing)
* user defined converters
* support for complex and datetime data types


.. _Python: https://www.python.org
.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _numpy: https://numpy.org
.. _bitarray: https://github.com/ilanschnell/bitarray

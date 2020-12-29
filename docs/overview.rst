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
  - :mod:`bpack.ba` backend based on bitarray_
    (only included for benchmarking purposes)

* support for signed/unsigned integer types
* support for :class:`enum.Enum` types
* support for sequence types, i.e. fields with multiple (homogeneous) items
* both bit and byte order can be specified by the user
* automatic size determination for some data types
* record nesting (the field in a record descriptor can be another record)
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


Possible additional features still not implemented
--------------------------------------------------

* numpy based backend
* possibility to specify data types using string specifiers with
  the native backend syntax (:mod:`struct`, bitstruct_, numpy_, ...)
* data encoding (packing)
* user defined converters


.. only:: never

    Miscellanea *To Do* list
    ------------------------

    * improve documentation
    * benchmarks
    * include :func:`dataclasses.dataclass` generation in
      :func:`bpack.descriptors.descriptor` (the use should not explicitly use
      :mod:`dataclasses`)
    * drop :func:`bpack.descriptors.descriptor` objects ``__len__`` method
      (always use :func:`bpack.descriptros.calcsize`)
    * :class:`EBaseUnits` shall become a :class:`IntFlag` to allow the
      *decoders* to declare baseunits as followd::

        basunits = bpack.EBaseUnits.BITS | bpack.EBaseUnits.BYTES


.. _Python: https://www.python.org
.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray
.. _numpy: https://numpy.org

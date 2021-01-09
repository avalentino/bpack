User Guide
==========

Core concepts
-------------

*bpack* is a lightweight Python package intended to help users to

* describe binary data structures
* encode/decode binary data to/form Python object

.. note::

   Currently the encoding feature is still not implemented,
   see also :doc:`overview`.


Descriptors
~~~~~~~~~~~

The user can define binary data structure in a declarative way, as follows:

.. testcode::

   import bpack

   @bpack.descriptor
   class BinaryRecord:
       field_1: int = bpack.field(size=4, signed=True)
       field_2: float = bpack.field(size=8)

Key concepts for definition of binary data structures are

* the declaration of the data structure by means of the
  :func:`bpack.descriptors.descriptor` class decorator.
  It allows to specify the main properties of the data structure.
* the specification of the characteristics of each field, mainly the data
  type, the size and (optionally) the offset with respect to the beginning
  of the record. This can be done using the :func:`bpack.descriptors.field`
  factory function.

In the above example the ``BinaryRecord`` has been defined to have two fields:

:field_1:
    a 32bit signed integer (``size`` is expressed in bytes in this case)
:field_2:
    a double precision floating point (8 bytes)

The offset of the fields have not been explicitly specified so they are
computed automatically.

In the example ``field_1`` has ``offset=0``, while ``offset=4`` has
``offset=4`` i.e. data belonging to ``field_2`` immediately follow the ones
of the previous field.

The design is strongly inspired to the one of the :mod:`dataclasses` package
of the Python standard library.


Decoders
~~~~~~~~

Once a binary structure is defined, the *bpack* package allows to
automatically generate :class:`Decoder` objects that are able
to convert binary data into a Python objects:

.. testcode::

   import bpack.st

   decoder = bpack.st.Decoder(BinaryRecord)
   record = decoder.decode(b'\x15\xcd[\x07\x00\x00\x00\x00\x18-DT\xfb!\t@')

   assert record.field_1 == 123456789
   assert record.field_2 == 3.141592653589793

   print(record)

.. testoutput::

   BinaryRecord(field_1=123456789, field_2=3.141592653589793)


In the example above it has been used the :class:`bpack.st.Decoder` class
form the :mod:`bpack.st` module.

Please note that the decoder class (:class:`bpack.st.Decoder`)

* takes in input the *descriptor* (i.e. the type) of the binary data
  structure, and
* return a *decoder* object which is capable to decode only binary data
  organized according to the *descriptor* received at the instantiation
  time. If one need to decode a differed data structure than it is necessary
  to instantiate a different decoder.

The :mod:`bpack.st` module used in the example is just one of the, so called,
*backends* available in *bpack*.

See the Backends_ section below for more details.


Binary data structures declaration
----------------------------------

As anticipated above the declaration of a binary data structure and
its main properties is done using the :func:`bpack.descriptors.descriptor`
class decorator.


Bit vs byte structures
~~~~~~~~~~~~~~~~~~~~~~

One of the properties that the :func:`bpack.descriptors.descriptor`
class decorator allows to specify if the structure itself is described
in terms of *bytes* or in terms of *bits*, i.e. if field size and offsets
have to be intended as number of bytes of as number of bits.

This property is called *baseunits*.

This is an important distinction for two reasons:

* it is fundamental for *decoders* (see below) to know much data have to be
  converted and where this data are exactly located in a string of bytes
* not all *backends* are capable of decoding both kinds of structures

In addition nested data structures (see `Record nesting`_), in principle,
could be described using different *baseunits*.

.. note::

   Currently available *backends* do not support nested data structures
   described using different *baseunits* (see :ref:`limitations-label`).
   Anyway it is in the plans to overcome this limitation.

*Baseunits* can be specified as follows:

.. testcode::

   @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
   class BitRecord:
       field_1: bool = bpack.field(size=1)
       field_2: int = bpack.field(size=3)
       field_3: int = bpack.field(size=4)


The `baseunits` parameter has been specified for the
:func:`bpack.descriptors.descriptor` class decorator and its value can
be one the possible values of the :class:`bpack.enums.EBaseUnits`
:class:`enum.Enum`:

* :data:`bpack.enums.EBaseUnits.BITS`, or
* :data:`bpack.enums.EBaseUnits.BYTES`

If the ``baseunits`` parameter is not specified than it is assumed to be
equal to :data:`bpack.enums.EBaseUnits.BYTES` by default.

Please note that the entire data structure of the above example is only
8 bits (1 byte) large.


Specifying bit/byte order
~~~~~~~~~~~~~~~~~~~~~~~~~

TBW

.. byteorder: Union[str, EByteOrder] = EByteOrder.DEFAULT,
.. bitorder: Optional[Union[str, EBitOrder]] = None,
.. size: Optional[int] = None,


Fields specification
--------------------

Type
~~~~

TBW


Size
~~~~

TBW

Automatic size computation.


Offset
~~~~~~

TBW

Automatic offset computation


Signed integer types
~~~~~~~~~~~~~~~~~~~~

TBW


Enumeration fields
------------------

TBW


Record nesting
--------------

TBW


Data decoders
-------------

Backends
~~~~~~~~

Backends provide encoding/decoding capabilities for binary data
*descriptors* exploiting external packages to do the low level job.

Currently *bpack* provides the:

* :mod:`bpack.st` backend, based on the :mod:`struct` package, and
* :mod:`bpack.bs` backend, based on the bitstruct_ package to decode
  binary data described at bit level, i.e. with fields that can have size
  expressed in terms of number of bits (also smaller that 8).

Additionally a :mod:`bpack.ba` backend, feature incomplete, is also provided
mainly for benchmarking purposes. The :mod:`bpack.ba` backend is based on the
bitarray_ package.

Finally it is planned a :mod:`bpack.np` backend based on numpy_.


.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray
.. _numpy: https://numpy.org


Automatic generation of decoders
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TBW


Decoder decorator
~~~~~~~~~~~~~~~~~

TBW

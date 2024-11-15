User Guide
==========

Core concepts
-------------

*bpack* is a lightweight Python package intended to help users to

* describe binary data structures
* encode/decode binary data to/from Python object


Descriptors
~~~~~~~~~~~

The user can define binary data structure in a declarative way, as follows:

.. testcode::

   import bpack

   @bpack.descriptor
   class BinaryRecord:
       field_1: float = bpack.field(size=8)
       field_2: int = bpack.field(size=4, signed=True)

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
    a double precision floating point (8 bytes)
:field_2:
    a 32bit signed integer (4 bytes)

``size`` is expressed in bytes in this case.

The offset of the fields have not been explicitly specified so they are
computed automatically.

In the example ``field_1`` has ``offset=0``, while ``field_2`` has
``offset=8`` i.e. data belonging to ``field_2`` immediately follow the ones
of the previous field.

The design is strongly inspired to the one of the :mod:`dataclasses` package
of the Python standard library.


Codecs
~~~~~~

Once a binary structure is defined, the *bpack* package allows to
automatically generate :class:`Codec` objects that are able
to convert binary data into a Python objects and vice versa:

.. testcode::

   import bpack.st

   binary_data = b"\x18-DT\xfb!\t@\x15\xcd[\x07"

   codec = bpack.st.Codec(BinaryRecord)
   record = codec.decode(binary_data)

   assert record.field_1 == 3.141592653589793
   assert record.field_2 == 123456789

   print(record)

.. testoutput::

   BinaryRecord(field_1=3.141592653589793, field_2=123456789)

.. testcode::

    encoded_data = codec.encode(record)
    assert binary_data == encoded_data

    print("binary_data: ", binary_data)
    print("encoded_data:", encoded_data)

.. testoutput::

    binary_data:  b'\x18-DT\xfb!\t@\x15\xcd[\x07'
    encoded_data: b'\x18-DT\xfb!\t@\x15\xcd[\x07'

In the example above it has been used the :class:`bpack.st.Codec` class
from the :mod:`bpack.st` module.

Please note that the decoder class (:class:`bpack.st.Codec`)

* takes in input the *descriptor* (i.e. the type) of the binary data
  structure, and
* return a *codec* object which is capable to encode/decode only binary data
  organized according to the *descriptor* received at the instantiation
  time. If one need to encode/decode a differed data structure than it is
  necessary to instantiate a different codec.

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
class decorator allows to specify is *baseunits*.
It allows to specify the elementary units used to describe the binary
structure itself.
A structure can be described in terms of *bytes* or in terms of *bits*,
i.e. if field size and offsets have to be intended as number of bytes of
as number of bits.

This is an important distinction for two reasons:

* it is fundamental for *decoders* (see below) to know much data have to be
  converted and where this data are exactly located in a string of bytes
* not all *backends* are capable of decoding both kinds of structures

.. note::

   Currently available *backends* do not support nested data structures
   (see `Record nesting`_) described using different *baseunits*
   (see :ref:`Limitations`).

*Baseunits* can be specified as follows:

.. testcode::

   @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
   class BitRecord:
       field_1: bool = bpack.field(size=1)
       field_2: int = bpack.field(size=3)
       field_3: int = bpack.field(size=4)


The ``baseunits`` parameter has been specified as a parameter of the
:func:`bpack.descriptors.descriptor` class decorator and its possible values
are enumerated by the :class:`bpack.enums.EBaseUnits` :class:`enum.Enum`:

* :data:`bpack.enums.EBaseUnits.BITS`, or
* :data:`bpack.enums.EBaseUnits.BYTES`

If the ``baseunits`` parameter is not specified than it is assumed to be
equal to :data:`bpack.enums.EBaseUnits.BYTES` by default.

Please note that the entire data structure of the above example is only
8 bits (1 byte) large.

.. note::

   Please note that *baseunits* and many of the function and method parameters
   whose valued is supposed to be an :class:`enum.Enum` can also accept a
   string value.
   E.g. the above example can also be written as follows:

   .. testcode::

      @bpack.descriptor(baseunits="bits")
      class BitRecord:
          field_1: bool = bpack.field(size=1)
          field_2: int = bpack.field(size=3)
          field_3: int = bpack.field(size=4)

   Please refer to the specific enum documentation (in this case
   :class:`bpack.enums.EBaseUnits`) to know which are string values
   corresponding to the desired enumerated value.


Specifying bit/byte order
~~~~~~~~~~~~~~~~~~~~~~~~~

Other important parameters for the :func:`bpack.descriptors.descriptor`
class decorator are:

:byteorder:
    whose possible values are described by :class:`bpack.enums.EByteOrder`.
    By the fault the native byte order is assumed.
:bitorder:
    whose possible values are described by :class:`bpack.enums.EBitOrder`.
    The *bitorder* parameter shall always be set to ``None`` the if
    *baseunits* value is :data:`bpack.enums.EBaseUnits.BYTES`.

Both this parameters describe the internal organization of binary data
of each field.


Descriptor size
~~~~~~~~~~~~~~~

The :func:`bpack.descriptors.descriptor` class decorator also allows to
specify *explicitly* the overall size of the binary data structure:

.. testcode::

   @bpack.descriptor(baseunits="bits", size=8)
   class BinaryRecord:
       field_1: bool = bpack.field(size=1)
       field_2: int = bpack.field(size=3)

In this case the the overall size of ``BitRecord`` is 8 bits (1 bytes)

.. doctest::

   >>> bpack.calcsize(BinaryRecord)
   8

even if the sum of sizes of all fields is only 4 bits.

Usually explicitly specifying the *size* of a binary data structure is not
necessary because the *bpack* is able to compute it automatically by looking
at the size of fields.

In some cases, anyway, it can be useful to specify it, e.g. when one want to
use a descriptor like the one defined in the above example as field of
a larger descriptor (see `Record nesting`_).
In this case it is important tho know the correct size of each field in
order to be able to automatically compute the *offset* of the following
ones.


Fields specification
--------------------

As anticipated in the previous section there are three main elements that
the *bpack* package need to know about fields in order to have a complete
description of a binary data structure:

* the field data **type**,
* the field **size** (expressed in *baseunits*,
  see `Bit vs byte structures`_), and
* the field **offset** with respect to the beginning of the binary data
  structure (also in this case expressed in *baseunits*,
  see `Bit vs byte structures`_)

.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field: int = bpack.field(size=4, offset=0)

Please note, anyway, that in some case it is possible to infer some of the
above information from the context so it is not always necessary to specify
all of them explicitly. More details will be provided in the following.

As shown in the example above the main way to specify a field descriptor is
to use the :func:`bpack.descriptors.field` factory function together with
Python type annotations to specify the data type.


Type
~~~~

The data type of a field is the only parameter that is always mandatory,
and also it is the only parameter that is not specified by means of the
:func:`bpack.descriptors.field` factory function.
Rather it is specified using the standard Python syntax for type annotations.

Currently supported data types are:

:basic types:
    basic Python types like ``bool``, ``int``, ``float``, ``bytes``, ``str``
    (``complex`` is not supported currently)
:enums:
    enumeration types defined using the :mod:`enum` module of the standard
    Python library.
    Please refer to the `Enumeration fields`_ section for more details about
    features and limitations
:sequences:
    used to define fields containing a sequence of homogeneous values
    (i.e. values having the same data type). A *sequence* data type in *bpack*
    can be defined using the standard type annotations classes like
    :class:`typing.Sequence` or :class:`typing.List`, or directly `list[...]`.
    Please refer to the `Sequence fields`_ section for more details about
    features and limitations
:descriptors:
    i.e. any binary data structure defined using the
    :func:`bpack.descriptors.descriptor` class decorator
    (see also `Record nesting`_)
:type annotations:
    annotated data types defined by means of the :class:`bpack.typing.T`
    type annotation. Please refer to the `Special type annotations`_ section
    for a more detailed description

.. note::

   The ``str`` type in Python is used to represent unicode strings.
   The conversion of this kind of strings from/to binary format requires
   some form of decoding/encoding.
   *Bpack* codecs (see `Data codecs`_) convert ``str`` data from/to
   ``bytes`` strings using the "UTF-8" encoding.

   Please note that the *size* of a ``str`` field still describes the
   number of bits/bytes in its binary representation, not the length
   of the string (which in principle could require a number of bytes
   larger that the number of characters).


Size
~~~~

The field *size* is specified as a positive integer in *baseunits*
(see the `Bit vs byte structures`_ section).

It is a fundamental information and it must be always specified by means
of the :func:`bpack.descriptors.field` factory function unless it is
absolutely clear and unambiguous how to determine the fields size from
the data type.

This is only possible in the following cases:

* the data type is ``bool`` in which case the size is assumed to be ``1``
  (at the moment no other basic type has a default size associated)
* the data type is a record descriptor, in which case the field size is
  computed as follows:

  .. testcode::

     bpack.calcsize(BinaryRecord, units=bpack.baseunits(BinaryRecord))

* the data type is specified using special type annotations also including
  size information:

  .. testcode::

     from bpack import T

     @bpack.descriptor
     class BinaryRecord:
         field: T["u3"]

  The ``T["u3"]`` type annotation specifier defines an unsigned integer type
  (``u``) having size 3 (for the specific example this means 3 bytes).
  Please refer to the `Special type annotations`_ section for more details.

Please note that the size of the field must not necessarily correspond to
the size of one of the data types supported by the platform.
In the example above it has been specified a type ``T["u3"]`` which
corresponds to a 24 bits unsigned integer. It is represented using a standard
Python ``int`` in the Python code but the binary representation will always
take only 3 bytes.


Offset
~~~~~~

The field *offset* is specified as a not-negative integer in *baseunits*
(see the `Bit vs byte structures`_ section), and it represent the amount
of *baseunits* from the beginning of the record to the beginning of the field.

It is a fundamental information and it can be specified by means of the
:func:`bpack.descriptors.field` factory function.

The *bpack* package, anyway, implements a mechanism to automatically compute
the field offset exploiting information of the other fields in the record.
For this reason it is necessary to specify the field *offset* explicitly only
in very specific cases.

For example the *verbose* definition of a record with 5 integer fields
looks like the following:

.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field_1: int = bpack.field(size=4, offset=0)
       field_2: int = bpack.field(size=4, offset=4)
       field_3: int = bpack.field(size=4, offset=8)
       field_4: int = bpack.field(size=4, offset=12)
       field_5: int = bpack.field(size=4, offset=16)

If not specified, the offset of the first field is assumed to be ``0``,
and the offset of the following fields is assumed to be equal to the
offset of the previous field plus the size of the previous field itself::

   field[n].offset = field[n - 1].offset + field[n - 1].size

In short the automatic offset computation works assuming that all fields
are stored contiguously and without holes.

.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field_1: int = bpack.field(size=4)  # offset = 0 first field
       field_2: int = bpack.field(size=4)  # offset = 4
                                           # field_1.offset + field_1.size
       field_3: int = bpack.field(size=4)  # offset = 8
                                           # field_2.offset + field_2.size
       field_4: int = bpack.field(size=4)  # offset = 12
                                           # field_3.offset + field_3.size
       field_5: int = bpack.field(size=4)  # offset = 16
                                           # field_4.offset + field_4.size

Now suppose that the user is not interested in the field n. 2 and wants to
remove it from the descriptor. This creates a *gap* in the binary data
which makes not possible to exploit the automatic offset computation
mechanism:

.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field_1: int = bpack.field(size=4)    # offset = 0 first field
       # field_2: int = bpack.field(size=4)
       field_3: int = bpack.field(size=4)    # offset = 4 != 8   NOT CORRECT
       field_4: int = bpack.field(size=4)    # offset = 8 != 12  NOT CORRECT
       field_5: int = bpack.field(size=4)    # offset = 12 != 16 NOT CORRECT

The automatic computation of the offset fails, in this case, because of the
missing information about ``field_2``.
Indeed, since ``field_2`` has not been specified, for the computation of
the offset of ``field_3`` *bpack* assumes that the previous field is
``field_1`` and performs the computation accordingly::

   field_3.offest = fielf_1.offset + field_i.size == 4 != 8  # INCORRECT

The incorrect offset of ``field_3`` causes the incorrect computation of the
offset all the fields that follow.

One option to recover the correct behavior (without falling back to the
*verbose* description shown at the beginning of the section) is to specify
explicitly **only** the offset of the first field after the gap:

.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field_1: int = bpack.field(size=4)    # offset = 0 first field
       # field_2: int = bpack.field(size=4)
       field_3: int = bpack.field(size=4, offset=8)
       field_4: int = bpack.field(size=4)    # offset = 12
       field_5: int = bpack.field(size=4)    # offset = 16

In this way the correct offset can be computed automatically for all fields
but the one(s) immediately following a *gap* in the data descriptor.


Signed integer types
~~~~~~~~~~~~~~~~~~~~

Only for integer types, it is possible to specify if the integer value is
*signed* or not.
Although this distinction is not relevant in the Python code, it is necessary
to have this information when data have to be stored in binary form.

.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field: int = bpack.field(size=4, offset=0, signed=True)

If *signed* is not specified for a field having an integer type, then it
is assumed to be ``False`` (*unsigned*).

The *signed* parameter is ignored if the data type is not ``int``.


Default values
~~~~~~~~~~~~~~

The :func:`bpack.descriptors.field` factory function also allows to specify
default values using the ``default`` parameter:

.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field: int = bpack.field(size=4, default=0)

This allows to instantiate the record without specifying the value of each
field:

.. doctest::

   >>> BinaryRecord()
   BinaryRecord(field=0)

In cases in which the :func:`bpack.descriptors.field` factory function
is not used for field definition, the default value can be specified by
direct assignment:

.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field_1: bool = False
       field_2: bpack.T["i4"] = 33

.. note::

   No check is performed by *bpack* to ensure that the default value
   specified for a field is consistent with the corresponding data type.


Enumeration fields
------------------

The *bpack* package supports direct mapping of integer types, strings of
``bytes`` and Python ``str`` (unicode) into enumerated values of Python
:class:`Enum` types (including also :class:`IntEnum` and :class:`IntFlag`).

Example:

.. testcode::

   import enum

   class EColor(enum.IntEnum):
       RED = 1
       GREEN = 2
       BLUE = 3
       BLACK = 10
       WHITE = 11

   @bpack.descriptor(baseunits="bits")
   class BinaryRecord:
       foreground: EColor = bpack.field(size=4, default=EColor.BLACK)
       background: EColor = bpack.field(size=4, default=EColor.WHITE)

   record = BinaryRecord()
   print(record)

.. testoutput::

   BinaryRecord(foreground=<EColor.BLACK: 10>, background=<EColor.WHITE: 11>)

The ``EColor`` enum values are lower that 16 so they can be represented
with only 4 bits.

In particular the binary representation of ``BLACK`` and ``WHITE`` is:

.. doctest::

   >>> format(EColor.BLACK, "04b")
   '1010'
   >>> format(EColor.WHITE, "04b")
   '1011'

and the binary string representing the above defined binary record is:

.. testcode::

   data = bytes([0b10101011])
   print(data)

.. testoutput::

   b'\xab'

The data string can be decoded using the :mod:`bpack.bs` backend that is
suitable to handle binary data structures with ``bits`` as *baseunits*:

.. testcode::

   import bpack.bs

   decoder = bpack.bs.Decoder(BinaryRecord)
   record = decoder.decode(data)
   print(record)

.. testoutput::

   BinaryRecord(foreground=<EColor.BLACK: 10>, background=<EColor.WHITE: 11>)

The result is directly mapped into Python enum values: ``EColor:BLACK`` and
``EColor:WHITE``.

.. note::

   The :class:`Enum` sub-classes are accepted as field type only if all
   the enumeration values have the same type (``int``, ``bytes`` or ``str``).

   Example::

      import enum
      import bpack


      class EType(enum.Enum):
         A = "A"
         B = 2


      @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
      class Record:
         field: EType = bpack.field(size=8, default=EType.A)  # ERROR!

   The above code will result in the following error::

      1 @bpack.descriptor(baseunits=bpack.EBaseUnits.BITS)
      2 class Record:
      3     field: EType = bpack.field(size=8, default=EType.A)

      [...]

      TypeError: only Enum with homogeneous values are supported

Sequence fields
---------------

*bpack* provides a basic support to homogeneous *sequence* fields i.e.
fields containing a sequence of values having the same data type.

The sequence is specified using the standard Python type annotation classes
:class:`typing.Sequence` or :class:`typing.List`, or directly using the
`list[...]` notation.

The data type of a sequence item can be any of the basic data types described
in `Type`_.

.. testcode::

   from typing import Sequence

   @bpack.descriptor
   class BinaryRecord:
       sequence: Sequence[int] = bpack.field(size=1, repeat=2)
       list_: list[float] = bpack.field(size=4, repeat=3)

Please note that the *size* parameter of the :func:`bpack.descriptors.field`
factory function describes the size of the sequence *item*, while the *repeat*
parameter described the number of elements in the *sequence*.

The :mod:`bpack.bs` and :mod:`bpack.st` backend map ``Sequence[T]`` onto
Python :class:`tuple` instances and ``List[T]`` or ``list[T]`` onto
:class:`list` instances.
The :mod:`bpack.np` instead maps all kind of sequences onto
:class:`numpy.ndarray` instances.


Record nesting
--------------

Descriptors of binary structures (record types) can have fields that are
binary structure descriptors in their turn (sub-records).

Example:

.. testcode::

   @bpack.descriptor
   class SubRecord:
       field_21: int = bpack.field(size=2, default=1)
       field_22: int = bpack.field(size=2, default=2)

   @bpack.descriptor
   class Record:
       field_1: int = bpack.field(size=4, default=0)
       field_2: SubRecord = bpack.field(default_factory=SubRecord)

   print(Record())

.. testoutput::

   Record(field_1=0, field_2=SubRecord(field_21=1, field_22=2))


Decoding of the ``Record`` structure will automatically decode also data
belonging to the sub-record and assign to ``field_2`` a ``SubRecord``
instance.


Special type annotations
------------------------

Using the :func:`bpack.descriptors.field` factory function to define fields
can be sometime very verbose and boring.

The *bpack* package provides a typing annotation helper,
:class:`bpack.typing.T`, that allows to specify basic types annotated
with additional information like the *size* or the *signed* attribute for
integers.
This helps to reduce the amount of typesetting required to specify a
binary structure.

The :class:`bpack.typing.T` type annotation class takes in input a string
argument and converts it into an annotated basic type.

.. doctest::

   >>> T["u4"]                           # doctest: +NORMALIZE_WHITESPACE
   typing.Annotated[int, TypeParams(byteorder=None, type='int',
                                    size=4, signed=False)]

The resulting type annotation is a :class:`typing.Annotated` basic type
with attached a :class:`bpack.typing.TypeParams` instance.

This allows `bpack` to retrieve the information necessary to specify a field.

For example the following descriptor:

.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field_1: int = bpack.field(size=4, signed=True, default=0)
       field_2: int = bpack.field(size=4, signed=False, default=1)

Can be specified in a more synthetic form as follows:


.. testcode::

   @bpack.descriptor
   class BinaryRecord:
       field_1: T["i4"] = 0
       field_2: T["u4"] = 1

String descriptors, or *typestr*, are compatible with numpy (a sub-set
of the one used in the numpy `array interface`_).

The *typestr* string format consists of 3 parts:

* an (optional) character describing the bit/byte order of the data

  - ``<``: little-endian,
  - ``>``: big-endian,
  - ``|``: not-relevant

* a character code giving the basic type of the array, and
* an integer providing the number of bits/bytes used by the type

The basic type character codes are:

* ``i``: sighed integer
* ``u``: unsigned integer
* ``f``: float
* ``c``: complex (**currently not supported**)
* ``S``: bytes (string)

.. note::

   Although the *typestr* format allows to specify the bit/byte *order*
   of the datatype it is usually not necessary to do it because
   descriptor object already have this information.

.. seealso::

   :func:`bpack.typing.str_to_type_params`, :class:`bpack.typing.TypeParams`,
   https://numpy.org/doc/stable/reference/arrays.dtypes.html and
   https://numpy.org/doc/stable/reference/arrays.interface.html

.. _`array interface`: https://numpy.org/doc/stable/reference/arrays.interface.html


Data codecs
-----------

Backends
~~~~~~~~

Backends provide encoding/decoding capabilities for binary data
*descriptors* exploiting external packages to do the low level job.

Currently *bpack* provides the following backends:

* :mod:`bpack.st` backend, based on the :mod:`struct` package, and
* :mod:`bpack.bs` backend, based on the bitstruct_ package to decode
  binary data described at bit level, i.e. with fields that can have size
  expressed in terms of number of bits (also smaller that 8).
* :mod:`bpack.np` backend, based on numpy_ (limited encoding capabilities)

Additionally a :mod:`bpack.ba` backend, feature incomplete, is also provided
mainly for benchmarking purposes. The :mod:`bpack.ba` backend is based on the
bitarray_ package.

.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray
.. _numpy: https://numpy.org


Codec objects
~~~~~~~~~~~~~

Each backend provides a ``Codec`` class that can be used to instantiate
a *codec* objects.

Please refer to the `Codecs`_ section for a description of basic concepts
of how decoders work.

Decoders are instantiated passing to the ``Codec`` class a binary data
record *descriptor*.
Each *codec* has

* a ``descriptor`` property, by which it is possible to access the *descriptor*
  associated to the ``Codec`` instance
* a ``baseunits`` property, that indicates the kind of *descriptors* supported
  by the ``Decoder`` class
* a ``decode(data: bytes)`` method, that takes in input a string of
  :class:`bytes` and returns an instance of the record type specified
  at the instantiation of the *codec* object
* a ``encode(record)`` method, that takes in input an instance of the record
  type specified at the instantiation of the *codec* object (a Python object)
  and returns a string of :class:`bytes`

Details on the ``Codec`` API can be found in:

* :class:`bpack.bs.Codec`,
* :class:`bpack.np.Codec`,
* :class:`bpack.st.Codec`

.. note::

   the :mod:`bpack.ba` backend does not provides encoding capabilities
   so no :class:`bpack.ba.Codec` class exists.
   A :class:`bpack.ba.Decoder` class exists instead providing only decoding
   capabilities.


Codec decorator
~~~~~~~~~~~~~~~

Each backend provides also a ``@codec`` decorator the can be used to
add to a *descriptor* direct decoding capabilities.
In particular the ``frombytes(data: bytes)`` class method and the
``tobytes()`` method are added to the *descriptor* to be able to write code
as the following:


.. testcode::

   import bpack
   import bpack.st

   @bpack.st.codec
   @bpack.descriptor
   class BinaryRecord:
       field_1: float = bpack.field(size=8)
       field_2: int = bpack.field(size=4, signed=True)

   binary_data = b"\x18-DT\xfb!\t@\x15\xcd[\x07"
   record = BinaryRecord.frombytes(binary_data)

   print(record)

.. testoutput::

   BinaryRecord(field_1=3.141592653589793, field_2=123456789)

.. testcode::

   encoded_data = record.tobytes()
   assert binary_data == encoded_data

   print(encoded_data)

.. testoutput::

   b'\x18-DT\xfb!\t@\x15\xcd[\x07'

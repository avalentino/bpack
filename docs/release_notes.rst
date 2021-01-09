Release Notes
=============

bpack v0.6.0 (UNRELEASED)
-------------------------

* New numpy_ based backend.
* The ``size`` parameter of the :func:`bpack.descriptors.field` factory
  function is now optional.
* New :meth:`bpack.enums.EByteOrder.get_native` method.
* Now data types in descriptor definition can also be specified by means of
  special type annotation type (:class:`bpack.typing.T`) that accepts
  numpy-like format strings.
* General improvements and code refactoring.
* Improved CI testing.
* Added automatic spell checking of documentation in CI.
* Backward incompatible changes:

  - :class:`bpack.enums.EBaseUnits`, :class:`bpack.enums.EByteOrder` and
    :class:`bpack.enums.EBitOrder` enums moved to the new :mod:`bpack.enums`
    module (the recommended way to access enums is directly form
    :mod:`bpack`, e.g. ``bpack.EByteOrder``)
  - :data:`bpack.enums.EByteOrder.BIG` and
    :data:`bpack.enums.EByteOrder.LITTLE` enumerates have been renamed into
    :data:`bpack.enums.EByteOrder.BE` and :data:`bpack.enums.EByteOrder.LE`
    respectively
  - classes decorated with the :func:`bpack.descriptors.descriptor`
    decorator no longer have the ``__len__`` method automatically added;
    the recommended way to compute the size of a descriptors (class or
    instance) is to use the :func:`bpack.descriptros.calcsize` function
  - the default behavior of the :func:`bpack.decorators.calcsize` has been
    changed to return the size of the input *descriptor* in the same
    *base units* of the descriptor itself; previously the default behavior
    was to return the size in bytes


.. _numpy: https://numpy.org


bpack v0.5.0 (31/12/2020)
-------------------------

* Initial release.

  The package implements all core functionalities but

  - the API is still not stable
  - the documentation is incomplete
  - some advanced feature is still missing

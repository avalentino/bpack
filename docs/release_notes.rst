Release Notes
=============

bpack v1.2.0 (UNRELEASED)
-------------------------

* TBW


bpack v1.1.0 (15/04/2023)
-------------------------

* Added support for signed integers to :func:`bpack.np.unpackbits`.
  Both standard signed integers and integers encoded with sign and module
  are now supported.
* Use uppercase enums in `s1isp.py` example.
* Improved docstrings in  :mod:`bpack.np`.
* Fixed several typos. 


bpack v1.0.0 (05/02/2023)
-------------------------

* Fix compatibility with Python v3.11.
* Move setup configuration from `setup.cfg` to `pyproject.toml`.


bpack v0.8.2 (20/03/2022)
-------------------------

* Fallback to standard bitstruct if the bitstruct.c extension
  does not support the format string


bpack v0.8.1 (30/11/2021)
-------------------------

* Drop ``setup.py``, no longer needed.
* Improve compatibility with `typing-extensions`_ v4.0
  (closes :issue:`1`).
* Use the compiled extension of `bitstruct`_ when available
  (and compatible with the specified format string).
* Use `cbitsturct`_ when available (preferred over the
  compiled extension of `bitstruct`_).

.. _`typing-extensions`: https://pypi.org/project/typing-extensions
.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _cbitsturct: https://github.com/qchateau/cbitstruct


bpack v0.8.0 (03/06/2021)
-------------------------

* New "encoding" feature. Records can be now encoded into binary strings
  using the :mod:`bpack.st` and :mod:`bpack.bs` backends.
  Previously only "decoding" was supported.
  The :mod:`bpack.np` only implements a partial support to encoding currently.


bpack v0.7.1 (08/03/2021)
-------------------------

* Improved User Guide
* :func:`bpack.np.unpackbits` has been generalized and optimized.
* New example for packet decoding.
* Improved support for nested records.


bpack v0.7.0 (21/01/2021)
-------------------------

* New *packbit*/*unpackbit* functions (provisional API).
* Fixed a bug in decoding of nested records.
* Added example program for Sentinel-1 space packets decoding


bpack v0.6.0 (15/01/2021)
-------------------------

* New numpy_ based backend.
* New :meth:`bpack.enums.EByteOrder.get_native` method.
* Now data types in descriptor definition can also be specified by means of
  special type annotation type (:class:`bpack.typing.T`) that accepts
  numpy-like format strings.
* Now it is no longer necessary to use the :func:`dataclasses.dataclass`
  decorator to define a descriptor.
  That way to define descriptors is **depercated**.
  All parameters previously specified via :func:`dataclasses.dataclass`
  (like e.g. *frozen*) shall now be passed directly to the
  :func:`bpack.descriptors.descriptor` decorator.
  With this change the use of :mod:`dataclasses` becomes an
  implementation detail.
* The ``size`` parameter of the :func:`bpack.descriptors.field` factory
  function is now optional.
* General improvements and code refactoring.
* Improved CI testing.
* Added automatic spell checking of documentation in CI.
* Backward incompatible changes:

  - :class:`bpack.enums.EBaseUnits`, :class:`bpack.enums.EByteOrder` and
    :class:`bpack.enums.EBitOrder` enums moved to the new :mod:`bpack.enums`
    module (the recommended way to access enums is directly from
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

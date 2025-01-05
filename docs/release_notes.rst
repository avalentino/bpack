Release Notes
=============

bpack v1.3.0 (06/01/2025)
-------------------------

* Support for annotations saved in string form (see also `PEP-563`_).
  Is some circumstances Python typing annotations are stored
  as strings. E.g. this happens when people uses::

    from __future__ import annotations

  Starting from v1.3.0, `bpack` is compatible with this way of storing
  annotations.
  Please note, anyway, that `bpack` still need to evaluate the annotations
  at compile time so the "Postponed Evaluation of Annotations" described in
  `PEP-563`_ is not really supported.

.. _`PEP-563`: https://peps.python.org/pep-0563


bpack v1.2.0 (26/11/2024)
-------------------------

* Drop support to Python 3.7 and 3.8. Now `bpack` requires Python >= 3.9.
* Add support to Python 3.13.
* The internal :func:`bpack.utils.create_fn` function has been removed
  and replaced by the new :func:`bpack.utils.add_function_to_class`
  internal function.
  Since the change is on utility functions that are considered internal and
  not part of the public package API, this is not considered a backward
  incompatible change.
* New 'full' installation option added to `pyproject.toml`.
* No longer use deprecated syntax in sphinx configuration.
* Improved documentation and fixed typos.
* flake8_ configuration moved to a dedicated file.
* Do not test the :mod:`bpack.ba` backend in PyPy3_.
* New functions:
  - :func:`bpack.typing.type_params_to_str`
  - :func:`bpack.descriptors.flat_fields_iterator`
* New :mod:`bpack.tools.codegen` module. It includes tool to generate flat
  binary record descriptors starting from nested ones
  (requires Python >= 3.10).

.. _flake8: https://github.com/pycqa/flake8
.. _PyPy3: https://pypy.org


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

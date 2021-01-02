:orphan:

Miscellanea *To Do* list
------------------------

* improve documentation
* improve typing
* benchmarks
* include :func:`dataclasses.dataclass` generation in
  :func:`bpack.descriptors.descriptor` (the use should not explicitly use
  :mod:`dataclasses`)
* drop :func:`bpack.descriptors.descriptor` objects ``__len__`` method
  (always use :func:`bpack.descriptros.calcsize`)
* :class:`EBaseUnits` shall become a :class:`IntFlag` to allow the
  *decoders* to declare base-units as follows::

    baseunits = bpack.EBaseUnits.BITS | bpack.EBaseUnits.BYTES

* replace :data:`EByteOrder.BIG` and :data:`EByteOrder.LITTLE`
  with ``BE`` and ``LE``
* support for complex data type in all backends
* new ``nfields(descriptor)`` helper function
* nested records and repeat
* improve support for typing -- bpack.T('i4')
* decoder attributes (Decoder.descriptor)

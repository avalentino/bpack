:orphan:

Miscellanea *To Do* list
------------------------

* check alignment in bpack.st (native '@' and '' behaves differently from '=')
* improve documentation
  - add missing documentation for `unpackbits` functions
* improve typing
  - MyPy
* benchmarks
* :class:`EBaseUnits` shall become a :class:`IntFlag` to allow the
  *decoders* to declare base-units as follows::

    baseunits = bpack.EBaseUnits.BITS | bpack.EBaseUnits.BYTES

* nested records and repeat (test)
* typing in generated methods (.frombytes) TBD

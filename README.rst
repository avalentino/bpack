Binary data structures (un-)Packing library
===========================================

:Copyright: 2020, Antonio Valentino <antonio.valentino@tiscali.it>

.. badges

|PyPI Status| |GHA Status| |Documentation Status|

.. |PyPI Status| image:: https://img.shields.io/pypi/v/bpack.svg
    :target: https://pypi.org/project/bpack
    :alt: PyPI Status
.. |GHA Status| image:: https://github.com/avalentino/bpack/workflows/Build/badge.svg
    :target: https://github.com/avalentino/bpack/actions
    :alt: GitHub Actions Status
.. |Documentation Status| image:: https://readthedocs.org/projects/bpack/badge/?version=latest
    :target: https://bpack.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. description

The *bpack* Python package provides tools to describe and encode/decode
binary data.

Binary data are assumed to be organised in *records*, each composed by a
sequence of fields. Fields are characterised by a known size, offset
(w.r.t. the beginning of the record) and datatype.

The package provides classes and functions that can be used to:

* describe binary data structures in a declarative way (structures can
  be specified up to the bit level)
* automatically generate encoders/decoders for a specified data descriptor

Encoders/decoders (*backends*) rely on well known Python packages like:

* |struct| (form the standard library)
* bitstruct_ (optional)
* bitarray_ (optional)
* numpy_ (optional) - **TODO**


.. _struct: https://docs.python.org/3/library/struct.html
.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _bitarray: https://github.com/ilanschnell/bitarray
.. _numpy: https://numpy.org

.. local-definitions

.. |struct| replace:: struct_

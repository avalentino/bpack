Binary data structures (un-)Packing library
===========================================

.. badges

|PyPI Status| |GHA Status| |Documentation Status|

.. |PyPI Status| image:: https://img.shields.io/pypi/v/bpack.svg
    :target: https://pypi.org/project/bpack
    :alt: PyPI Status
.. |GHA Status| image:: https://github.com/avalentino/bpack/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/avalentino/bpack/actions
    :alt: GitHub Actions Status
.. |Documentation Status| image:: https://readthedocs.org/projects/bpack/badge/?version=latest
    :target: https://bpack.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. description

The *bpack* Python package provides tools to describe and encode/decode
binary data.

Binary data are assumed to be organized in *records*, each composed by a
sequence of fields. Fields are characterized by a known size, offset
(w.r.t. the beginning of the record) and datatype.

The package provides classes and functions that can be used to:

* describe binary data structures in a declarative way (structures can
  be specified up to the bit level)
* automatically generate encoders/decoders for a specified data descriptor

Encoders/decoders (*backends*) rely on well known Python packages like:

* |struct| (form the standard library)
* bitstruct_ (optional)
* numpy_ (optional)
* bitarray_ (optional) - partial implementation


.. _struct: https://docs.python.org/3/library/struct.html
.. _bitstruct: https://github.com/eerimoq/bitstruct
.. _numpy: https://numpy.org
.. _bitarray: https://github.com/ilanschnell/bitarray

.. local-definitions

.. |struct| replace:: struct_


License
-------

:Copyright: 2020-2023, Antonio Valentino <antonio.valentino@tiscali.it>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

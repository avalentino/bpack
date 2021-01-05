Installation
============

Pip
---

Basic installation:

.. code-block:: shell

  $ python3 -m pip install bpack

Recommended:

.. code-block:: shell

  $ python3 -m pip install bpack[bs]

to install also dependencies necessary to use the :mod:`bpack.bs` backend
and (for binary structures defined up to the bit level).


Conda
-----

.. code-block:: shell

  $ conda install -c conda-forge bpack


Testing
-------

To run the test suite it is necessary to have pytest_ installed:

.. code-block:: shell

  $ python3 -m pytest --pyargs bpack

This only tests decoder backends for which the necessary dependencies
are available.
To run a complete test please make sure to install all optional dependencies
and testing libraries:

.. code-block:: shell

  $ python3 -m pip install bpack[test]


.. _pytest: https://docs.pytest.org

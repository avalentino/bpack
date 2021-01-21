Developers Guide
================

Project links
-------------

:PyPI page:
    https://pypi.org/project/bpack
:repository:
    https://github.com/avalentino/bpack
:issue tracker:
    https://github.com/avalentino/bpack/issues
:CI:
    https://github.com/avalentino/bpack/actions


Set-up the development environment
----------------------------------

Pip
~~~

.. code-block:: shell

  $ python3 -m venv --prompt venv .venv
  $ source .venv/bin/activate
  (venv) $ python3 -m pip install -r requirements-dev-txt


Conda
~~~~~

.. code-block:: shell

  $ conda create -c conda-forge -n bpack \
      --file requirements-dev.txt python=3


Debian/Ubuntu
~~~~~~~~~~~~~

.. code-block:: shell

  $ sudo apt install python3-bitstruct python3-bitarray \
      python3-pytest python3-pytest-cov \
      python3-sphinx python3-sphinx-rtd-theme


Testing the code
----------------

Basic testing
~~~~~~~~~~~~~

.. code-block:: shell

  $ python3 -m pytest

It is also recommended to use the ``-W=error`` option.


Advanced testing
~~~~~~~~~~~~~~~~

Tox_ is used to run a comprehensive test suite on multiple Python version.
I also check formatting, coverage and checks that the documentation builds
properly.

.. code-block:: shell

  $ tox


Test coverage
-------------

.. code-block:: shell

  $ python3 -m pytest --cov --cov-report=html --cov-report=term bpack


Check formatting
----------------

.. code-block:: shell

  $ python3 -m flake8 --statistics --count bpack


Build the documentation
-----------------------

.. code-block:: shell

  $ make -C docs html


Test code snippets in the documentation
---------------------------------------

.. code-block:: shell

  $ make -C docs doctest


Check documentation links
-------------------------

.. code-block:: shell

  $ make -C docs linkcheck


Check documentation spelling
----------------------------

.. code-block:: shell

  $ make -C docs spelling


Update the API documentation
----------------------------

.. code-block:: shell

  $ rm -rf docs/api
  $ sphinx-apidoc --module-first --separate --no-toc \
      --doc-project "bpack API" -o docs/api \
      --templatedir docs/_templates/apidoc \
      bpack bpack/tests


.. _Tox: https://tox.readthedocs.io
.. _Python: https://www.python.org
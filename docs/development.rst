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
:HTML documentation:
    https://bpack.readthedocs.io


Set-up the development environment
----------------------------------

Pip based environment
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

  $ python3 -m venv --prompt venv .venv
  $ source .venv/bin/activate
  (venv) $ python3 -m pip install -r requirements-dev-txt


Conda based environment
~~~~~~~~~~~~~~~~~~~~~~~

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

Tox_ (>4) is used to run a comprehensive test suite on multiple Python version.
It also checks formatting, coverage and ensures that the documentation builds
properly.

.. code-block:: shell

  $ tox run


Test coverage
-------------

.. code-block:: shell

  $ python3 -m pytest --cov --cov-report=html --cov-report=term bpack


Check code style and formatting
-------------------------------

The code style and formatting shall be checked with flake8_ as follows:

.. code-block:: shell

  $ python3 -m flake8 --statistics --count bpack

Moreover, also the correct formatting of "docstrings" shall be checked, using
pydocstyle_ this time:

.. code-block:: shell

	$ python3 -m pydocstyle --count bpack

A more strict check of formatting can be done using black_:

.. code-block:: shell

	$ python3 -m black --check bpack

Finally the ordering of imports can be checked with isort_ as follows:

.. code-block:: shell

	$ python3 -m isort --check bpack

Please note that all the relevant configuration for the above mentioned
tools are in the `pyproject.toml` file.


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
.. _flake8: https://flake8.pycqa.org
.. _pydocstyle: http://www.pydocstyle.org
.. _black: https://black.readthedocs.io
.. _isort: https://pycqa.github.io/isort

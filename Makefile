#!/usr/bin/make -f

PYTHON=python3

.PHONY: default help dist check clean distclean api lint

default: help

help:
	@echo "Usage: make <TARGET>"
	@echo "Available targets:"
	@echo "  help      - print this help message"
	@echo "  dist      - generate the distribution packages (source and wheel)"
	@echo "  check     - run a full test (using tox)"
	@echo "  clean     - clean build artifacts"
	@echo "  distclean - clean all generated and cache files"
	@echo "  api       - update the API source files in the documentation"
	@echo "  lint      - perform check with code linter (flake8, black)"

dist:
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*

check:
	$(PYTHON) -m tox run

clean:
	$(MAKE) -C docs clean
	$(RM) -r build bpack.egg-info docs/_build
	$(RM) -r __pycache__ */__pycache__ */*/__pycache__

distclean: clean
	$(RM) -r dist .coverage htmlcov .pytest_cache .tox
	@# $(RM) .DS_Store */.DS_Store */*/.DS_Store
	@# $(RM) -r .idea

api:
	$(RM) -r docs/api
	sphinx-apidoc --module-first --separate --no-toc --doc-project "bpack API" \
	  -o docs/api --templatedir docs/_templates/apidoc bpack bpack/tests

lint:
	$(PYTHON) -m flake8 --count --statistics bpack
	$(PYTHON) -m pydocstyle --count bpack
	$(PYTHON) -m isort --check bpack
	$(PYTHON) -m black --check bpack

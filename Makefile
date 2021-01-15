#!/usr/bin/make -f

PYTHON=python3

.PHONY: default help sdist check clean distclean

default: help

help:
	@echo "Usage: make <TARGET>"
	@echo "Available targets:"
	@echo "  help      - print this help message"
	@echo "  sdist     - generate the source distribution"
	@echo "  check     - run a full test (using tox)"
	@echo "  clean     - clean build artifacts"
	@echo "  distclean - clean all generated and cache files"

sdist:
	$(PYTHON) setup.py sdist

check:
	$(PYTHON) -m tox

clean:
	$(MAKE) -C docs clean
	$(RM) -r build bpack.egg-info docs/_build
	$(RM) -r __pycache__ */__pycache__ */*/__pycache__

distclean: clean
	$(RM) -r dist .coverage htmlcov .pytest_cache .tox
	@# $(RM) .DS_Store */.DS_Store */*/.DS_Store
	@# $(RM) -r .idea

#!/usr/bin/env python3

import os
import setuptools


ROOT = os.path.dirname(__file__)


def get_version(filename, strip_extra=False):
    import re
    from distutils.version import LooseVersion
    # import packaging.version

    with open(filename) as fd:
        data = fd.read()

    mobj = re.search(
        r'''^__version__\s*=\s*(?P<quote>['"])(?P<version>.*)(?P=quote)''',
        data, re.MULTILINE)
    version = LooseVersion(mobj.group('version'))

    if strip_extra:
        return '.'.join(map(str, version.version[:3]))
    else:
        return version.vstring


cfg = dict(
    version=get_version(os.path.join(ROOT, 'bpack', '__init__.py')),
)


if __name__ == '__main__':
    setuptools.setup(**cfg)

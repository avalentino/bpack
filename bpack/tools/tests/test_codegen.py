"""Unit tests for bpack.tools.codegen."""

import sys
import inspect
import pathlib

import pytest

import bpack.tools.codegen

from .data.flat import Flat
from .data.nested import Nested

flat_data = pathlib.Path(__file__).parent.joinpath("data/flat.py").read_text()


@pytest.mark.skipif(sys.version_info < (3, 10), reason="needs Python >= 3.10")
def test_flat_descriptor_code_generator():
    codegen = bpack.tools.codegen.FlatDescriptorCodeGenerator(
        Nested, name="Flat"
    )
    code = codegen.get_code()
    code = code.replace("b'abc'", 'b"abc"')
    assert code.strip() == inspect.getsource(Flat).strip()


@pytest.mark.skipif(sys.version_info < (3, 10), reason="needs Python >= 3.10")
def test_flat_descriptor_code_generator_with_includes():
    codegen = bpack.tools.codegen.FlatDescriptorCodeGenerator(
        Nested, name="Flat"
    )
    code = codegen.get_code(imports=True)
    code = code.replace("b'abc'", 'b"abc"')
    assert code.strip() == flat_data.strip()

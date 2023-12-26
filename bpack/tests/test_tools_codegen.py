"""Unit tests for bpack.tools.codegen."""

import inspect
import pathlib

import bpack.tools.codegen

from .data.flat import Flat
from .data.nested import Nested

flat_data = pathlib.Path(__file__).parent.joinpath("data/flat.py").read_text()


def test_flat_descriptor_code_generator():
    codegen = bpack.tools.codegen.FlatDescriptorCodeGenerator(
        Nested, name="Flat"
    )
    code = codegen.get_code()
    assert code.strip() == inspect.getsource(Flat).strip()


def test_flat_descriptor_code_generator_with_includes():
    codegen = bpack.tools.codegen.FlatDescriptorCodeGenerator(
        Nested, name="Flat"
    )
    code = codegen.get_code(imports=True)
    assert code.strip() == flat_data.strip()

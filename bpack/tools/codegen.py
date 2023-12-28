"""Code generators for bpack."""

import enum
import typing
import inspect
import textwrap
import warnings
import functools
import itertools
import collections
from typing import Optional, Union
from dataclasses import MISSING

import bpack
from bpack.codecs import has_codec, get_codec_type, Codec
from bpack.typing import type_params_to_str
from bpack.descriptors import flat_fields_iterator, METADATA_KEY

__all__ = [
    "FlatDescriptorCodeGenerator",
]


def annotated_to_str(annotated_type: typing.Annotated):
    _, params = typing.get_args(annotated_type)
    return type_params_to_str(params)


def get_default_str(value):
    if isinstance(value, enum.Enum):
        return f"{value.__class__.__name__}.{value.name}"
    else:
        return str(value)


def iter_descriptor_types(descriptor, recursive: bool = True):
    for f in bpack.fields(descriptor):
        if bpack.is_descriptor(f.type):
            yield f.type
            if recursive:
                yield from iter_descriptor_types(f.type)


def method_or_property(x):
    return inspect.isfunction(x) or inspect.isdatadescriptor(x)


@functools.cache
def _is_stdlib_module(module: str):
    import sys

    module = module.split(".", 1)[0]
    # @COMPATIBILITY: new in Python 3.10
    if hasattr(sys, "stdlib_module_names"):
        return module in sys.stdlib_module_names
    else:
        import pathlib
        import sysconfig

        platstdlib = pathlib.Path(sysconfig.get_path("platstdlib"))
        return bool(platstdlib.glob(f"{module}*"))


def _classify_modules(modules):
    stdlib = []
    others = []
    for module in modules:
        if _is_stdlib_module(module):
            stdlib.append(module)
        else:
            others.append(module)
    return stdlib, others


class FlatDescriptorCodeGenerator:
    """Source code generator for flat binary data descriptors.

    Generate the Python source code of a flat binary record descriptor
    equivalent to a nested one provided as input.
    """

    def __init__(
        self,
        descriptor,
        name: Optional[str] = None,
        indent: Union[int, str] = "    ",
    ):
        """Initialize a `FlatDescriptorCodeGenerator` instance.

        Initialization arguments:

        :param descriptor:
            binary record descriptor (possibly nested)
        :param name:
            class name to be used for the generated flat record descriptor
        :param indent:
            string of number of blanks to be used for the indentation in the
            generated code
        """
        self._indent = " " * indent if isinstance(indent, int) else indent
        self._filed_names = set()
        self.imports: dict = collections.defaultdict(set)
        self.imports[None].add("bpack")
        self.module_docstring = None
        self.pre_code = None
        self.post_code = None
        self._lines = []

        self._setup_class_declaration(descriptor, name)
        self._setup_fields(descriptor)
        self._lines.append("")
        self._setup_methods(descriptor)

    def _setup_class_declaration(self, descriptor, name: Optional[str] = None):
        if has_codec(descriptor):
            backend = get_codec_type(descriptor).__module__
            codec_type = "codec" if has_codec(descriptor, Codec) else "decoder"
            self._lines.append(f"@{backend}.{codec_type}")
            self.imports[None].add(backend)

        descriptor_args = []

        baseunits = bpack.baseunits(descriptor).name
        descriptor_args.append(f"baseunits=EBaseUnits.{baseunits}")
        self.imports["bpack"].add("EBaseUnits")

        byteorder = bpack.byteorder(descriptor).name
        if bpack.byteorder(descriptor) != bpack.EByteOrder.DEFAULT:
            descriptor_args.append(f"byteorder=EByteOrder.{byteorder}")
            self.imports["bpack"].add("EByteOrder")

        # TODO: bitorder

        self._lines.append(f"@bpack.descriptor({', '.join(descriptor_args)})")

        name = descriptor.__name__ if name is None else name
        self._lines.append(f"class {name}:")

        if (
            descriptor.__doc__ is not None
            and not descriptor.__doc__.startswith(descriptor.__name__)
        ):
            self._lines.append(f'{self._indent}"""{descriptor.__doc__}"""')
            self._lines.append("")

    def _setup_fields(self, descriptor):
        auto_offset = 0
        for fld in flat_fields_iterator(descriptor):
            if bpack.typing.is_annotated(fld.type):
                typestr = f'T["{annotated_to_str(fld.type)}"]'
                self.imports["bpack"].add("T")
            elif fld.type is bool:
                typestr = "bool"
            elif issubclass(fld.type, enum.Enum):
                typestr = fld.type.__name__
                self.imports[fld.type.__module__].add(typestr)
            else:
                raise TypeError(f"unsupported field type: {fld.type!r}")

            metadata = fld.metadata[METADATA_KEY]
            size = metadata["size"]
            offset = metadata["offset"]

            is_annotated_or_bool = (
                bpack.typing.is_annotated(fld.type) or fld.type is bool
            )

            size_str = f"size={size}" if not is_annotated_or_bool else ""
            offset_str = f"offset={offset}" if offset != auto_offset else ""
            if fld.default_factory is not MISSING:
                default_str = f"default_factory={fld.default_factory}"
                module = fld.default_factory.__module__
                self.imports[module].add(fld.default_factory.__name__)
            elif fld.default is not MISSING:
                default_str = f"default={get_default_str(fld.default)}"
                if hasattr(fld.default, "__class__"):
                    module = fld.default.__class__.__module__
                    name = fld.default.__class__.__name__
                    self.imports[module].add(name)
            else:
                default_str = ""

            if (
                any([size_str, offset_str])
                or fld.default_factory is not MISSING
            ):
                args = [
                    item
                    for item in [size_str, offset_str, default_str]
                    if item
                ]
                field_str = f" = bpack.field({', '.join(args)})"
            elif is_annotated_or_bool and fld.default is not MISSING:
                field_str = f" = {get_default_str(fld.default)}"
                if hasattr(fld.default, "__class__"):
                    module = fld.default.__class__.__module__
                    name = fld.default.__class__.__name__
                    self.imports[module].add(name)
            else:
                field_str = ""

            auto_offset = offset + size

            self._filed_names.add(fld.name)
            self._lines.append(
                f"{self._indent}{fld.name}: {typestr}{field_str}"
            )

    def _setup_methods(self, descriptor):
        global_ctx = vars(inspect.getmodule(descriptor))

        for klass in itertools.chain(
            iter_descriptor_types(descriptor), [descriptor]
        ):
            local_ctx = vars(klass)

            targets = {
                k: v
                for k, v in inspect.getmembers(klass, method_or_property)
                if not k.startswith("__")
            }
            targets.pop("tobytes", None)
            targets.pop("frombytes", None)
            if not targets:
                continue
            self._lines.append(f"{self._indent}# === {klass.__name__} ===")

            for method in targets.values():
                self._lines.append(
                    textwrap.indent(inspect.getsource(method), "")
                )

                annotations = inspect.get_annotations(method)
                for var in annotations.values():
                    module = inspect.getmodule(var)
                    if module is not None:
                        self.imports[module.__name__].add(var.__name__)
                    else:
                        warnings.warn(
                            f"(annotations) unable to determine the module of "
                            f"{var!r}"
                        )

                variables = inspect.getclosurevars(method)
                for var_type in ("nonlocals", "globals"):
                    for name, var in getattr(variables, var_type).items():
                        try:
                            name = (
                                var if isinstance(var, str) else var.__name__
                            )
                        except AttributeError:
                            module = descriptor.__module__
                            self.imports[module].add(name)
                        else:
                            module = inspect.getmodule(var)
                            if module is not None:
                                if module.__name__ == name:
                                    self.imports[None].add(name)
                                else:
                                    self.imports[module.__name__].add(name)
                            elif name in global_ctx:
                                self.imports[descriptor.__module__].add(name)
                            elif name not in local_ctx:
                                warnings.warn(
                                    f"({var_type}) unable to determine the "
                                    f"module of {name!r}"
                                )

    def _get_classified_imports(self):
        if self.imports.get(None):
            stdlib, others = _classify_modules(self.imports[None])
        else:
            stdlib = others = None

        from_stdlib, from_others = _classify_modules(
            key for key in self.imports if key and key != "builtins"
        )

        return stdlib, others, from_stdlib, from_others

    def _get_import_lines(
        self, stdlib, others, from_stdlib, from_others, line_length: int = 80
    ):
        import_lines = []

        if stdlib:
            import_lines.extend(
                f"import {name}" for name in sorted(sorted(stdlib), key=len)
            )
        if from_stdlib:
            for key in sorted(sorted(from_stdlib), key=len):
                values = sorted(self.imports[key])
                s = f"from {key} import {', '.join(values)}"
                if len(s) < line_length:
                    import_lines.append(s)
                else:
                    import_lines.append(f"from {key} import (")
                    import_lines.extend(
                        f"{self._indent}{value}," for value in values
                    )
                    import_lines.append(")")

        if others or from_others:
            import_lines.append("")

        if others:
            import_lines.extend(
                f"import {name}" for name in sorted(sorted(others), key=len)
            )
        if from_others:
            for key in sorted(sorted(from_others), key=len):
                values = sorted(self.imports[key])
                s = f"from {key} import {', '.join(values)}"
                if len(s) < line_length:
                    import_lines.append(s)
                else:
                    import_lines.append(f"from {key} import (")
                    import_lines.extend(
                        f"{self._indent}{value}," for value in values
                    )
                    import_lines.append(")")

        return import_lines

    def patch(self, code):
        """Patch the generated code."""
        return code

    def get_code(
        self,
        imports: bool = False,
        line_length: int = 80,
        beautify: bool = True,
    ):
        """Generate the Python source code.

        By default only the code for the binary record descriptor is generated.
        If the `imports` is set to `True`, also the import statements for all
        types used by the descriptor are included in the generated code.
        """
        lines = []

        if self.module_docstring:
            lines.extend(f'"""{self.module_docstring}"""'.splitlines())
            lines.append("")
        if imports:
            import_lines = self._get_import_lines(
                *self._get_classified_imports(), line_length=line_length
            )
            lines.extend(import_lines)
            lines.append("")
            lines.append("")

        if self.pre_code:
            lines.extend(self.pre_code.splitlines())

        lines.extend(self._lines)

        if self.post_code:
            lines.extend(self.post_code.splitlines())

        code = "\n".join(lines)

        code = self.patch(code)

        if beautify:
            try:
                import black
            except ImportError:
                pass
            else:
                mode = black.Mode(
                    target_versions={black.TargetVersion.PY311},
                    line_length=line_length,
                )
                code = black.format_str(code, mode=mode)

        return code

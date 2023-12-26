"""Code generators for bpack."""

import enum
import typing
import inspect
import textwrap
import itertools
import collections
from typing import Optional, Union
from dataclasses import MISSING

import bpack
from bpack.typing import type_params_to_str
from bpack.codecs import has_codec, get_codec_type, Codec
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


class FlatDescriptorCodeGenerator:
    """Source code generator for flat binary data descriptors."""

    def __init__(
            self,
            descriptor,
            name: Optional[str] = None,
            indent: Union[int, str] = "    ",
    ):
        self._indent = " " * indent if isinstance(indent, int) else indent
        self._lines = []
        self._imports = collections.defaultdict(set)
        self._imports[None].add("bpack")
        self._import_lines = []

        self._setup_class_declaration(descriptor, name)
        self._setup_fields(descriptor)
        self._lines.append("")
        self._setup_methods(descriptor)
        self._import_lines.extend(self._get_imports())

    def _setup_class_declaration(self, descriptor, name: Optional[str] = None):
        if has_codec(descriptor):
            backend = get_codec_type(descriptor).__module__
            codec_type = "codec" if has_codec(descriptor, Codec) else "decoder"
            self._lines.append(f"@{backend}.{codec_type}")

        descriptor_args = []

        baseunits = bpack.baseunits(descriptor).name
        descriptor_args.append(f"baseunits=EBaseUnits.{baseunits}")
        self._imports["bpack"].add("EBaseUnits")

        byteorder = bpack.byteorder(descriptor).name
        if bpack.byteorder(descriptor) != bpack.EByteOrder.DEFAULT:
            descriptor_args.append(f"byteorder=EByteorder.{byteorder}")
            self._imports["bpack"].add("EByteorder")

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
                self._imports["bpack"].add("T")
            elif fld.type is bool:
                typestr = "bool"
            elif issubclass(fld.type, enum.Enum):
                typestr = fld.type.__name__
                self._imports[fld.type.__module__].add(typestr)
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
                self._imports[module].add(fld.default_factory.__name__)
            elif fld.default is not MISSING:
                default_str = f"default={get_default_str(fld.default)}"
                if hasattr(fld.default, "__class__"):
                    module = fld.default.__class__.__module__
                    name = fld.default.__class__.__name__
                    self._imports[module].add(name)
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
                    self._imports[module].add(name)
            else:
                field_str = ""

            auto_offset = offset + size

            self._lines.append(
                f"{self._indent}{fld.name}: {typestr}{field_str}"
            )

    def _setup_methods(self, descriptor):
        for klass in itertools.chain(
            iter_descriptor_types(descriptor), [descriptor]
        ):
            targets = {
                k: v for k, v in inspect.getmembers(klass, method_or_property)
                if not k.startswith("_")
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

    def _get_imports(self):
        import_lines = []

        if self._imports.get(None):
            self._import_lines.extend(
                f"import {name}" for name in sorted(self._imports[None])
            )

        import_lines.extend(
            f"from {key} import {', '.join(sorted(values))}"
            for key, values in self._imports.items()
            if key and key != "builtins"
        )

        return import_lines

    def get_code(self, imports: bool = False):
        lines = []
        if imports:
            lines.extend(self._import_lines)
            lines.append("")
            lines.append("")
        lines.extend(self._lines)

        return "\n".join(lines)

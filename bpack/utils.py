"""Internal utility functions and classes."""

import enum
import typing
import functools
import dataclasses
import collections.abc

from .typing import get_origin, get_args, Annotated


def classdecorator(func):
    """Class decorator that can be used with or without parameters."""

    @functools.wraps(func)
    def wrapper(cls=None, **kwargs):
        def wrap(klass):
            return func(klass, **kwargs)

        # Check if called as @decorator or @decorator(...).
        if cls is None:
            # Called with parentheses
            return wrap

        # Called as @decorator without parentheses
        return wrap(cls)

    return wrapper


def add_function_to_class(
    cls,
    name,
    args,
    body,
    *,
    globals=None,  # noqa: A002
    locals=None,  # noqa: A002
    return_type=dataclasses.MISSING,
    is_classmethod: bool = False,
):
    """Create a function object and add it to the specified class."""
    if hasattr(dataclasses, "_create_fn"):
        func = dataclasses._create_fn(
            name,
            args,
            body,
            globals=globals,
            locals=locals,
            return_type=return_type,
        )
        if is_classmethod:
            func = classmethod(func)
        dataclasses._set_new_attribute(cls, name, func)
    else:
        import textwrap

        body = textwrap.indent("\n".join(body), "    ").splitlines(True)
        func_builder = dataclasses._FuncBuilder(globals)
        func_builder.add_fn(
            name,
            args,
            body,
            locals=locals,
            return_type=return_type,
            decorator="@classmethod" if is_classmethod else None,
        )
        func_builder.add_fns_to_class(cls)


def set_new_attribute(cls, name, value):
    """Programmatically add a new attribute/method to a class."""
    return dataclasses._set_new_attribute(cls, name, value)


def sequence_type(type_: type, error: bool = False) -> type | None:
    """Return the sequence type associated to a typed sequence.

    The function return :class:`list` or :class:`tuple` if the input is
    considered a valid typed sequence, ``None`` otherwise.

    Please note that fields annotated with :class:`typing.Tuple` are not
    considered homogeneous sequences even if all items are specified to
    have the same type.
    """
    sequence_type_ = get_origin(type_)
    if sequence_type_ is None:
        return None
    if not issubclass(sequence_type_, typing.Sequence):
        return None
    args = get_args(type_)
    if len(args) < 1:
        return None
    if len(args) > 1:
        if error:
            raise TypeError(f"{type_} is not supported")
        else:
            return None

    if not issubclass(sequence_type_, collections.abc.MutableSequence):
        sequence_type_ = tuple

    assert sequence_type_ in {list, tuple}

    return sequence_type_


def is_sequence_type(type_: type, error: bool = False) -> bool:
    """Return True if the input is an homogeneous typed sequence.

    Please note that fields annotated with :class:`typing.Tuple` are not
    considered homogeneous sequences even if all items are specified to
    have the same type.
    """
    seq_type = sequence_type(type_, error=error)
    return seq_type is not None


def is_enum_type(type_: type) -> bool:
    """Return True if the input is and :class:`enum.Enum`."""
    return get_origin(type_) is None and issubclass(type_, enum.Enum)


def enum_item_type(enum_cls: type[enum.Enum]) -> type:
    """Return the type of the items of an enum.Enum.

    This function also checks that all items of an enum have the same
    (or compatible) type.
    """
    if not is_enum_type(enum_cls):
        raise TypeError(f'"{enum_cls}" is not an enum. Enum')
    elif issubclass(enum_cls, int):
        return int
    else:
        types_ = [type(item.value) for item in enum_cls]
        type_ = types_.pop()
        for item in types_:
            if issubclass(item, type_):
                continue
            elif issubclass(type_, item):
                type_ = item
            else:
                raise TypeError(
                    "only Enum with homogeneous values are supported"
                )
        return type_


def effective_type(
    type_: type | type[enum.Enum] | type, keep_annotations: bool = False
) -> type:
    """Return the effective type.

    In case of enums or sequences return the item type.
    """
    origin = get_origin(type_)
    if origin is None:
        if type_ is not None and issubclass(type_, enum.Enum):
            etype = enum_item_type(type_)
        else:
            etype = type_
    elif origin is Annotated:  # TODO: check issubclass(origin, Annotated):
        if keep_annotations:
            etype = type_
        else:
            etype, _ = get_args(type_)
    elif not issubclass(origin, typing.Sequence):
        etype = type_
    elif issubclass(origin, tuple):
        etype = type_
    else:
        # is a sequence
        args = get_args(type_)
        assert len(args) == 1
        etype = effective_type(args[0], keep_annotations=keep_annotations)

    return etype


def is_int_type(type_: type) -> bool:
    """Return true if the effective type is an integer."""
    if is_sequence_type(type_):
        etype = effective_type(type_)
        return issubclass(etype, int)
    else:
        return issubclass(type_, int)

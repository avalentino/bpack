"""Utility functions and classes."""

import enum
import typing
import functools
import dataclasses
import collections.abc

from typing import Union, Type


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


def create_fn(name, args, body, *, globals=None, locals=None,
              return_type=dataclasses.MISSING):
    """Create a function object."""
    return dataclasses._create_fn(name, args, body,
                                  globals=globals, locals=locals,
                                  return_type=return_type)


def set_new_attribute(cls, name, value):
    """Programmatically add a new attribute/method ro a class."""
    return dataclasses._set_new_attribute(cls, name, value)


def get_sequence_type(type_: Type, error: bool = False) -> Union[Type, None]:
    """Return the sequence type associated to a typed sequence.

    The function return :class:`list` or :class:`tuple` if the input is
    considered a valid typed sequence, ``None`` otherwise.

    Please ot that :class:`typing.Tuple`s are not considered homogeneous
    sequences even if all items are specified to have the same type.
    """
    sequence_type = typing.get_origin(type_)
    if sequence_type is None:
        return None
    if not issubclass(sequence_type, typing.Sequence):
        return None
    args = typing.get_args(type_)
    if len(args) < 1:
        return None
    if len(args) > 1:
        if error:
            raise TypeError(f'{type_} is not supported')
        else:
            return None

    if not issubclass(sequence_type, collections.abc.MutableSequence):
        sequence_type = tuple

    assert sequence_type in {list, tuple}

    return sequence_type


def is_sequence_type(type_: Type, error: bool = False) -> bool:
    """Return True if the input is an homogeneous typed sequence.

    Please ot that :class:`typing.Tuple`s are not considered homogeneous
    sequences even if all items are specified to have the same type.
    """
    seq_type = get_sequence_type(type_, error=error)
    return seq_type is not None


def is_enum_type(type_: Type) -> bool:
    """Return True if the input is and :class:`enum.Enum`."""
    return (typing.get_origin(type_) is None and
            issubclass(type_, enum.Enum))


def enum_item_type(enum_cls: Type[enum.Enum]) -> Type:
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
                    'only Enum with homogeneous values are supported')
        return type_


def effective_type(type_: Type) -> Type:
    """Return the effective type.

    In case of enums or sequences return the item type.
    """
    origin = typing.get_origin(type_)
    if origin is None:
        if type_ is not None and issubclass(type_, enum.Enum):
            etype = enum_item_type(type_)
        else:
            etype = type_
    elif not issubclass(origin, typing.Sequence):
        etype = type_
    elif issubclass(origin, typing.Tuple):
        etype = type_
    else:
        args = typing.get_args(type_)
        assert len(args) == 1
        etype = args[0]
    return etype

"""Utility functions and classes."""

import enum
import functools
import dataclasses

from typing import Type


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


def enum_item_type(enum_cls: Type[enum.Enum]) -> Type:
    """Return the type of the items of an enum.Enum.

    This function also checks that all items of an enum have the same
    (or compatible) type.
    """
    if not issubclass(enum_cls, enum.Enum):
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


def effective_type(type_):
    """Return the effective type (in case of enums return the item type)."""
    if type_ is not None and issubclass(type_, enum.Enum):
        etype = enum_item_type(type_)
    else:
        etype = type_
    return etype
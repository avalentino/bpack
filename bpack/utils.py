"""Utility functions and classes."""

import functools
import dataclasses


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
    return dataclasses._create_fn(name, args, body,
                                  globals=globals, locals=locals,
                                  return_type=return_type)


def set_new_attribute(cls, name, value):
    return dataclasses._set_new_attribute(cls, name, value)

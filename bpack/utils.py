"""Utility finctions and classes."""

import functools


def classdecorator(func):
    """Class decorator that can be used with or without parameters."""
    functools.wraps(func)

    def wrapper(cls=None, **kwargs):
        def wrap(cls):
            return func(cls, **kwargs)

        # Check if called as @decorator or @decorator(...).
        if cls is None:
            # Called with parentheses
            return wrap

        # Called as @decorator without parentheses
        return wrap(cls)

    return wrapper

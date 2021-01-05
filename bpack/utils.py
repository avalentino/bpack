"""Utility functions and classes."""

import re
import sys
import enum
import typing
import functools
import dataclasses
import collections.abc

from typing import NamedTuple, Optional, Type, Union
try:
    from typing import get_origin, get_args
except ImportError:
    # COMPATIBILITY
    from typing_extensions import get_origin, get_args


from.enums import EByteOrder


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
    """Programmatically add a new attribute/method to a class."""
    return dataclasses._set_new_attribute(cls, name, value)


def _get_forward_ref(ref):
    assert isinstance(ref, typing.ForwardRef)
    return ref.__forward_arg__  # TODO: check


def sequence_type(type_: Type, error: bool = False) -> Union[Type, None]:
    """Return the sequence type associated to a typed sequence.

    The function return :class:`list` or :class:`tuple` if the input is
    considered a valid typed sequence, ``None`` otherwise.

    Please note that fields annotated with :class:`typing.Tuple` are not
    considered homogeneous sequences even if all items are specified to
    have the same type.
    """
    sequence_type = get_origin(type_)
    if sequence_type is None:
        return None
    if not issubclass(sequence_type, typing.Sequence):
        return None
    args = get_args(type_)
    if len(args) < 1:
        return None
    if len(args) > 1:
        if error:
            raise TypeError(f'{type_} is not supported')
        else:
            return None
    if isinstance(args[0], typing.ForwardRef):
        typestr = _get_forward_ref(args[0])
        try:
            params = str_to_type_params(typestr)
        except (TypeError, ValueError):
            return None
        else:
            # TODO: drop
            assert isinstance(params.type, type)
    elif not isinstance(args[0], type):
        # COMPATIBILITY: with typing_extensions and Python v3.7
        # need to be a concrete type
        return None

    if not issubclass(sequence_type, collections.abc.MutableSequence):
        sequence_type = tuple

    assert sequence_type in {list, tuple}

    return sequence_type


def is_sequence_type(type_: Type, error: bool = False) -> bool:
    """Return True if the input is an homogeneous typed sequence.

    Please note that fields annotated with :class:`typing.Tuple` are not
    considered homogeneous sequences even if all items are specified to
    have the same type.
    """
    seq_type = sequence_type(type_, error=error)
    return seq_type is not None


def is_enum_type(type_: Type) -> bool:
    """Return True if the input is and :class:`enum.Enum`."""
    return get_origin(type_) is None and issubclass(type_, enum.Enum)


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


# TODO: Union[Type, str] -> Union[Type, str]
def effective_type(type_: Type, keep_typestr: bool = False) -> Type:
    """Return the effective type.

    In case of enums or sequences return the item type.
    """
    origin = get_origin(type_)
    if origin is None:
        if (type_ is not None and not isinstance(type_, str) and
                issubclass(type_, enum.Enum)):
            etype = enum_item_type(type_)
        else:
            etype = type_
    elif not issubclass(origin, typing.Sequence):
        etype = type_
    elif issubclass(origin, typing.Tuple):
        etype = type_
    else:
        args = get_args(type_)
        assert len(args) == 1
        etype = args[0]

    if isinstance(etype, typing.ForwardRef):
        etype = _get_forward_ref(etype)

    if isinstance(etype, str) and not keep_typestr:
        try:
            params = str_to_type_params(etype)
        except (TypeError, ValueError):
            pass
        else:
            etype = params.type

    return etype


def is_int_type(type_: Type) -> bool:
    """Return true if the effective type is an integer."""
    if is_sequence_type(type_):
        etype = effective_type(type_)
        return issubclass(etype, int)
    else:
        return issubclass(type_, int)


_DTYPE_RE = re.compile(
    r'^(?P<byteorder>[<|>])?'
    r'(?P<type>[?bBiufcmMUVOSat])'
    r'(?P<size>\d+)?$')


FieldTypes = Type[Union[bool, int, float, complex, bytes, str]]


class TypeParams(NamedTuple):
    byteorder: Optional[EByteOrder]
    type: FieldTypes
    size: int
    signed: Optional[bool]

    def __repr__(self):
        byteorder = self.byteorder
        byteorder = repr(byteorder) if byteorder is not None else byteorder
        size = str(self.size) if self.size is not None else self.size
        return (
            f'{self.__class__.__name__}(byteorder={byteorder}, '
            f'type={self.type.__name__!r}, size={size})'
        )


def str_to_type_params(typestr: str) -> TypeParams:
    """Convert a string describing a data type into type parameters.

    The ``typestr`` parameter is a string describing a data type.

    The *typestr* string format consists of 3 parts:

    * an (optional) character describing the byte order of the data

      - ``<``: little-endian,
      - ``>``: big-endian,
      - ``|``: not-relevant

    * a character code giving the basic type of the array, and
    * an integer providing the number of bytes the type uses

    The basic type character codes are:

    * ``i``: sighed integer
    * ``u``: unsigned integer
    * ``f``: float
    * ``c``: complex
    * ``S``: bytes (string)

    .. seealso:: https://numpy.org/doc/stable/reference/arrays.dtypes.html
       and https://numpy.org/doc/stable/reference/arrays.interface.html
    """
    mobj = _DTYPE_RE.match(typestr)
    if mobj is None:
        raise ValueError(f'invalid data type specifier: "{typestr}"')
    byteorder = mobj.group('byteorder')
    stype = mobj.group('type')
    size = mobj.group('size')
    signed = None

    if size is not None:
        size = int(size)
        if size <= 0:
            raise ValueError(f'invalid size: "{size}"')

    if byteorder == '|':
        byteorder = None
    elif byteorder is not None:
        byteorder = EByteOrder(byteorder)

    # if stype == '?' or (stype == 'b' and size == 1):
    #     type_ = bool
    # elif stype in 'bB':
    #     type_ = bytes
    # elif stype == 'i':
    if stype == 'i':
        type_ = int
        signed = True
    elif stype == 'u':
        type_ = int
        signed = False
    elif stype == 'f':
        type_ = float
    elif stype == 'c':
        type_ = complex
    # elif stype == 'm':
    #     type_ = datetime.timedelta
    # elif stype == 'M':
    #     type_ = datetime.datetime
    # elif stype == 'U':
    #     type_ = str
    elif stype == 'S':
        type_ = bytes
    # elif stype == 'V':
    #     type_ = bytes
    else:
        # '?': bool
        # 'b': (signed) byte (single item)
        # 'B': (unsigned) byte (single item)
        # 't': bitfield
        # 'O': object
        # 'U': (unicode) str (32bit UCS4 encoding)
        # 'a' : null terminated strings
        # 'm', 'M': timedelta and datetime
        raise TypeError(
            f'type specifier "{stype}" is valid for the "array protocol" but '
            f'not supported by bpack')

    return TypeParams(byteorder, type_, size, signed)

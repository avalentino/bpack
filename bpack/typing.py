"""bpack support for type annotations."""

import re
from typing import Annotated, NamedTuple, Optional, Union, get_args, get_origin

# @COMPATIBILITY: available in Python 3.7 ... 3.11
try:
    from typing import _tp_cache
except ImportError:

    def _tp_cache(x):
        return x


from .enums import EByteOrder

__all__ = ["T", "TypeParams", "is_annotated"]


_DTYPE_RE = re.compile(
    r"^(?P<byteorder>[<|>])?" r"(?P<type>[?bBiufcmMUVOSat])" r"(?P<size>\d+)?$"
)


FieldTypes = type[Union[bool, int, float, complex, bytes, str]]


class TypeParams(NamedTuple):
    """Named tuple describing type parameters."""

    byteorder: Optional[EByteOrder]
    type: FieldTypes  # noqa: A003
    size: Optional[int]
    signed: Optional[bool]

    def __repr__(self):
        """Return the string representation of the TypeParams object."""
        byteorder = self.byteorder
        byteorder = repr(byteorder) if byteorder is not None else byteorder
        size = str(self.size) if self.size is not None else self.size
        return (
            f"{self.__class__.__name__}(byteorder={byteorder}, "
            f"type={self.type.__name__!r}, size={size}, signed={self.signed})"
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

    .. note:: *typestr* the format described above is a sub-set of the
       one used in the numpy "array interface".

    .. seealso:: https://numpy.org/doc/stable/reference/arrays.dtypes.html
       and https://numpy.org/doc/stable/reference/arrays.interface.html
    """
    mobj = _DTYPE_RE.match(typestr)
    if mobj is None:
        raise ValueError(f"invalid data type specifier: '{typestr}'")
    byteorder = mobj.group("byteorder")
    stype = mobj.group("type")
    size = mobj.group("size")
    signed = None

    if size is not None:
        size = int(size)
        if size <= 0:
            raise ValueError(f"invalid size: '{size}'")

    if byteorder == "|":
        byteorder = None
    elif byteorder is not None:
        byteorder = EByteOrder(byteorder)

    # if stype == '?' or (stype == 'b' and size == 1):
    #     type_ = bool
    # elif stype in 'bB':
    #     type_ = bytes
    # elif stype == 'i':
    if stype == "i":
        type_ = int
        signed = True
    elif stype == "u":
        type_ = int
        signed = False
    elif stype == "f":
        type_ = float
    elif stype == "c":
        type_ = complex
    # elif stype == 'm':
    #     type_ = datetime.timedelta
    # elif stype == 'M':
    #     type_ = datetime.datetime
    # elif stype == 'U':
    #     type_ = str
    elif stype == "S":
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
            f"type specifier '{stype}' is valid for the 'array protocol' but "
            f"not supported by bpack"
        )

    return TypeParams(byteorder, type_, size, signed)


def type_params_to_str(params: TypeParams) -> str:
    """Convert a ``TypeParams`` object into a ``typestr``.

    The returned ``typestr`` is a string describing a data type.

    .. seealso:: please refer to :func:`bpack.typing.str_to_type_params`
       for a detailed description of the *typestr* string format.
    """
    byteorder = params.byteorder
    byteorder = "" if byteorder is None else EByteOrder(byteorder).value

    if params.type is int:
        if params.signed:
            type_ = "i"
        else:
            type_ = "u"
    elif params.type is float:
        type_ = "f"
    elif params.type is complex:
        type_ = "c"
    # elif params.type is datetime.timedelta:
    #     type_ = "m"
    # elif params.type is datetime.datetime:
    #     type_ = "M"
    # elif params.type is str:
    #     type_ = "U"
    elif params.type is bytes:
        type_ = "S"
        # type_ = "V"
    else:
        raise TypeError(f"data type '{params.type}' is not supported in bpack")

    size = params.size if params.size is not None else ""

    return f"{byteorder}{type_}{size}"


class T:
    """Allow to specify numeric type annotations using string descriptors.

    Example::

      >>> T['u4']                           # doctest: +NORMALIZE_WHITESPACE
      typing.Annotated[int, TypeParams(byteorder=None,
                       type='int', size=4, signed=False)]

    The resulting type annotation is a :class:`typing.Annotated` numeric type
    with attached a :class:`bpack.typing.TypeParams` instance.

    String descriptors, or *typestr*, are compatible with numpy (a sub-set
    of one used in the numpy "array interface").

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

    .. note:: *typestr* the format described above is a sub-set of the
       one used in the numpy "array interface".

    .. seealso:: :func:`str_to_type_params`, :class:`TypeParams`,
       https://numpy.org/doc/stable/reference/arrays.dtypes.html and
       https://numpy.org/doc/stable/reference/arrays.interface.html
    """

    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        """Initialize a new `T` descriptor."""
        raise TypeError(f"Type '{cls.__name__}' cannot be instantiated.")

    @_tp_cache
    def __class_getitem__(cls, params):  # noqa: D105, N805
        if not isinstance(params, str):
            raise TypeError(
                f"{cls.__name__}[...] should be used with a single argument "
                f"(a string describing a basic numeric type)."
            )
        typestr = params
        metadata = str_to_type_params(typestr)
        return Annotated[metadata.type, metadata]

    def __init_subclass__(cls, *args, **kwargs):
        """Subclass initializer.

        Alway raise a TypeError to prevent sub-classing.
        """
        raise TypeError(f"Cannot subclass {cls.__module__}.{cls.__name__}")


def is_annotated(type_: type) -> bool:
    """Return True if the input is an annotated numeric type.

    An *annotated numeric type* is assumed to be a :class:`typing.Annotated`
    type annotation of a basic numeric type with attached a
    :class:`bpack.typing.TypeParams` instance.

    .. seealso:: :class:`bpack.typing.T`.
    """
    if get_origin(type_) is Annotated:
        args = get_args(type_)
        if len(args) == 2:
            etype, params = args
            return isinstance(etype, type) and isinstance(params, TypeParams)
    return False

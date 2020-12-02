"""Descriptors for binary records."""

import enum
import math
import types
import warnings
import dataclasses
import collections.abc
from typing import Optional, Tuple

from . import utils
from .utils import classdecorator


__all__ = [
    'descriptor', 'field', 'Field', 'fields', 'is_descriptor', 'is_field',
    'calcsize', 'EBaseUnits', 'get_baseunits',
]


BASEUNITS_ATTR_NAME = '__bpack_baseunits__'


class EBaseUnits(enum.Enum):
    """Base units used to specify size and offset parameters in descriptors."""

    BITS = 'bits'
    BYTES = 'bytes'


class Field(dataclasses.Field):
    """Descriptor for binary fields.

    This class inherits form :class:`dataclass.Field` and adds the
    the possibility to describe easily the size of the binary field
    and, optionally, its offset with respect to the beginning of the
    binary record.
    """

    def __init__(self, **kwargs):
        metadata = kwargs.setdefault('metadata', {})

        offset = kwargs.pop('offset', None)
        if offset is not None:
            if not isinstance(offset, int):
                raise TypeError(
                    f'invalid offset: {offset!r}: must be a positive integer')
            if offset < 0:
                raise ValueError(
                    f'invalid offset: {offset!r}: '
                    f'must be a positive or null integer')
            metadata['offset'] = offset

        size = kwargs.pop('size', None)
        if size is not None:
            if not isinstance(size, int):
                raise TypeError(
                    f'invalid size: {size!r}: must be a positive integer')
            if size <= 0:
                raise ValueError(
                    f'invalid size: {size!r}: must be a positive integer')
            metadata['size'] = size
        else:
            # TODO: add automatic size determination form type (in descriptor)
            raise TypeError('no field size specified')

        field_ = dataclasses.field(**kwargs)
        super().__init__(field_.default,
                         field_.default_factory,
                         field_.init,
                         field_.repr,
                         field_.hash,
                         field_.compare,
                         field_.metadata)

    @property
    def offset(self) -> int:
        """Offset form the beginning of the record (in baseunits).

        .. seealso: :func:`bpack.descriptor.descriptor`.
        """
        return self.metadata['offset']

    @property
    def size(self) -> int:
        """Size of the field (in baseunits).

        .. seealso: :func:`bpack.descriptor.descriptor`.
        """
        return self.metadata['size']

    def __repr__(self) -> str:
        """Return the string representation of the Field object."""
        return super().__repr__().replace(dataclasses.Field.__name__,
                                          self.__class__.__name__)

    def _update_metadata(self, **kwargs):
        metadata = dict(self.metadata)
        metadata.update(**kwargs)
        self.metadata = types.MappingProxyType(metadata)


field = Field


def is_field(obj) -> bool:
    """Return true if an ``obj`` can be considered is a descriptor field."""
    if (issubclass(obj.type, Field) or
            (hasattr(obj, 'offset') and hasattr(obj, 'size'))):
        return True
    else:
        return False


class DescriptorConsistencyError(ValueError):
    pass


# TODO: units attribute (TBD)
# TODO: signed attribute
# TODO: repeat attribute
# TODO: converters (TBD, or in decoder)
# TODO: order for byte/bit order
@classdecorator
def descriptor(cls, size: Optional[int] = None,
               baseunits: EBaseUnits = EBaseUnits.BYTES):
    """Class decorator to define descriptors for binary records.

    It converts a dataclass into a descriptor object for binary records.

    * ensures that all fields are :class:`bpack.descriptor.Field` descriptors
    * offsets are automatically computed if necessary
    * consistency checks on offsets and sizes are performed
    * the ``__len__`` special method is added (returning always the
      record size in bytes).
    """
    fields_ = dataclasses.fields(cls)

    # replace dataclasses.Field with descriptors.Field if necessary
    # WARNING: this operation relies on implementation details
    fields_dict = getattr(cls, dataclasses._FIELDS)
    for field_ in fields_:
        assert isinstance(field_, dataclasses.Field)
        if not isinstance(field_, Field):
            new_field = field(default=field_.default,
                              default_factory=field_.default_factory,
                              init=field_.init,
                              repr=field_.repr,
                              hash=field_.hash,
                              compare=field_.compare,
                              metadata=field_.metadata,
                              # size id mandatory in the current implementation
                              size=None)
            new_field.name = field_.name
            new_field.type = field_.type
            fields_dict[field_.name] = new_field

    field_ = fields_[0]
    if field_.metadata.get('offset') is None:
        field_._update_metadata(offset=0)

    for idx, field_ in enumerate(fields_[1:], start=1):
        auto_offset = fields_[idx - 1].offset + fields_[idx - 1].size
        field_offset = field_.metadata.get('offset')
        if field_offset is not None:
            if field_offset < auto_offset:
                raise DescriptorConsistencyError(
                    f'invalid offset for filed n. {idx}: {field}')
        else:
            field_._update_metadata(offset=auto_offset)

        # TODO: auto-size
        # field_size = field_.metadata.get('size')
        # if size is None:
        #     assert field_.type is not None  # TODO: check in get size
        #     auto_size = get_size_for_type(field_.type)
        #     assert auto_size is not None
        #     field_._update_metadata(size=auto_size)

    content_size = sum(field_.size for field_ in fields_)
    field_ = fields_[-1]
    auto_size = field_.offset + field_.size
    assert auto_size >= content_size  # this should be already checked above

    if size is None:
        size = auto_size
    elif int(size) != size:
        raise TypeError(f'invalid size: {size!r}')
    elif size < auto_size:
        raise DescriptorConsistencyError(
            f'the specified size ({size}) is smaller than total size of '
            f'fields ({auto_size})')

    baseunits = EBaseUnits(baseunits)
    if baseunits is EBaseUnits.BITS:
        if size % 8 != 0:
            warnings.warn('bit struct not aligned to bytes')
        size = math.ceil(size / 8)

    setattr(cls, BASEUNITS_ATTR_NAME, baseunits)

    get_len_func = utils.create_fn(
        name='__len__',
        args=tuple(),
        body=['return size'],
        locals={'size': size},
    )
    get_len_func = staticmethod(get_len_func)
    get_len_func.__doc__ = "Return the record size in bytes"
    assert not hasattr(cls, '__len__')
    utils.set_new_attribute(cls, '__len__', get_len_func)
    collections.abc.Sized.register(cls)

    return cls


def is_descriptor(obj) -> bool:
    """Return true if ``obj`` is a descriptor or a descriptor instance."""
    try:
        return (hasattr(obj, BASEUNITS_ATTR_NAME) and
                is_field(dataclasses.fields(obj)[0]))
    except (TypeError, ValueError):
        # dataclass.fields(...) --> TypeError
        # attr.fields(...)      --> NotAnAttrsClassError(ValueError)
        return False
    except IndexError:
        # no fields
        return False


def calcsize(obj) -> int:
    """Return the size in bytes of the ``obj`` record."""
    if not is_descriptor(obj):
        raise TypeError(f'{obj!r} is not a descriptor')
    return obj.__len__()


def get_baseunits(obj) -> EBaseUnits:
    """Return the base units of a binary record descriptor."""
    try:
        return getattr(obj, BASEUNITS_ATTR_NAME)
    except AttributeError:
        raise TypeError(f'"{obj}" is not a descriptor')


def fields(descriptor_, pad=False) -> Tuple[Field, ...]:
    """Return a tuple containing fields of the specified descriptor.

    Items are instances of the :class:`Field` describing characteristics
    of each field of the input descriptor.

    If the ``pad`` parameter is set to True then also generate dummy fields
    describing the padding necessary to take into account of offsets.
    """
    if pad:
        fields_ = []
        offset = 0
        for field_ in dataclasses.fields(descriptor_):
            assert field_.offset >= offset
            if field_.offset > offset:
                # padding
                padfield = field(size=field_.offset - offset, offset=offset)
                assert padfield.type is None  # padding
                fields_.append(padfield)
                # offset = field.offset
            fields_.append(field_)
            offset = field_.offset + field_.size
        return tuple(fields_)
    else:
        return dataclasses.fields(descriptor_)

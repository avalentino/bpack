"""Binary data descriptors."""

import enum
import math
import types
import warnings
import dataclasses
from typing import Optional

from .utils import classdecorator


__all__ = [
    'EBaseUnits', 'is_record', 'is_field', 'fields', 'record_size',
    'Field', 'record',
]


class EBaseUnits(enum.Enum):
    BITS = 'bits'
    BYTES = 'bytes'


def is_record(obj):
    try:
        return isinstance(dataclasses.fields(obj)[0], Field)
    except (TypeError, ValueError):
        # dataclass.fields(...) --> TypeError
        # attr.fields(...)      --> NotAnAttrsClassError(ValueError)
        return False
    except IndexError:
        # no fields
        return False


def is_field(obj):
    if (issubclass(obj.type, Field) or
            (hasattr(obj, 'offset') and hasattr(obj, 'size'))):
        return True
    else:
        return False


fields = dataclasses.fields


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
            # TODO: add automatic size determination form type (in record)
            raise TypeError('no size specified')

        field = dataclasses.field(**kwargs)
        super().__init__(field.default,
                         field.default_factory,
                         field.init,
                         field.repr,
                         field.hash,
                         field.compare,
                         field.metadata)

    @property
    def offset(self):
        return self.metadata['offset']

    @property
    def size(self):
        return self.metadata['size']

    def __repr__(self):
        return super().__repr__().replace(dataclasses.Field.__name__,
                                          self.__class__.__name__)

    def _update_metadata(self, **kwargs):
        metadata = dict(self.metadata)
        metadata.update(**kwargs)
        self.metadata = types.MappingProxyType(metadata)


class RecordConsistencyError(ValueError):
    pass


@classdecorator
def record(cls, size: Optional[int] = None,
           baseunits: EBaseUnits = EBaseUnits.BYTES):
    """Class decorator to convert a dataclass into a record.

    * ensures that all fields are :class:`bpack.descriptor.Field` descriptors
    * offsets are automatically computed if necessary
    * consistency checks on offsets and sizes are performed
    * the ``__len__`` special method is added (returning always the
      record size in bytes).
    """
    fields = dataclasses.fields(cls)

    field = fields[0]
    if field.metadata.get('offset') is None:
        field._update_metadata(offset=0)

    for idx, field in enumerate(fields[1:], start=1):
        auto_offset = fields[idx - 1].offset + fields[idx - 1].size
        field_offset = field.metadata.get('offset')
        if field_offset is not None:
            if field_offset < auto_offset:
                raise RecordConsistencyError(
                    f'invalid offset for filed n. {idx}: {field}')
        else:
            field._update_metadata(offset=auto_offset)

        # TODO: auto-size
        # field_size = field.metadata.get('size')
        # if size is None:
        #     assert field.type is not None  # TODO: check in get size
        #     auto_size = get_size_for_type(field.type)
        #     assert auto_size is not None
        #     field._update_metadata(size=auto_size)

    content_size = sum(field.size for field in fields)
    field = fields[-1]
    auto_size = field.offset + field.size
    assert auto_size >= content_size  # this should be already checked above

    if size is None:
        size = auto_size
    elif int(size) != size:
        raise TypeError(f'invalid size: {size!r}')
    elif size < auto_size:
        raise RecordConsistencyError(
            f'the specified size ({size}) is smaller than total size of '
            f'fields ({auto_size})')

    baseunits = EBaseUnits(baseunits)
    if baseunits is EBaseUnits.BITS:
        if size % 8 != 0:
            warnings.warn('bit struct not aligned to bytes')
        size = math.ceil(size / 8)

    cls._BASEUNITS = baseunits

    get_len_func = dataclasses._create_fn(
        name='__len__',
        args=tuple(),
        body=['return size'],
        locals={'size': size},
    )
    get_len_func = staticmethod(get_len_func)
    get_len_func.__doc__ = "Return the record size in bytes"
    assert not hasattr(cls, '__len__')
    dataclasses._set_new_attribute(cls, '__len__', get_len_func)

    return cls


def record_size(obj):
    if not is_record(obj):
        raise TypeError(f'{obj!r} is not a record')
    return obj.__len__()

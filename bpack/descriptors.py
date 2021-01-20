"""Descriptors for binary records."""

import copy
import enum
import math
import types
import warnings
import dataclasses
from typing import Iterable, Optional, Sequence, Type, Union

import bpack.typing
import bpack.utils
from .utils import classdecorator
from .enums import EBaseUnits, EByteOrder, EBitOrder

__all__ = [
    'descriptor', 'is_descriptor', 'fields', 'asdict', 'calcsize',
    'baseunits', 'byteorder', 'bitorder', 'field', 'Field', 'is_field',
    'field_descriptors',
    'BinFieldDescriptor', 'get_field_descriptor', 'set_field_descriptor',
    'BASEUNITS_ATTR_NAME', 'BYTEORDER_ATTR_NAME', 'BITORDER_ATTR_NAME',
    'METADATA_KEY',
]


BASEUNITS_ATTR_NAME = '__bpack_baseunits__'
BYTEORDER_ATTR_NAME = '__bpack_byteorder__'
BITORDER_ATTR_NAME = '__bpack_bitorder__'
SIZE_ATTR_NAME = '__bpack_size__'
METADATA_KEY = '__bpack_metadata__'


class DescriptorConsistencyError(ValueError):
    pass


class NotFieldDescriptorError(TypeError):
    pass


def _resolve_type(type_):
    """Remove type annotations.

    Replace :class:`typing.Annotated` types with the corresponding
    not-annotated ones.
    """
    if bpack.utils.is_sequence_type(type_):
        etype = bpack.utils.effective_type(type_)
        rtype = copy.copy(type_)
        rtype.__args__ = (etype,)
    elif bpack.typing.is_annotated(type_):
        rtype = bpack.utils.effective_type(type_)
    else:
        rtype = type_
    return rtype


@dataclasses.dataclass
class BinFieldDescriptor:
    """Descriptor for bpack fields."""

    type: Optional[Type] = None
    size: Optional[int] = None          # item size
    offset: Optional[int] = None
    signed: Optional[bool] = None
    repeat: Optional[int] = None        # number of items
    # converter: Optional[Callable] = None

    def _validate_type(self):
        if self.type is None:
            raise TypeError(f'invalid type "{self.type}"')

    def _validate_size(self):
        msg = f'invalid size: {self.size!r} (must be a positive integer)'
        if not isinstance(self.size, int):
            raise TypeError(msg)
        if self.size <= 0:
            raise ValueError(msg)

    def _validate_offset(self):
        msg = f'invalid offset: {self.offset!r} (must be an integer >= 0)'
        if not isinstance(self.offset, int):
            raise TypeError(msg)
        if self.offset < 0:
            raise ValueError(msg)

    def _validate_signed(self):
        if not isinstance(self.signed, bool):
            raise TypeError(
                f'invalid "signed" parameter: {self.signed!r} '
                f'(must be a bool or None)')

    def _validate_repeat(self):
        msg = f'invalid repeat: {self.repeat!r} (must be a positive)'
        if not isinstance(self.repeat, int):
            raise TypeError(msg)
        if self.repeat < 1:
            raise ValueError(msg)

    def _validate_enum_type(self):
        assert issubclass(self.type, enum.Enum)
        # perform checks on supported enum.Enum types
        bpack.utils.enum_item_type(self.type)

    def __post_init__(self):
        """Finalize BinFieldDescriptor instance initialization."""
        if self.offset is not None:
            self._validate_offset()

        if self.size is not None:
            self._validate_size()

        if self.signed is not None:
            self._validate_signed()

        if self.repeat is not None:
            self._validate_repeat()

    def validate(self):
        """Perform validity check on the BinFieldDescriptor instance."""
        self._validate_type()
        self._validate_size()
        if self.offset is not None:
            self._validate_offset()
        if self.signed is not None:
            self._validate_signed()
            if not self.is_int_type():
                warnings.warn(
                    f'the "signed" parameter will be ignored for non-integer '
                    f'type: "{self.type}"')
        if self.repeat is not None:
            self._validate_repeat()
            if not self.is_sequence_type() and self.repeat is not None:
                raise TypeError(
                    f'repeat parameter specified for non-sequence type: '
                    f'{self.type}')
        if bpack.utils.is_enum_type(self.type):
            self._validate_enum_type()
        elif self.is_sequence_type() and self.repeat is None:
            raise TypeError(
                f'no "repeat" parameter specified for sequence type '
                f'{self.type}')

    def is_int_type(self) -> bool:
        return bpack.utils.is_int_type(self.type)

    def is_sequence_type(self) -> bool:
        return bpack.utils.is_sequence_type(self.type, error=True)

    def is_enum_type(self) -> bool:
        return bpack.utils.is_enum_type(self.type)

    @property
    def total_size(self):
        """Total size in bytes of the field (considering all item)."""
        repeat = self.repeat if self.repeat is not None else 1
        return self.size * repeat

    @staticmethod
    def _is_compatible_param(old, new):
        if old is not None and new is not None and old != new:
            return False
        return True

    def update_from_type(self, type_: Type):
        if self.type is not None:
            raise TypeError('the type attribute is already set')
        if bpack.typing.is_annotated(type_):
            _, params = bpack.typing.get_args(type_)
            valid = True
            if not self._is_compatible_param(self.size, params.size):
                valid = False
            if not self._is_compatible_param(self.signed, params.signed):
                valid = False
            if not valid:
                raise DescriptorConsistencyError(
                    f'type string "{params}" is incompatible with the '
                    f'field descriptor {self}')

            self.type = params.type
            if self.signed is None:
                self.signed = params.signed
            if self.size is None:
                self.size = params.size
        elif bpack.utils.is_sequence_type(type_):
            etype = bpack.utils.effective_type(type_, keep_annotations=True)
            self.update_from_type(etype)
            self.type = _resolve_type(type_)
        else:
            self.type = type_


Field = dataclasses.Field


def field(*, size: Optional[int] = None, offset: Optional[int] = None,
          signed: Optional[bool] = None, repeat: Optional[int] = None,
          metadata=None, **kwargs) -> Field:
    """Initialize a field descriptor.

    Returned object is a :class:`Field` instance with metadata properly
    initialized to describe the field of a binary record.
    """
    field_descr = BinFieldDescriptor(size=size, offset=offset, signed=signed,
                                     repeat=repeat)
    metadata = metadata.copy() if metadata is not None else {}
    metadata[METADATA_KEY] = types.MappingProxyType(
        dataclasses.asdict(field_descr))
    return dataclasses.field(metadata=metadata, **kwargs)


def is_field(obj) -> bool:
    """Return true if an ``obj`` can be considered is a field descriptor."""
    return (isinstance(obj, Field) and obj.metadata and
            METADATA_KEY in obj.metadata)


def _update_field_metadata(field_, **kwargs):
    metadata = field_.metadata.copy() if field_.metadata is not None else {}
    metadata.update(**kwargs)
    field_.metadata = types.MappingProxyType(metadata)
    return field_


def get_field_descriptor(field: Field,                                  # noqa
                         validate: bool = True) -> BinFieldDescriptor:
    """Return the field descriptor attached to a :class:`Field`."""
    if not is_field(field):
        raise NotFieldDescriptorError(f'not a field descriptor: {field}')
    field_descr = BinFieldDescriptor(**field.metadata[METADATA_KEY])
    field_descr.update_from_type(field.type)
    if validate:
        field_descr.validate()
    return field_descr


def set_field_descriptor(field: Field, descriptor: BinFieldDescriptor,  # noqa
                         validate: bool = True) -> Field:
    """Set the field metadata according to the specified descriptor."""
    if validate:
        descriptor.validate()
    field_descr_metadata = {
        k: v for k, v in dataclasses.asdict(descriptor).items()
        if v is not None
    }
    type_ = field_descr_metadata.pop('type', None)
    if bpack.typing.is_annotated(field.type):
        field_type, _ = bpack.typing.get_args(field.type)
    else:
        field_type = field.type
    if type_ != _resolve_type(field_type):
        raise TypeError(
            f'type mismatch between BinFieldDescriptor.type ({type_!r}) and '
            f'filed.type ({field.type!r})')
    new_metadata = {
        METADATA_KEY: types.MappingProxyType(field_descr_metadata),
    }
    _update_field_metadata(field, **new_metadata)
    return field


_DEFAULT_SIZE_MAP = {
    EBaseUnits.BYTES: {
        bool: 1,
        # int: 4,
        # float: 4,
    },
    EBaseUnits.BITS: {
        bool: 1,
        # int: 32,
        # float: 32,
    },
}


def _get_default_size(type_,
                      baseunits: EBaseUnits) -> Union[int, None]:       # noqa
    if is_descriptor(type_):
        return calcsize(type_, baseunits)

    etype = bpack.utils.effective_type(type_)

    # if bpack.utils.is_enum_type(type_):
    #     if bpack.utils.is_int_type(type_):
    #         signbit = 1 if any(item.value < 0 for item in type_) else 0
    #         bits = signbit + max(item.value.bit_lenght() for item in type_)
    #         if baseunits is EBaseUnits.BITS:
    #             if bits <= 8:
    #                 return 1
    #             elif bits <= 16:
    #                 return 2
    #             elif bits <= 32:
    #                 return 4
    #             else:
    #                 return 8
    #         else:
    #             return bits
    #     elif issubclass(etype, str):
    #         length = max(len(item.value.encode('utf-8')) for item in type_)
    #         return length * bytes_to_baseunits
    #     elif issubclass(etype, bytes):
    #         length = max(len(item.value) for item in type_)
    #         return length * bytes_to_baseunits
    #     else:
    #         return None

    return _DEFAULT_SIZE_MAP[baseunits].get(etype)                      # noqa


def _get_effective_byteorder(byteorder: EByteOrder,                     # noqa
                             baseunits: EBaseUnits) -> EByteOrder:      # noqa
    byteorder = EByteOrder(byteorder)                                   # noqa
    effective_byteorder = byteorder
    if baseunits is EBaseUnits.BYTES:
        if byteorder in {EByteOrder.NATIVE, EByteOrder.DEFAULT}:
            effective_byteorder = EByteOrder.get_native()
    else:
        if byteorder is EByteOrder.DEFAULT:
            effective_byteorder = EByteOrder.BE
        elif byteorder in EByteOrder.NATIVE:
            effective_byteorder = EByteOrder.get_native()
    return effective_byteorder


@classdecorator
def descriptor(cls, *, size: Optional[int] = None,
               byteorder: Union[str, EByteOrder] = EByteOrder.DEFAULT,  # noqa
               bitorder: Optional[Union[str, EBitOrder]] = None,        # noqa
               baseunits: EBaseUnits = EBaseUnits.BYTES,                # noqa
               **kwargs):
    """Class decorator to define descriptors for binary records.

    It converts a dataclass into a descriptor object for binary records.

    * ensures that all fields are :class:`bpack.descriptor.Field` descriptors
    * offsets are automatically computed if necessary
    * consistency checks on offsets and sizes are performed

    :param cls:
        class to be decorated
    :param size:
        the size (expressed in *base units*) of the binary record
    :param byteorder:
        the byte-order of the binary record
    :param bitorder:
        the bit-order of the binary record
        (must be ``None`` if the *base units* are bytes).
        If set to none in bit-based records it is assumed
        :data:`bpack.enums.EBitOrder.DEFAULT` which corresponds to
        :data:`bpack.enums.EBitOrder.MSB` in all decoders currently
        implemented.
    :param baseunits:
        the base units (:data:`bpack.enums.EBaseUnits.BITS` or
        :data:`bpack.enums.EBaseUnits.BYTES`) used to specify the
        binary record descriptor

    It is also possible to specify as additional keyword arguments all the
    parameters accepted by :func:`dataclasses.dataclass`.
    """
    baseunits = EBaseUnits(baseunits)                                   # noqa
    byteorder = EByteOrder(byteorder)                                   # noqa

    if dataclasses.is_dataclass(cls):
        warnings.warn('the explicit use of dataclasses is deprecated',
                      category=DeprecationWarning)
    else:
        cls = dataclasses.dataclass(cls, **kwargs)

    fields_ = dataclasses.fields(cls)

    # Initialize to a dummy value with initial offset + size = 0
    prev_field_descr = BinFieldDescriptor(size=None, offset=0)
    prev_field_descr.size = 0  # trick to bypass checks on BinFieldDescriptor
    content_size = 0

    for idx, field_ in enumerate(fields_):
        assert isinstance(field_, Field)

        # NOTE: this is ensured by dataclasses but not by attr
        assert field_.type is not None

        if bpack.typing.is_annotated(field_.type):
            # check byteorder
            _, params = bpack.typing.get_args(field_.type)
            if params.byteorder:
                effective_byteorder = _get_effective_byteorder(byteorder,
                                                               baseunits)
                if params.byteorder != effective_byteorder:
                    raise DescriptorConsistencyError(
                        f'the byteorder of field {field_.name} '
                        f'("{params.byteorder}" is not consistent with the '
                        f'descriptor byteorder ({byteorder}) )')

        try:
            field_descr = get_field_descriptor(field_, validate=False)
        except NotFieldDescriptorError:
            field_descr = BinFieldDescriptor()
            if isinstance(field_, Field):
                field_descr.update_from_type(field_.type)

        if field_descr.size is None:
            field_descr.size = _get_default_size(field_descr.type, baseunits)

        if field_descr.size is None:
            raise TypeError(f'size not specified for field: "{field_.name}"')

        if (is_descriptor(field_descr.type) and
                calcsize(field_descr.type, baseunits) != field_descr.size):
            raise DescriptorConsistencyError(
                f'mismatch between field.size ({field_descr.size}) and size '
                f'of field.type ({calcsize(field_descr.type, baseunits)}) '
                f'in field "{field_.name}"')

        auto_offset = prev_field_descr.offset + prev_field_descr.total_size

        if field_descr.offset is None:
            field_descr.offset = auto_offset
        elif field_descr.offset < auto_offset:
            raise DescriptorConsistencyError(
                f'invalid offset for filed n. {idx}: {field_}')

        set_field_descriptor(field_, field_descr)
        prev_field_descr = field_descr
        content_size += field_descr.size

    field_descr = get_field_descriptor(fields_[-1])
    auto_size = field_descr.offset + field_descr.total_size
    assert auto_size >= content_size  # this should be already checked above

    if size is None:
        size = auto_size
    elif int(size) != size:
        raise TypeError(f'invalid size: {size!r}')
    elif size < auto_size:
        raise DescriptorConsistencyError(
            f'the specified size ({size}) is smaller than total size of '
            f'fields ({auto_size})')

    if baseunits is EBaseUnits.BITS:
        if size % 8 != 0:
            warnings.warn('bit struct not aligned to bytes')

    if baseunits is not EBaseUnits.BITS and bitorder is not None:
        raise ValueError(
            'it is not possible to specify the "bitorder" '
            'if "baseunits" is not "BITS"')
    elif baseunits is EBaseUnits.BITS and bitorder is None:
        bitorder = EBitOrder.DEFAULT                                    # noqa

    setattr(cls, BASEUNITS_ATTR_NAME, baseunits)
    setattr(cls, BYTEORDER_ATTR_NAME, byteorder)
    setattr(cls, BITORDER_ATTR_NAME,
            EBitOrder(bitorder) if bitorder is not None else None)
    setattr(cls, SIZE_ATTR_NAME, size)

    return cls


def fields(obj) -> Sequence[Field]:
    """Return a tuple describing the fields of this descriptor."""
    return dataclasses.fields(obj)                                      # noqa


def is_descriptor(obj) -> bool:
    """Return true if ``obj`` is a descriptor or a descriptor instance."""
    try:
        return hasattr(obj, BASEUNITS_ATTR_NAME) and is_field(fields(obj)[0])
    except (TypeError, ValueError):
        # dataclass.fields(...) --> TypeError
        # attr.fields(...)      --> NotAnAttrsClassError(ValueError)
        return False
    except IndexError:
        # no fields
        return False


def asdict(obj, *, dict_factory=dict) -> dict:
    """Return the fields of a record as a new dictionary.

     The returned dictionary maps field names to field values.

    If given, 'dict_factory' will be used instead of built-in dict.
    The function applies recursively to field values that are
    dataclass instances. This will also look into built-in containers:
    tuples, lists, and dicts.
    """
    return dataclasses.asdict(obj, dict_factory=dict_factory)


def calcsize(obj, units: Optional[EBaseUnits] = None) -> int:
    """Return the size of the ``obj`` record.

    If the *units* parameter is not specified (default) then the returned
    *size* is expressed in the same *base units* of the descriptor.
    """
    if not is_descriptor(obj):
        raise TypeError(f'{obj!r} is not a descriptor')

    size = getattr(obj, SIZE_ATTR_NAME)
    baseunits_ = getattr(obj, BASEUNITS_ATTR_NAME)

    if units and units is not baseunits_:
        if units is EBaseUnits.BYTES:
            # baseunits is BITS and units is BYTES
            size = math.ceil(size / 8)
        else:
            # baseunits is BYTES and units is BITS
            size *= 8

    return size


def baseunits(obj) -> EBaseUnits:
    """Return the base units of a binary record descriptor."""
    try:
        return getattr(obj, BASEUNITS_ATTR_NAME)
    except AttributeError:
        raise TypeError(f'"{obj}" is not a descriptor')


def byteorder(obj) -> EByteOrder:
    """Return the byte order of a binary record descriptor (endianess)."""
    try:
        return getattr(obj, BYTEORDER_ATTR_NAME)
    except AttributeError:
        raise TypeError(f'"{obj}" is not a descriptor')


def bitorder(obj) -> Union[EBitOrder, None]:
    """Return the bit order of a binary record descriptor."""
    try:
        return getattr(obj, BITORDER_ATTR_NAME)
    except AttributeError:
        raise TypeError(f'"{obj}" is not a descriptor')


def field_descriptors(descriptor,                                       # noqa
                      pad: bool = False) -> Iterable[BinFieldDescriptor]:
    """Return the list of field descriptors for the input record descriptor.

    Items are instances of the :class:`BinFieldDescriptor` class describing
    characteristics of each field of the input binary record descriptor.

    If the ``pad`` parameter is set to True then also generate dummy field
    descriptors for padding elements necessary to take into account offsets
    between fields.
    """
    if pad:
        offset = 0
        for field_ in fields(descriptor):
            field_descr = get_field_descriptor(field_)
            assert field_descr.offset >= offset
            if field_descr.offset > offset:
                # padding
                yield BinFieldDescriptor(size=field_descr.offset - offset,
                                         offset=offset)
                # offset = field_.offset
            yield field_descr
            offset = field_descr.offset + field_descr.total_size

        size = calcsize(descriptor)
        if offset < size:
            # padding
            yield BinFieldDescriptor(size=size - offset, offset=offset)
    else:
        for field_ in fields(descriptor):
            yield get_field_descriptor(field_)

# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT-License
# Created: 2019-02-18
from typing import TYPE_CHECKING, KeysView, ItemsView, Any, Union, Dict
import logging
from ezdxf.lldxf import validator
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXFKeyError, DXFValueError
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, RETURN_DEFAULT,
)
from ezdxf.audit import AuditError
from .dxfentity import base_class, SubclassProcessor, DXFEntity
from .dxfobj import DXFObject
from .factory import register_entity

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace, Auditor

__all__ = ['Dictionary', 'DictionaryWithDefault', 'DictionaryVar']

acdb_dictionary = DefSubclass('AcDbDictionary', {
    # If set to 1, indicates that elements of the dictionary are to be treated
    # as hard-owned:
    'hard_owned': DXFAttr(
        280, default=0, optional=True,
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),

    # Duplicate record cloning flag (determines how to merge duplicate entries):
    # 0 = not applicable
    # 1 = keep existing
    # 2 = use clone
    # 3 = <xref>$0$<name>
    # 4 = $0$<name>
    # 5 = Unmangle name
    'cloning': DXFAttr(
        281, default=1,
        validator=validator.is_in_integer_range(0, 6),
        fixer=RETURN_DEFAULT,
    ),
    # 3: entry name
    # 350: entry handle, some DICTIONARY objects have 360 as handle group code,
    # this is accepted by AutoCAD but not documented by the DXF reference!
    # ezdxf replaces group code 360 by 350.
})

KEY_CODE = 3
VALUE_CODE = 350
# Some DICTIONARY use group code 360:
SEARCH_CODES = (VALUE_CODE, 360)


@register_entity
class Dictionary(DXFObject):
    """
    AutoCAD maintains items such as mline styles and group definitions as
    objects in dictionaries. Other applications are free to create and use
    their own dictionaries as they see fit. The prefix "ACAD_" is reserved
    for use by AutoCAD applications.

    Dictionary entries are (key, DXFEntity) pairs. DXFEntity could be a string,
    because at loading time not all objects are already stored in the EntityDB,
    and have to acquired later.

    """
    DXFTYPE = 'DICTIONARY'
    DXFATTRIBS = DXFAttributes(base_class, acdb_dictionary)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self._data: Dict[str, Union[str, DXFEntity]] = dict()
        self._value_code = VALUE_CODE

    def _copy_data(self, entity: 'Dictionary') -> None:
        """ Copy hard owned entities but do not store the copies in the entity
        database, this is a second step, this is just real copying.

        """
        # todo: what about reactors of cloned DXF objects?
        entity._value_code = self._value_code
        if self.dxf.hard_owned:
            entity._data = {key: entity.copy() for key, entity in self.items()}
        else:
            entity._data = {key: entity for key, entity in self.items()}

    def _add_data_to_db(self) -> None:
        """ Add hard owned and therefore copied entities into database and the
        objects section.
        """
        # todo: don't know how to proceed with reactors of cloned objects?
        if self.dxf.hard_owned:
            my_handle = self.dxf.handle
            for _, entity in self.items():
                entity.dxf.owner = my_handle
                entity.dxf.handle = None
                self.entitydb.add(entity)
                # Add sub-entities also to the objects section, else they
                # wouldn't be exported to DXF:
                self.doc.objects.add_object(entity)

    def load_dxf_attribs(self,
                         processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(
                dxf, acdb_dictionary
            )
            self.load_dict(tags)
        return dxf

    def load_dict(self, tags):
        entry_handle = None
        dict_key = None
        value_code = VALUE_CODE
        for code, value in tags:
            if code in SEARCH_CODES:
                # First store handles, because at this point, NOT all objects
                # are stored in the EntityDB, at first access convert the handle
                # to a DXFEntity object.
                value_code = code
                entry_handle = value
            elif code == KEY_CODE:
                dict_key = value
            if dict_key and entry_handle:
                try:
                    entity = self.entitydb[entry_handle]
                except KeyError:
                    # Store entity as handle string:
                    entity = entry_handle

                self._data[dict_key] = entity
                entry_handle = None
                dict_key = None
        # Use same value code as loaded:
        self._value_code = value_code

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)

        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_dictionary.name)
        self.dxf.export_dxf_attribs(tagwriter, ['hard_owned', 'cloning'])
        self.export_dict(tagwriter)

    def export_dict(self, tagwriter: 'TagWriter'):
        # key: dict key string
        # value: DXFEntity or handle as string
        # Ignore invalid handles at export, because removing can create an empty
        # dictionary, which is more a problem for AutoCAD than invalid handles,
        # and removing the whole dictionary is maybe also a problem.
        for key, value in self._data.items():
            tagwriter.write_tag2(KEY_CODE, key)
            # Value can be a handle string or a DXFEntity object:
            if isinstance(value, DXFEntity):
                if value.is_alive:
                    value = value.dxf.handle
                else:
                    logger.debug(
                        f'Key "{key}" points to a destroyed entity '
                        f'in {str(self)}, target replaced by "0" handle.'
                    )
                    value = '0'
            # Use same value code as loaded:
            tagwriter.write_tag2(self._value_code, value)

    @property
    def is_hard_owner(self) -> bool:
        """ ``True`` if :class:`Dictionary` is hard owner of entities. Hard
        owned entities will be deleted by deleting the dictionary.

        """
        return bool(self.dxf.hard_owned)

    def keys(self) -> KeysView:
        """ Returns :class:`KeysView` of all dictionary keys. """
        return self._data.keys()

    def items(self) -> ItemsView:
        """ Returns :class:`ItemsView` for all dictionary entries as
        (:attr:`key`, :class:`DXFEntity`) pairs.

        """
        for key in self.keys():
            yield key, self.get(key)  # maybe handle -> DXFEntity

    def __getitem__(self, key: str) -> 'DXFEntity':
        """ Return the value for `key`, raises a :class:`DXFKeyError` if `key`
        does not exist.

        """
        return self.get(key)

    def __setitem__(self, key: str, value: 'DXFEntity') -> None:
        """ Add item as ``(key, value)`` pair to dictionary.  """
        return self.add(key, value)

    def __delitem__(self, key: str) -> None:
        """ Delete entry `key` from the dictionary, raises :class:`DXFKeyError`
        if key does not exist.

        """
        return self.remove(key)

    def __contains__(self, key: str) -> bool:
        """ Returns ``True`` if `key` exist. """
        return key in self._data

    def __len__(self) -> int:
        """ Returns count of items. """
        return len(self._data)

    count = __len__

    def get(self, key: str, default: Any = DXFKeyError) -> 'DXFEntity':
        """
        Returns :class:`DXFEntity` for `key`, if `key` exist, else `default` or
        raises a :class:`DXFKeyError` for `default` = :class:`DXFKeyError`.

        """
        try:
            entity = self._data[key]
        except KeyError:
            if default is DXFKeyError:
                raise DXFKeyError(f"KeyError: '{key}'")
            else:
                return default
        else:
            if isinstance(entity, str):
                # Entity is still a handle:
                entity = self.entitydb[entity]
                # and replace handle by DXFEntity object:
                self._data[key] = entity
            return entity

    def add(self, key: str, value: 'DXFEntity') -> None:
        """ Add entry ``(key, value)``. """
        if isinstance(value, str):
            try:
                value = self.entitydb[value]
            except KeyError:
                raise DXFValueError(
                    f'Invalid entity handle #{value} for key {key}')
        self._data[key] = value

    def remove(self, key: str) -> None:
        """ Delete entry `key`. Raises :class:`DXFKeyError`, if `key` does not
        exist. Deletes also hard owned DXF objects from OBJECTS section.

        """
        data = self._data
        if key not in data:
            raise DXFKeyError(key)

        if self.is_hard_owner:
            entity = self.get(key)
            # Presumption: hard owned DXF objects always reside in the OBJECTS
            # section.
            self.doc.objects.delete_entity(entity)
        del data[key]

    def discard(self, key: str) -> None:
        """ Delete entry `key` if exists. Does NOT raise an exception if `key`
        not exist and does not delete hard owned DXF objects.

        """
        try:
            del self._data[key]
        except KeyError:
            pass

    def clear(self) -> None:
        """  Delete all entries from :class:`Dictionary`, deletes hard owned
        DXF objects from OBJECTS section.

        """
        if self.is_hard_owner:
            self._delete_hard_owned_entries()
        self._data.clear()

    def _delete_hard_owned_entries(self) -> None:
        # Presumption: hard owned DXF objects always reside in the OBJECTS section
        objects = self.doc.objects
        for key, entity in self.items():
            objects.delete_entity(entity)

    def add_new_dict(self, key: str, hard_owned: bool = False) -> 'Dictionary':
        """
        Create a new sub :class:`Dictionary`.

        Args:
            key: name of the sub dictionary
            hard_owned: entries of the new dictionary are hard owned

        """
        dxf_dict = self.doc.objects.add_dictionary(owner=self.dxf.handle,
                                                   hard_owned=hard_owned)
        self.add(key, dxf_dict)
        return dxf_dict

    def add_dict_var(self, key: str, value: str) -> 'DictionaryVar':
        """ Add new :class:`DictionaryVar`.

        Args:
             key: entry name as string
             value: entry value as string

        """
        new_var = self.doc.objects.add_dictionary_var(
            owner=self.dxf.handle,
            value=value
        )
        self.add(key, new_var)
        return new_var

    def set_or_add_dict_var(self, key: str, value: str) -> 'DictionaryVar':
        """ Set or add new :class:`DictionaryVar`.

        Args:
             key: entry name as string
             value: entry value as string

        """
        if key not in self:
            dict_var = self.doc.objects.add_dictionary_var(
                owner=self.dxf.handle,
                value=value
            )
            self.add(key, dict_var)
        else:
            dict_var = self.get(key)
            dict_var.dxf.value = str(value)
        return dict_var

    def get_required_dict(self, key: str) -> 'Dictionary':
        """ Get entry `key` or create a new :class:`Dictionary`,
        if `Key` not exit.
        """
        try:
            dxf_dict = self.get(key)
        except DXFKeyError:
            dxf_dict = self.add_new_dict(key)
        return dxf_dict

    def audit(self, auditor: 'Auditor') -> None:
        super().audit(auditor)
        self._check_invalid_entries(auditor)

    def _check_invalid_entries(self, auditor: 'Auditor'):
        trash = []  # do not delete content while iterating
        append = trash.append
        db = self.entitydb
        for key, entry in self._data.items():
            if isinstance(entry, str):
                if entry not in db:
                    append(key)
            elif entry.is_alive:
                if entry.dxf.handle not in db:
                    append(key)
            else:  # entry is destroyed
                append(key)
        for key in trash:
            del self._data[key]
            auditor.fixed_error(
                code=AuditError.INVALID_DICTIONARY_ENTRY,
                message=f'Removed entry "{key}" with invalid handle in {str(self)}',
                dxf_entity=self,
                data=key,
            )

    def destroy(self) -> None:
        if self.is_hard_owner:
            self._delete_hard_owned_entries()


acdb_dict_with_default = DefSubclass('AcDbDictionaryWithDefault', {
    'default': DXFAttr(340),
})


@register_entity
class DictionaryWithDefault(Dictionary):
    DXFTYPE = 'ACDBDICTIONARYWDFLT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_dictionary,
                               acdb_dict_with_default)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self._default = None  # type: DXFEntity

    def load_dxf_attribs(self,
                         processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        processor.load_dxfattribs_into_namespace(dxf, acdb_dict_with_default)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_dict_with_default.name)
        self.dxf.export_dxf_attribs(tagwriter, 'default')

    def get(self, key: str, default: Any = DXFKeyError) -> DXFEntity:
        # `default` argument is ignored, exist only for API compatibility,
        """ Returns :class:`DXFEntity` for `key` or the predefined dictionary
        wide :attr:`dxf.default` entity if `key` does not exist.

        """
        if self._default is None:
            self._default = self.entitydb[self.dxf.default]
        return super().get(key, default=self._default)

    def set_default(self, default) -> None:
        """ Set dictionary wide default entry.

        Args:
            default: default entry as hex string or as :class:`DXFEntity`

        """
        if isinstance(default, str):
            self._default = self.entitydb[default]
        else:
            self._default = default
        self.dxf.default = self._default.dxf.handle


acdb_dict_var = DefSubclass('DictionaryVariables', {
    'schema': DXFAttr(280, default=0),
    # Object schema number (currently set to 0)
    'value': DXFAttr(1, default=''),
})


@register_entity
class DictionaryVar(DXFObject):
    """
    DICTIONARYVAR objects are used by AutoCAD as a means to store named values
    in the database for setvar / getvar purposes without the need to add entries
    to the DXF HEADER section. System variables that are stored as
    DICTIONARYVAR objects are the following:

        - DEFAULTVIEWCATEGORY
        - DIMADEC
        - DIMASSOC
        - DIMDSEP
        - DRAWORDERCTL
        - FIELDEVAL
        - HALOGAP
        - HIDETEXT
        - INDEXCTL
        - INDEXCTL
        - INTERSECTIONCOLOR
        - INTERSECTIONDISPLAY
        - MSOLESCALE
        - OBSCOLOR
        - OBSLTYPE
        - OLEFRAME
        - PROJECTNAME
        - SORTENTS
        - UPDATETHUMBNAIL
        - XCLIPFRAME
        - XCLIPFRAME

    """
    DXFTYPE = 'DICTIONARYVAR'
    DXFATTRIBS = DXFAttributes(base_class, acdb_dict_var)

    def load_dxf_attribs(self,
                         processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        processor.load_dxfattribs_into_namespace(dxf, acdb_dict_var)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_dict_var.name)
        self.dxf.export_dxf_attribs(tagwriter, ['schema', 'value'])

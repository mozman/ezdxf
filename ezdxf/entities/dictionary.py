# Copyright (c) 2019, Manfred Moitzi
# License: MIT-License
# Created: 2019-02-18
from typing import TYPE_CHECKING, KeysView, ItemsView, Any, Union, Dict
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXFKeyError
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from .dxfentity import base_class, SubclassProcessor, DXFEntity
from .dxfobj import DXFObject
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes2 import TagWriter, Drawing, DXFNamespace, Auditor

__all__ = ['Dictionary', 'DictionaryWithDefault', 'DictionaryVar']

acdb_dictionary = DefSubclass('AcDbDictionary', {
    'hard_owned': DXFAttr(280, default=0),  # Hard-owner flag.
    # If set to 1, indicates that elements of the dictionary are to be treated as hard-owned
    'cloning': DXFAttr(281, default=1),  # Duplicate record cloning flag (determines how to merge duplicate entries):
    # 0 = not applicable
    # 1 = keep existing
    # 2 = use clone
    # 3 = <xref>$0$<name>
    # 4 = $0$<name>
    # 5 = Unmangle name

    # 3: entry name
    # 350: entry handle, some DICTIONARY objects have 360 as handle group code, this is accepted by AutoCAD but not
    # documented by the DXF reference!!! ezdxf replaces 360 codes by 350.
})

KEY_CODE = 3
VALUE_CODE = 350
SEARCH_CODES = (VALUE_CODE, 360)  # some DICTIONARY have 360 handles


@register_entity
class Dictionary(DXFObject):
    """
    AutoCAD maintains items such as mline styles and group definitions as objects in dictionaries.
    Other applications are free to create and use their own dictionaries as they see fit. The prefix "ACAD_" is reserved
    for use by AutoCAD applications.

    Dictionary entries are (key, DXFEntity) pairs. DXFEntity could be a string, because at loading time not all objects
    are already stored in the EntityDB, and have to acquired later.

    """
    DXFTYPE = 'DICTIONARY'
    DXFATTRIBS = DXFAttributes(base_class, acdb_dictionary)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self._data = dict()  # type: Dict[str, Union[str, DXFEntity]]

    def _copy_data(self, entity: 'Dictionary') -> None:
        """ Copy hard owned entities but do not store the copies in the entity database, this is a
        second step, this is just real copying.
        """
        # todo: what about reactors of cloned DXF objects?
        if self.dxf.hard_owned:
            entity._data = {key: entity.copy() for key, entity in self.items()}
        else:
            entity._data = {key: entity for key, entity in self.items()}

    def _add_data_to_db(self) -> None:
        """ Add hard owned and therefor copied entities into database and the objects section.  """
        # todo: don't know how to proceed with reactors of cloned objects?
        if self.dxf.hard_owned:
            my_handle = self.dxf.handle
            for _, entity in self.items():
                entity.dxf.owner = my_handle
                entity.dxf.handle = None
                self.entitydb.add(entity)
                # add it also to the objects section, else it wouldn't exported to DXF file
                self.doc.objects.add_object(entity)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_dictionary)
            self.load_dict(tags)
        return dxf

    def load_dict(self, tags):
        entry_handle = None
        dict_key = None
        for code, value in tags:
            if code in SEARCH_CODES:
                # first store handles, because at this point, not all objects are stored in the EntityDB,
                # at access convert the handle to DXFEntity
                entry_handle = value
            elif code == KEY_CODE:
                dict_key = value
            if dict_key and entry_handle:
                try:
                    entity = self.entitydb[entry_handle]
                except KeyError:
                    entity = entry_handle  # store entity as handle string

                self._data[dict_key] = entity
                entry_handle = None
                dict_key = None

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)

        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_dictionary.name)
        self.dxf.export_dxf_attribs(tagwriter, ['hard_owned', 'cloning'])
        self.export_dict(tagwriter)
        # xdata and embedded objects export will be done by parent class

    def export_dict(self, tagwriter: 'TagWriter'):
        # key: dict key string
        # value: DXFEntity
        for key, value in self._data.items():
            tagwriter.write_tag2(KEY_CODE, key)
            # value can be a handle string or a DXFEntity
            if not isinstance(value, str):
                value = value.dxf.handle
            tagwriter.write_tag2(VALUE_CODE, value)

    @property
    def is_hard_owner(self) -> bool:
        return bool(self.dxf.hard_owned)

    def keys(self) -> KeysView:
        """
        Generator for the dictionary's keys.

        """
        return self._data.keys()

    def items(self) -> ItemsView:
        """
        Generator for the dictionary's items as (key, DXFEntity) pairs.

        """
        for key in self.keys():
            yield (key, self.get(key))  # maybe handle -> DXFEntity

    def __getitem__(self, key: str) -> 'DXFEntity':
        """
        Return the value for `key` if key is in the dictionary, else raises a `KeyError`.

        """
        return self.get(key)

    def __setitem__(self, key: str, value: 'DXFEntity') -> None:
        """
        Add item `(key, value)` to dictionary.

        """
        return self.add(key, value)

    def __delitem__(self, key: str) -> None:
        """
        Remove element `key` from the dictionary. Raises `KeyError` if key is not contained in the dictionary.

        """
        return self.remove(key)

    def __contains__(self, key: str) -> bool:
        """
        Return True if the dictionary has `key`, else False.

        """
        return key in self._data

    def __len__(self) -> int:
        """
        Return the number of items in the dictionary.

        """
        return len(self._data)

    count = __len__

    def get(self, key: str, default: Any = DXFKeyError) -> 'DXFEntity':
        """
        Return DXFEntity for `key` if `key` is in the dictionary, else `default` or raises a `DXFKeyError`
        for `default`=`DXFKeyError`.

        """
        try:
            entity = self._data[key]
        except KeyError:
            if default is DXFKeyError:
                raise DXFKeyError("KeyError: '{}'".format(key))
            else:
                return default
        else:
            if isinstance(entity, str):
                # entity is still a handle, get DXFEntity from EntityDB
                entity = self.entitydb[entity]
                # and store DXFEntity in the dict
                self._data[key] = entity
            return entity

    def add(self, key: str, value: 'DXFEntity') -> None:
        """
        Add item `(key, value)` to dictionary.

        """
        if isinstance(value, str):
            try:
                value = self.entitydb[value]
            except KeyError:
                raise DXFKeyError('Invalid entity handle #{} for key {}'.format(value, key))
        self._data[key] = value

    def remove(self, key: str) -> None:
        """
        Remove element `key` from the dictionary. Raises `DXFKeyError` if `key` not exists. Deletes hard owned DXF
        objects from OBJECTS section.

        """
        data = self._data
        if key not in data:
            raise DXFKeyError(key)

        if self.is_hard_owner:
            entity = self.get(key)
            # Presumption: hard owned DXF objects always reside in the OBJECTS section
            self.doc.objects.delete_entity(entity)
        del data[key]

    def discard(self, key: str) -> None:
        """
        Remove `key` from dictionary, if exists. Does NOT delete hard owned entities!

        """
        try:
            del self._data[key]
        except KeyError:
            pass

    def clear(self) -> None:
        """
        Removes all entries from DXFDictionary, and also deletes all hard owned DXF objects from OBJECTS section.

        """
        if self.is_hard_owner:
            self.delete_hard_owned_entries()
        self._data.clear()

    def delete_hard_owned_entries(self) -> None:
        # Presumption: hard owned DXF objects always reside in the OBJECTS section
        objects = self.doc.objects
        for key, entity in self.items():
            objects.delete_entity(entity)

    def add_new_dict(self, key: str, hard_owned: bool = False) -> 'Dictionary':
        """
        Create a new sub dictionary.

        Args:
            key: name of the sub dictionary
            hard_owned: entries of the new dictionary are hard owned

        """
        dxf_dict = self.doc.objects.add_dictionary(owner=self.dxf.handle, hard_owned=hard_owned)
        self.add(key, dxf_dict)
        return dxf_dict

    def get_required_dict(self, key: str) -> 'Dictionary':
        """
        Get DXFDictionary `key`, if exists or create a new DXFDictionary.

        """
        try:
            dxf_dict = self.get(key)
        except DXFKeyError:
            dxf_dict = self.add_new_dict(key)
        return dxf_dict

    def audit(self, auditor: 'Auditor') -> None:
        auditor.check_handles_exists(self, handles=self._data.values())

    def destroy(self) -> None:
        if self.is_hard_owner:
            self.delete_hard_owned_entries()


acdb_dict_with_default = DefSubclass('AcDbDictionaryWithDefault', {
    'default': DXFAttr(340),
})


@register_entity
class DictionaryWithDefault(Dictionary):
    DXFTYPE = 'ACDBDICTIONARYWDFLT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_dictionary, acdb_dict_with_default)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self._default = None  # type: DXFEntity

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
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
        """
        Return DXFEntity for `key` if exists else returns the predefined dictionary wide `default` entity. Parameter
        `default` is always ignored!

        """
        if self._default is None:
            self._default = self.entitydb[self.dxf.default]
        return super().get(key, default=self._default)

    def set_default(self, default) -> None:
        if isinstance(default, str):
            self._default = self.entitydb[default]
        else:
            self._default = default
        self.dxf.default = self._default.dxf.handle


acdb_dict_var = DefSubclass('DictionaryVariables', {
    'schema': DXFAttr(280, default=0),  # Object schema number (currently set to 0)
    'value': DXFAttr(1, default=''),
})


@register_entity
class DictionaryVar(DXFObject):
    """
    DICTIONARYVAR objects are used by AutoCAD as a means to store named values in the database for setvar / getvar
    purposes without the need to add entries to the DXF HEADER section. System variables that are stored as
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

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        processor.load_dxfattribs_into_namespace(dxf, acdb_dict_var.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_dict_var.name)
        self.dxf.export_dxf_attribs(tagwriter, ['schema', 'value'])

# Copyright (c) 2019-2021, Manfred Moitzi
# License: MIT-License
from typing import (
    TYPE_CHECKING,
    Union,
    Dict,
    Optional,
    List,
)
import logging
from ezdxf.lldxf import validator
from ezdxf.lldxf.const import (
    SUBCLASS_MARKER,
    DXFKeyError,
    DXFValueError,
    DXFTypeError,
)
from ezdxf.lldxf.attributes import (
    DXFAttr,
    DXFAttributes,
    DefSubclass,
    RETURN_DEFAULT,
    group_code_mapping,
)
from ezdxf.lldxf.types import is_valid_handle
from ezdxf.audit import AuditError
from ezdxf.entities import factory, DXFGraphic
from .dxfentity import base_class, SubclassProcessor, DXFEntity
from .dxfobj import DXFObject

logger = logging.getLogger("ezdxf")

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace, Auditor, XRecord

__all__ = ["Dictionary", "DictionaryWithDefault", "DictionaryVar"]

acdb_dictionary = DefSubclass(
    "AcDbDictionary",
    {
        # If set to 1, indicates that elements of the dictionary are to be treated
        # as hard-owned:
        "hard_owned": DXFAttr(
            280,
            default=0,
            optional=True,
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
        "cloning": DXFAttr(
            281,
            default=1,
            validator=validator.is_in_integer_range(0, 6),
            fixer=RETURN_DEFAULT,
        ),
        # 3: entry name
        # 350: entry handle, some DICTIONARY objects have 360 as handle group code,
        # this is accepted by AutoCAD but not documented by the DXF reference!
        # ezdxf replaces group code 360 by 350.
    },
)
acdb_dictionary_group_codes = group_code_mapping(acdb_dictionary)
KEY_CODE = 3
VALUE_CODE = 350
# Some DICTIONARY use group code 360:
SEARCH_CODES = (VALUE_CODE, 360)


@factory.register_entity
class Dictionary(DXFObject):
    """AutoCAD maintains items such as mline styles and group definitions as
    objects in dictionaries. Other applications are free to create and use
    their own dictionaries as they see fit. The prefix "ACAD_" is reserved
    for use by AutoCAD applications.

    Dictionary entries are (key, DXFEntity) pairs. DXFEntity could be a string,
    because at loading time not all objects are already stored in the EntityDB,
    and have to be acquired later.

    """

    DXFTYPE = "DICTIONARY"
    DXFATTRIBS = DXFAttributes(base_class, acdb_dictionary)

    def __init__(self):
        super().__init__()
        self._data: Dict[str, Union[str, DXFObject]] = dict()
        self._value_code = VALUE_CODE

    def _copy_data(self, entity: DXFEntity) -> None:
        """Copy hard owned entities but do not store the copies in the entity
        database, this is a second step (factory.bind), this is just real copying.
        """
        assert isinstance(entity, Dictionary)
        entity._value_code = self._value_code
        if self.dxf.hard_owned:
            # Reactors are removed from the cloned DXF objects.
            entity._data = {key: entity.copy() for key, entity in self.items()}
        else:
            entity._data = {key: entity for key, entity in self.items()}

    def post_bind_hook(self) -> None:
        """Called by binding a new or copied dictionary to the document,
        bind hard owned sub-entities to the same document and add them to the
        objects section.
        """
        if not self.dxf.hard_owned:
            return

        # copied or new dictionary:
        doc = self.doc
        assert doc is not None
        object_section = doc.objects
        owner_handle = self.dxf.handle
        for _, entity in self.items():
            entity.dxf.owner = owner_handle
            factory.bind(entity, doc)
            # For a correct DXF export add entities to the objects section:
            object_section.add_object(entity)

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.fast_load_dxfattribs(
                dxf, acdb_dictionary_group_codes, 1, log=False
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
                # Store entity as handle string:
                self._data[dict_key] = entry_handle
                entry_handle = None
                dict_key = None
        # Use same value code as loaded:
        self._value_code = value_code

    def post_load_hook(self, doc: "Drawing") -> None:
        super().post_load_hook(doc)
        db = doc.entitydb

        def items():
            for key, handle in self.items():
                entity = db.get(handle)
                if entity is not None and entity.is_alive:
                    yield key, entity

        if len(self):
            for k, v in list(items()):
                self.__setitem__(k, v)

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_dictionary.name)
        self.dxf.export_dxf_attribs(tagwriter, ["hard_owned", "cloning"])
        self.export_dict(tagwriter)

    def export_dict(self, tagwriter: "TagWriter"):
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
                    value = "0"
            # Use same value code as loaded:
            tagwriter.write_tag2(self._value_code, value)

    @property
    def is_hard_owner(self) -> bool:
        """Returns ``True`` if the dictionary is hard owner of entities.
        Hard owned entities will be destroyed by deleting the dictionary.
        """
        return bool(self.dxf.hard_owned)

    def keys(self):
        """Returns a :class:`KeysView` of all dictionary keys."""
        return self._data.keys()

    def items(self):
        """Returns an :class:`ItemsView` for all dictionary entries as
        (key, entity) pairs. An entity can be a handle string if the entity
        does not exist.
        """
        for key in self.keys():
            yield key, self.get(key)  # maybe handle -> DXFEntity

    def __getitem__(self, key: str) -> DXFEntity:
        """Return self[`key`].

        The returned value can be a handle string if the entity does not exist.

        Raises:
            DXFKeyError: `key` does not exist

        """
        if key in self._data:
            return self._data[key]  # type: ignore
        else:
            raise DXFKeyError(key)

    def __setitem__(self, key: str, entity: DXFObject) -> None:
        """Set self[`key`] = `entity`.

        Only DXF objects stored in the OBJECTS section are allowed as content
        of :class:`Dictionary` objects. DXF entities stored in layouts are not
        allowed.

        Raises:
            DXFTypeError: invalid DXF type

        """
        return self.add(key, entity)

    def __delitem__(self, key: str) -> None:
        """Delete self[`key`].

        Raises:
            DXFKeyError: `key` does not exist

        """
        return self.remove(key)

    def __contains__(self, key: str) -> bool:
        """Returns `key` ``in`` self."""
        return key in self._data

    def __len__(self) -> int:
        """Returns count of dictionary entries."""
        return len(self._data)

    count = __len__

    def get(
        self, key: str, default: Optional[DXFObject] = None
    ) -> Optional[DXFObject]:
        """Returns the :class:`DXFEntity` for `key`, if `key` exist else
        `default`. An entity can be a handle string if the entity
        does not exist.

        """
        return self._data.get(key, default)  # type: ignore

    def add(self, key: str, entity: DXFObject) -> None:
        """Add entry ``(key, value)``.

        Raises:
            DXFValueError: invalid entity handle
            DXFTypeError: invalid DXF type

        """
        if isinstance(entity, str):
            if not is_valid_handle(entity):
                raise DXFValueError(
                    f"Invalid entity handle #{entity} for key {key}"
                )
        elif isinstance(entity, DXFGraphic):
            raise DXFTypeError(
                f"Graphic entities not allowed: {entity.dxftype()}"
            )
        self._data[key] = entity

    def remove(self, key: str) -> None:
        """Delete entry `key`. Raises :class:`DXFKeyError`, if `key` does not
        exist. Destroys hard owned DXF entities.

        """
        data = self._data
        if key not in data:
            raise DXFKeyError(key)

        if self.is_hard_owner:
            assert self.doc is not None
            entity = self.__getitem__(key)
            # Presumption: hard owned DXF objects always reside in the OBJECTS
            # section.
            # TODO: use entity.destroy()?
            self.doc.objects.delete_entity(entity)  # type: ignore
        del data[key]

    def discard(self, key: str) -> None:
        """Delete entry `key` if exists. Does not raise an exception if `key`
        doesn't exist and does not destroy hard owned DXF entities.

        """
        try:
            del self._data[key]
        except KeyError:
            pass

    def clear(self) -> None:
        """Delete all entries from the dictionary and destroys hard owned
        DXF entities.
        """
        if self.is_hard_owner:
            self._delete_hard_owned_entries()
        self._data.clear()

    def _delete_hard_owned_entries(self) -> None:
        # Presumption: hard owned DXF objects always reside in the OBJECTS section
        objects = self.doc.objects  # type: ignore
        for key, entity in self.items():
            # TODO: is entity a string?
            # TODO: use entity.destroy()?
            objects.delete_entity(entity)  # type: ignore

    def add_new_dict(self, key: str, hard_owned: bool = False) -> "Dictionary":
        """Create a new sub-dictionary of type :class:`Dictionary`.

        Args:
            key: name of the sub-dictionary
            hard_owned: entries of the new dictionary are hard owned

        """
        dxf_dict = self.doc.objects.add_dictionary(  # type: ignore
            owner=self.dxf.handle, hard_owned=hard_owned
        )
        self.add(key, dxf_dict)
        return dxf_dict

    def add_dict_var(self, key: str, value: str) -> "DictionaryVar":
        """Add a new :class:`DictionaryVar`.

        Args:
             key: entry name as string
             value: entry value as string

        """
        new_var = self.doc.objects.add_dictionary_var(  # type: ignore
            owner=self.dxf.handle, value=value
        )
        self.add(key, new_var)
        return new_var

    def add_xrecord(self, key: str) -> "XRecord":
        """Add a new :class:`XRecord`.

        Args:
             key: entry name as string

        """
        new_xrecord = self.doc.objects.add_xrecord(  # type: ignore
            owner=self.dxf.handle,
        )
        self.add(key, new_xrecord)
        return new_xrecord

    def set_or_add_dict_var(self, key: str, value: str) -> "DictionaryVar":
        """Set or add new :class:`DictionaryVar`.

        Args:
             key: entry name as string
             value: entry value as string

        """
        if key not in self:
            dict_var = self.doc.objects.add_dictionary_var(  # type: ignore
                owner=self.dxf.handle, value=value
            )
            self.add(key, dict_var)
        else:
            dict_var = self.get(key)
            dict_var.dxf.value = str(value)  # type: ignore
        return dict_var

    def link_dxf_object(self, name: str, obj: DXFObject) -> None:
        """Add `obj` and set owner of `obj` to this dictionary.

        Graphical DXF entities have to reside in a layout and therefore can not
        be owned by a :class:`Dictionary`.

        Raises:
            DXFTypeError: `obj` has invalid DXF type

        """
        if not isinstance(obj, DXFObject):
            raise DXFTypeError(f"invalid DXF type: {obj.dxftype()}")
        self.add(name, obj)
        obj.dxf.owner = self.dxf.handle

    def get_required_dict(self, key: str, hard_owned=False) -> "Dictionary":
        """Get entry `key` or create a new :class:`Dictionary`,
        if `Key` not exist.
        """
        dxf_dict = self.get(key)
        if dxf_dict is None:
            dxf_dict = self.add_new_dict(key, hard_owned=hard_owned)
        return dxf_dict  # type: ignore

    def audit(self, auditor: "Auditor") -> None:
        super().audit(auditor)
        self._check_invalid_entries(auditor)

    def _check_invalid_entries(self, auditor: "Auditor"):
        trash: List[str] = []  # do not delete content while iterating
        append = trash.append
        db = auditor.entitydb
        for key, entry in self._data.items():
            if isinstance(entry, str):
                if entry not in db:
                    append(key)
            elif entry.is_alive:
                # TODO: remove graphical entities without destroying them
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
        if not self.is_alive:
            return

        if self.is_hard_owner:
            self._delete_hard_owned_entries()
        super().destroy()


acdb_dict_with_default = DefSubclass(
    "AcDbDictionaryWithDefault",
    {
        "default": DXFAttr(340),
    },
)
acdb_dict_with_default_group_codes = group_code_mapping(acdb_dict_with_default)


@factory.register_entity
class DictionaryWithDefault(Dictionary):
    DXFTYPE = "ACDBDICTIONARYWDFLT"
    DXFATTRIBS = DXFAttributes(
        base_class, acdb_dictionary, acdb_dict_with_default
    )

    def __init__(self):
        super().__init__()
        self._default: Optional[DXFObject] = None

    def _copy_data(self, entity: DXFEntity) -> None:
        assert isinstance(entity, DictionaryWithDefault)
        entity._default = self._default

    def post_load_hook(self, doc: "Drawing") -> None:
        # Set _default to None if default object not exist - audit() replaces
        # a not existing default object by a place holder object.
        # AutoCAD ignores not existing default objects!
        self._default = doc.entitydb.get(self.dxf.default)  # type: ignore
        super().post_load_hook(doc)

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_dict_with_default_group_codes, 2
            )
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_dict_with_default.name)
        self.dxf.export_dxf_attribs(tagwriter, "default")

    def __getitem__(self, key: str):
        return self.get(key)

    def get(
        self, key: str, default: Optional[DXFObject] = None
    ) -> Optional[DXFObject]:
        # `default` argument is ignored, exist only for API compatibility,
        """Returns :class:`DXFEntity` for `key` or the predefined dictionary
        wide :attr:`dxf.default` entity if `key` does not exist or ``None``
        if default value also not exist.

        """
        return super().get(key, default=self._default)

    def set_default(self, default: DXFObject) -> None:
        """Set dictionary wide default entry.

        Args:
            default: default entry as :class:`DXFEntity`

        """
        self._default = default
        self.dxf.default = self._default.dxf.handle

    def audit(self, auditor: "Auditor") -> None:
        def create_missing_default_object():
            placeholder = self.doc.objects.add_placeholder(
                owner=self.dxf.handle
            )
            self.set_default(placeholder)
            auditor.fixed_error(
                code=AuditError.CREATED_MISSING_OBJECT,
                message=f"Created missing default object in {str(self)}.",
            )

        if self._default is None or not self._default.is_alive:
            if auditor.entitydb.locked:
                auditor.add_post_audit_job(create_missing_default_object)
            else:
                create_missing_default_object()
        super().audit(auditor)


acdb_dict_var = DefSubclass(
    "DictionaryVariables",
    {
        "schema": DXFAttr(280, default=0),
        # Object schema number (currently set to 0)
        "value": DXFAttr(1, default=""),
    },
)
acdb_dict_var_group_codes = group_code_mapping(acdb_dict_var)


@factory.register_entity
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

    DXFTYPE = "DICTIONARYVAR"
    DXFATTRIBS = DXFAttributes(base_class, acdb_dict_var)

    @property
    def value(self) -> str:
        """Get/set the value of the :class:`DictionaryVar` as string."""
        return self.dxf.get("value", "")

    @value.setter
    def value(self, data: str) -> None:
        self.dxf.set("value", str(data))

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(dxf, acdb_dict_var_group_codes, 1)
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_dict_var.name)
        self.dxf.export_dxf_attribs(tagwriter, ["schema", "value"])

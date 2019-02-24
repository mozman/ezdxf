# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
# DXFEntity - Root Entity
from typing import TYPE_CHECKING, List, Any, Iterable, Optional, Union, Callable
from ezdxf.clone import clone
from ezdxf import options
from ezdxf.lldxf.types import handle_code, dxftag, cast_value, DXFTag, SUBCLASS_MARKER
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF2000, STRUCTURE_MARKER, OWNER_CODE, DXF12
from ezdxf.lldxf.const import ACAD_REACTORS, ACAD_XDICTIONARY
from ezdxf.lldxf.const import DXFAttributeError, DXFKeyError, DXFValueError, DXFStructureError
from ezdxf.tools import set_flag_state
from .xdata import XData, EmbeddedObjects
from .appdata import AppData, Reactors, ExtensionDict
import logging

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFDictionary
    from ezdxf.eztypes import Auditor, TagWriter
    from ezdxf.entities.factory import EntityFactory
    from ezdxf.entitydb import EntityDB
    from ezdxf.drawing2 import Drawing
    from ezdxf.entities.layouts import BaseLayout

__all__ = ['DXFNamespace', 'DXFEntity', 'DXFTagStorage', 'SubclassProcessor', 'base_class', 'entity_linker']

"""
DXFEntity() is the base class of **all** DXF entities.

DXFNamespace() manages ass DXF attributes of an entity

New DXF version handling

By introducing the new entity system ezdxf does not care about DXF versions at usage, the
latest supported version is used. The DXF version of the document can be changed at runtime,
but unsupported features of later DXF versions, are just ignored by saving, ezdxf does no
conversion between different DXF versions, ezdxf is still not a CAD application.

"""

ERR_INVALID_DXF_ATTRIB = 'Invalid DXF attribute "{}" for entity {}'
ERR_DXF_ATTRIB_NOT_EXITS = 'DXF attribute "{}" does not exist'


class DXFNamespace:
    """
    Uses the Python object itself as attribute storage, only valid Python names can be used as attrib name.

    """

    def __init__(self, processor: 'SubclassProcessor' = None, entity: 'DXFEntity' = None):
        if processor:
            base_class_ = processor.base_class
            code = handle_code(base_class_[0].value)
            # CLASS entity has no handle and TABLE also has no handle if loaded from DXF R12 file
            handle = base_class_.get_first_value(code, None)
            # owner is None if loaded from DXF R12 file
            owner = base_class_.get_first_value(330, None)
            self.rewire(entity, handle, owner)
        else:
            self.reset_handles()
            self.rewire(entity)

    def reset_handles(self):
        """ Reset handle and owner to None. """
        self.__dict__['handle'] = None
        self.__dict__['owner'] = None

    def rewire(self, entity: 'DXFEntity', handle: str = None, owner: str = None) -> None:
        """
        Rewire DXF namespace with parent entity

        Args:
            entity: new associated entity
            handle: new handle or None
            owner:  new entity owner handle or None

        """
        # bypass __setattr__()
        self.__dict__['_entity'] = entity
        if handle is not None:
            self.__dict__['handle'] = handle
        if owner is not None:
            self.__dict__['owner'] = owner

    def clone(self):
        namespace = self.__class__()
        for key, value in self.__dict__.items():
            if key not in {'_entity', 'handle', 'owner'}:
                namespace.__dict__[key] = clone(value)
        return namespace

    def __deepcopy__(self, memodict: dict):
        raise NotImplementedError('use self.clone()')

    def __getattr__(self, key: str) -> Any:
        """ called if key does not exist, returns default value or None for unset default values
        """
        attrib_def = self.dxfattribs.get(key, None)  # type: DXFAttr
        if attrib_def:
            if attrib_def.xtype == XType.callback:
                return attrib_def.get_callback_value(self._entity)
            else:
                return attrib_def.default  # returns None for attributes without default value
        else:
            raise DXFAttributeError(ERR_INVALID_DXF_ATTRIB.format(key, self.dxftype))

    def __setattr__(self, key: str, value: Any) -> None:
        attrib_def = self.dxfattribs.get(key, None)  # type: DXFAttr
        if attrib_def:
            if attrib_def.xtype == XType.callback:
                attrib_def.set_callback_value(self._entity, value)
            else:
                self.__dict__[key] = cast_value(attrib_def.code, value)
        else:
            raise DXFAttributeError(ERR_INVALID_DXF_ATTRIB.format(key, self.dxftype))

    def __delattr__(self, key: str) -> None:
        if self.hasattr(key):
            del self.__dict__[key]
        else:
            raise DXFAttributeError(ERR_DXF_ATTRIB_NOT_EXITS.format(key))

    def get(self, key: str, default: Any = None) -> Any:
        """ Returns given `default` value not DXF default value for unset attributes. """
        # callback values should not exist as attribute in __dict__
        if self.hasattr(key):
            # do not return the DXF default value
            return self.__dict__[key]
        attrib_def = self.dxfattribs.get(key, None)  # type: DXFAttr
        if attrib_def:
            if attrib_def.xtype == XType.callback:
                return attrib_def.get_callback_value(self._entity)
            else:
                return default  # return give default
        else:
            raise DXFAttributeError(ERR_INVALID_DXF_ATTRIB.format(key, self.dxftype))

    def all_existing_dxf_attribs(self) -> dict:
        """
        Returns all existing DXF attributes, except DXFEntity parent link.

        Contains only DXF attributes, which are accessible by DXFNamespace.

        """
        attribs = dict(self.__dict__)
        del attribs['_entity']
        return attribs

    def set(self, key: str, value: Any) -> None:
        self.__setattr__(key, value)

    def discard(self, key: str) -> None:
        try:
            del self.__dict__[key]
        except KeyError:
            pass

    def is_supported(self, key: str) -> bool:
        """
        Returns True if DXF attribute `key` is supported else False. Does not grant that attribute `key` really exists.

        The new entity system, ignores the DXF version at runtime, unsupported features, are just not saved
        (no conversion between DXF version is done!).

        """

        return self.dxfattribs.get(key, None) is not None

    def hasattr(self, key: str) -> bool:
        """
        Returns True if attribute `key` really exists else False.

        Does no check if attribute `key` is supported, but implicit supported if exists.

        """
        return key in self.__dict__

    @property
    def dxftype(self):
        return self._entity.DXFTYPE

    @property
    def dxfattribs(self):
        return self._entity.DXFATTRIBS

    def dxf_default_value(self, key: str) -> Any:
        """
        Returns the default value as defined in the DXF standard.

        """
        attrib = self.dxfattribs.get(key, None)
        if attrib:
            return attrib.default
        else:
            return None

    def export_dxf_attribs(self, tagwriter: 'TagWriter', attribs: Union[str, Iterable]) -> None:
        """
        Exports DXF attribute `name` by `tagwriter`. Non optional attributes are forced and optional tags are only
        written if different to default value. DXF version check is always on: does not export DXF attribs which are not
        supported by tagwriter.dxfversion.

        Replaces export_dxf_attribute() and export_dxf_attribs() in the long run.

        Args:
            tagwriter: tag writer object
            attribs: DXF attribute name as string or an iterable of names

        """
        if isinstance(attribs, str):
            self._export_dxf_attribute_optional(tagwriter, attribs)
        else:
            for name in attribs:
                self._export_dxf_attribute_optional(tagwriter, name)

    def _export_dxf_attribute_optional(self, tagwriter: 'TagWriter', name: str) -> None:
        """
        Exports DXF attribute `name` by `tagwriter`. Optional tags are only written if different to default value.

        Args:
            tagwriter: tag writer object
            name: DXF attribute name

        """
        export_dxf_version = tagwriter.dxfversion
        not_force_optional = not tagwriter.force_optional
        attrib = self.dxfattribs.get(name, None)

        if attrib:
            optional = attrib.optional
            default = attrib.default
            value = self.get(name, None)
            if value is None and not optional:  # force default value e.g. layer
                value = default  # default value could be None

            if attrib.dxfversion:
                required_dxf_version = attrib.dxfversion
            else:
                required_dxf_version = DXF12

            # align_point is optional but default is None, write if exists and ignore force
            # optional and default value=None is handled correct
            if (value is not None) and (export_dxf_version >= required_dxf_version):  # do not export None
                # check optional value == default value
                if optional and not_force_optional and default is not None and (default == value):
                    return  # do not write explicit optional attribs if equal to default value
                # just use x, y for 2d points if value is a 3d point (Vector, tuple)
                if attrib.xtype == XType.point2d and len(value) > 2:
                    value = value[:2]
                tag = dxftag(attrib.code, value)
                tagwriter.write_tag(tag)
        else:
            raise DXFAttributeError(ERR_INVALID_DXF_ATTRIB.format(name, self.dxftype))


class SubclassProcessor:
    def __init__(self, tags: ExtendedTags, r12=None):
        if len(tags.subclasses) == 0:
            raise ValueError('Invalid tags.')
        self.subclasses = list(tags.subclasses)  # copy subclasses
        # DXF R12 and prior have no subclass marker system, all tags of an entity in one flat list
        # Where later DXF versions have at least 2 subclasses base_class and AcDbEntity
        # Exception CLASS has also only one subclass and no subclass marker, handled as DXF R12 entity
        self.r12 = len(self.subclasses) == 1 if r12 is None else r12
        self.name = tags.dxftype()
        try:
            self.handle = tags.get_handle()
        except DXFValueError:
            self.handle = '<?>'

    @property
    def base_class(self):
        return self.subclasses[0]

    def log_unprocessed_tags(self, unprocessed_tags: List, subclass='<?>'):
        if options.log_unprocessed_tags and len(unprocessed_tags):
            for tag in unprocessed_tags:
                logger.debug("unprocessed tag: {} in {}(#{}).{}".format(str(tag), self.name, self.handle, subclass))

    def find_subclass(self, name: str):
        for subclass in self.subclasses:
            if len(subclass) and subclass[0].value == name:
                return subclass
        return None

    def subclass_by_index(self, index: int):
        try:
            return self.subclasses[index]
        except IndexError:
            return None

    def load_dxfattribs_into_namespace(self, dxf: DXFNamespace, subclass_definition: DefSubclass,
                                       index: int = None) -> Tags:
        """
        Load all existing DXF attribute into DXFNamespace and return unprocessed tags, without leading subclass marker
        (102, ...).

        Args:
            dxf: target namespace
            subclass_definition: DXF attribute definitions (name=subclass_name, attribs={key=attribute name, value=DXFAttr})
            index: locate subclass by location

        Returns:
             Tags: unprocessed tags

        """

        # r12 has always unprocessed tags, because there are all tags in one subclass and one subclass definition never
        # covers all tags e.g. handle is processed in main_call, so it is an unprocessed tag in AcDbEntity.
        unprocessed_tags = Tags()
        if self.r12:
            tags = self.subclasses[0]
        else:
            if index is None:
                tags = self.find_subclass(subclass_definition.name)
            else:
                tags = self.subclass_by_index(index)
            if tags is None:
                return unprocessed_tags

        # do not cache group codes, content of group code will be deleted while processing
        group_codes = {dxfattr.code: dxfattr for dxfattr in subclass_definition.attribs.values()}

        # iterate without leading subclass marker or for r12 without leading (0, ...) structure tag
        for tag in tags[1:]:
            code, value = tag
            if code in group_codes:
                attrib = group_codes[code]  # type: DXFAttr
                if (attrib.xtype != XType.callback) or (attrib.setter is not None):
                    dxf.set(attrib.name, value)
                # remove group code because only the first occurrence is needed, group codes sometimes are used multiple times
                # in the same subclass for different purposes.
                del group_codes[code]
            else:
                unprocessed_tags.append(tag)
        return unprocessed_tags


base_class = DefSubclass(None, {
    'handle': DXFAttr(5),
    # owner: Soft-pointer ID/handle to owner BLOCK_RECORD object
    # this tag is not supported by DXF R12, but is used intern to unify entity handling between DXF R12 and DXF R2000+
    # do not write this tag into DXF file for DXF R12!
    'owner': DXFAttr(330),
    # Application defined data can only appear here:
    # {APPID ... multiple entries possible DXF R12?
    # {ACAD_REACTORS ... one entry DXF R2000+, optional
    # {ACAD_XDICTIONARY  ... one entry DXF R2000+, optional
})


class DXFEntity:
    DXFTYPE = 'DXFENTITY'  # storing as class var needs less memory
    DXFATTRIBS = DXFAttributes(base_class)  # DXF attribute definitions
    DEFAULT_ATTRIBS = None  # type: dict
    MIN_DXF_VERSION_FOR_EXPORT = DXF12

    # Explicit excluding is better than implicit excluding; idea to exclude attribs with leading '_' prevents
    # 'protected' members from cloning, which may cause other problems.
    EXCLUDE_FROM_CLONING = {'doc'}

    def __init__(self, doc: 'Drawing' = None):
        """ Default constructor """
        self.doc = doc  # type: Drawing
        # order of appearance in entity spaces, 100 (top) before 0 (default) before -100 (bottom)
        # whole int range allowed
        self.priority = 0  # type: int
        # create extended data only if needed
        self.appdata = None  # type: Optional[AppData]
        self.reactors = None  # type: Optional[Reactors]
        self.extension_dict = None  # type: Optional[ExtensionDict]
        self.xdata = None  # type: Optional[XData]
        self.embedded_objects = None  # type: Optional[EmbeddedObjects]
        self.dxf = DXFNamespace(entity=self)  # type: DXFNamespace

    @classmethod
    def load(cls, tags: Union[ExtendedTags, Tags], doc: 'Drawing' = None) -> 'DXFEntity':
        """
        Constructor to generate entities loaded from DXF files (untrusted environment)

        Args:
            tags: DXF tags as Tags() or ExtendedTags()
            doc: DXF Document

        """
        if not isinstance(tags, ExtendedTags):
            tags = ExtendedTags(tags)
        entity = cls(doc)  # bare minimum setup
        entity.load_tags(tags)
        return entity

    @classmethod
    def from_text(cls, text: str, doc: 'Drawing' = None) -> 'DXFEntity':
        """ Load constructor from text for testing """
        return cls.load(ExtendedTags.from_text(text), doc)

    @classmethod
    def shallow_copy(cls, other: 'DXFEntity') -> 'DXFEntity':
        """ Copy constructor for type casting e.g. Polyface and Polymesh """
        entity = cls(other.doc)
        entity.dxf = other.dxf
        entity.extension_dict = other.extension_dict
        entity.reactors = other.reactors
        entity.appdata = other.appdata
        entity.xdata = other.xdata
        entity.embedded_objects = other.embedded_objects
        entity.dxf.rewire(entity)
        entity.doc.entitydb.add(entity)  # same handle -> replaces other
        return entity

    def load_tags(self, tags: ExtendedTags) -> None:
        if tags:
            if len(tags.appdata):
                self.setup_app_data(tags.appdata)
            if len(tags.xdata):
                self.xdata = XData(tags.xdata)  # same process for every entity
            if tags.embedded_objects:
                self.embedded_objects = EmbeddedObjects(tags.embedded_objects)  # same process for every entity
            processor = SubclassProcessor(tags)
            self.dxf = self.load_dxf_attribs(processor)

    @classmethod
    def new(cls, handle: str = None, owner: str = None, dxfattribs: dict = None, doc: 'Drawing' = None) -> 'DXFEntity':
        """
        Constructor for building new entities from scratch by ezdxf (trusted environment)

        Args:
            handle: unique DXF entity handle or None
            owner: owner handle iof entity has an owner else None or '0'
            dxfattribs: DXF attributes to initialize
            doc: DXF document

        """
        entity = cls(doc)  # bare minimum setup
        if handle is not None:
            entity.dxf.handle = handle
        if owner is not None:
            entity.dxf.owner = owner  # set also for DXF R12 for internal usage
        default_attribs = dict(cls.DEFAULT_ATTRIBS or {})  # copy
        default_attribs.update(dxfattribs or {})
        entity.update_dxf_attribs(default_attribs)
        entity.post_new_hook()
        return entity

    def clone(self) -> 'DXFEntity':
        entity = self.__class__(doc=self.doc)
        self._clone_attribs(entity)
        entity.dxf.rewire(entity)
        return entity

    def _clone_attribs(self, entity):
        for key, value in self.__dict__.items():
            if key not in self.EXCLUDE_FROM_CLONING:
                entity.__dict__[key] = clone(value)

    def __deepcopy__(self, memodict: dict):
        raise NotImplementedError('use self.clone()')

    def __priority__(self) -> int:
        return self.priority

    def update_dxf_attribs(self, dxfattribs: dict) -> None:
        for key, value in dxfattribs.items():
            self.dxf.set(key, value)

    def post_new_hook(self):
        # for post processing and integrity validation after entity creation
        pass

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> DXFNamespace:
        # inheritance hook
        return DXFNamespace(processor, self)

    def setup_app_data(self, appdata: List[Tags]) -> None:
        for data in appdata:
            code, appid = data[0]
            if appid == ACAD_REACTORS:
                self.reactors = Reactors.from_tags(data)
            elif appid == ACAD_XDICTIONARY:
                self.extension_dict = ExtensionDict.from_tags(self, data)
            else:
                self.set_app_data(appid, data)

    @property
    def dxffactory(self) -> 'EntityFactory':
        return self.doc.dxffactory

    def get_dxf_attrib(self, key: str, default: Any = None) -> Any:
        return self.dxf.get(key, default)

    def set_dxf_attrib(self, key: str, value: Any) -> None:
        self.dxf.set(key, value)

    def del_dxf_attrib(self, key: str) -> None:
        self.dxf.delete(key)

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    def dxftype(self) -> str:
        return self.DXFTYPE

    def assign_layout(self, layout: 'BaseLayout') -> None:
        if layout.is_active_paperspace:
            self.dxf.paperspace = 1
        else:
            self.dxf.discard('paperspace')

        self.dxf.owner = layout.layout_key
        for linked_entity in self.linked_entities():
            linked_entity.assign_layout(layout)

    def layout(self) -> Optional['BaseLayout']:
        doc = self.doc
        try:  # is modelspace or paperspace
            layout = doc.layouts.get_layout_for_entity(self)
        except DXFKeyError:  # is a generic block
            block_rec = self.doc.entitydb[self.dxf.owner]
            block_name = block_rec.dxf.name
            layout = doc.blocks.get(block_name)
        return layout

    def __str__(self) -> str:
        """
        Returns a simple string representation.

        """
        return "{}(#{})".format(self.dxftype(), self.dxf.handle)

    def __repr__(self) -> str:
        """
        Returns a simple string representation including the class.

        """
        return str(self.__class__) + " " + str(self)

    def dxfattribs(self) -> dict:
        """
        Clones defined and existing DXF attributes as dict.

        """
        return self.dxf.all_existing_dxf_attribs()

    def set_flag_state(self, flag: int, state: bool = True, name: str = 'flags') -> None:
        flags = self.dxf.get(name, 0)
        self.dxf.set(name, set_flag_state(flags, flag, state=state))

    def get_flag_state(self, flag: int, name: str = 'flags') -> bool:
        return bool(self.dxf.get(name, 0) & flag)

    def linked_entities(self) -> Iterable['DXFEntity']:
        """ Yield linked entities: VERTEX or ATTRIB, different handling than attached entities. """
        return []

    def attached_entities(self) -> Iterable['DXFEntity']:
        """ Yield attached entities: MTEXT,  different handling than linked entities. """
        return []

    def link_entity(self, entity: 'DXFEntity') -> None:
        """ Store linked or attached entities. Same API for both types of appended data. """
        pass

    def set_owner(self, owner: str, paperspace: int = 0) -> None:
        self.dxf.owner = owner
        self.dxf.paperspace = paperspace
        for e in self.linked_entities():
            e.set_owner(owner, paperspace)

    @property
    def is_alive(self):
        return hasattr(self, 'dxf')

    def destroy(self) -> None:
        """
        Delete all data and references.

        """
        if self.extension_dict is not None:
            self.extension_dict.destroy(self.doc)
            del self.extension_dict
        del self.appdata
        del self.reactors
        del self.xdata
        del self.embedded_objects
        del self.doc
        del self.dxf

    def preprocess_export(self, tagwriter: 'TagWriter') -> bool:
        """ Pre requirement check and pre processing for export.

        Returns False if entity should not be exported at all.

        """
        return True

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        """ Export DXF entity by tagwriter

        This is a key method:

        - has to know the group codes for each attribute
        - has to add subclass tags in correct order
        - has to integrate extended data: ExtensionDict, Reactors, AppData
        - has to maintain the correct tag order (because sometimes order matters)

        """
        if tagwriter.dxfversion < self.MIN_DXF_VERSION_FOR_EXPORT:
            return
        if not self.preprocess_export(tagwriter):
            return
        # ! first step !
        # write handle, AppData, Reactors, ExtensionDict, owner
        self.export_base_class(tagwriter)

        # this is the entity specific part
        self.export_entity(tagwriter)

        # ! Last step !
        # write xdata, embedded objects
        self.export_xdata(tagwriter)
        self.export_embedded_objects(tagwriter)
        self.post_export(tagwriter)

    def export_base_class(self, tagwriter: 'TagWriter') -> None:
        # 1. tag: (0, DXFTYPE)
        tagwriter.write_tag2(STRUCTURE_MARKER, self.DXFTYPE)
        if tagwriter.dxfversion >= DXF2000:
            tagwriter.write_tag2(handle_code(self.dxf.dxftype), self.dxf.handle)
            if self.appdata:
                self.appdata.export_dxf(tagwriter)
            if self.reactors:
                self.reactors.export_dxf(tagwriter)
            if self.extension_dict:
                self.extension_dict.export_dxf(tagwriter)
            tagwriter.write_tag2(OWNER_CODE, self.dxf.owner)
        else:  # DXF R12
            if tagwriter.write_handles:
                tagwriter.write_tag2(handle_code(self.dxf.dxftype), self.dxf.handle)
                # do not write owner handle - not supported by DXF R12

    # interface definition
    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export DXF entity specific data by tagwriter

        This is a key method:

        - has to know the group codes for each attribute
        - has to add subclass tags in correct order
        - has to maintain the correct tag order (because sometimes order matters)

        """
        # base class (handle, appid, reactors, xdict, owner) export is done by parent class
        pass
        # xdata and embedded objects  export is also done by parent

    def export_xdata(self, tagwriter: 'TagWriter') -> None:
        if self.xdata:
            self.xdata.export_dxf(tagwriter)

    def export_embedded_objects(self, tagwriter: 'TagWriter') -> None:
        if self.embedded_objects:
            self.embedded_objects.export_dxf(tagwriter)

    def post_export(self, tagwriter: 'TagWriter'):
        """ Called after for entity export.

        Only for INSERT & POLYLINE to add SEQEND

        """
        pass

    def audit(self, auditor: 'Auditor') -> None:
        pass

    def _new_compound_entity(self, type_: str, dxfattribs: dict) -> 'DXFEntity':
        """
        Create new entity with same layout settings as `self`.

        Used by INSERT & POLYLINE to create appended DXF entities, don't use it to create new standalone entities.

        """
        dxfattribs = dxfattribs or {}
        # if layer is not deliberately set, set same layer as creator entity,
        # at least VERTEX should have the same layer as the POLYGON entity.
        # Don't know if that is also important for the ATTRIB & INSERT entity.
        if 'layer' not in dxfattribs:
            dxfattribs['layer'] = self.dxf.layer

        entity = self.dxffactory.create_db_entry(type_, dxfattribs)
        entity.dxf.owner = self.dxf.owner
        entity.dxf.paperspace = self.dxf.paperspace
        return entity

    def has_extension_dict(self) -> bool:
        return self.extension_dict is not None

    def get_extension_dict(self) -> 'DXFDictionary':
        def new_extension_dict():
            self.extension_dict = ExtensionDict(self)
            return self.extension_dict.get()

        if self.has_extension_dict():
            return self.extension_dict.get()
        else:
            return new_extension_dict()

    def has_app_data(self, appid: str) -> bool:
        return self.appdata and (appid in self.appdata)

    def get_app_data(self, appid: str) -> Tags:
        if self.appdata:
            return self.appdata.get(appid)
        else:
            raise DXFKeyError(appid)

    def set_app_data(self, appid: str, tags: Iterable) -> None:
        if self.appdata is None:
            self.appdata = AppData()
        self.appdata.add(appid, tags)

    def discard_app_data(self, appid: str):
        if self.appdata:
            self.appdata.discard(appid)

    def has_xdata(self, appid: str) -> bool:
        return self.xdata and (appid in self.xdata)

    def get_xdata(self, appid: str) -> Tags:
        if self.xdata:
            return self.xdata.get(appid)
        else:
            raise DXFKeyError(appid)

    def set_xdata(self, appid: str, tags: Iterable) -> None:
        if self.xdata is None:
            self.xdata = XData()
        self.xdata.add(appid, tags)

    def discard_xdata(self, appid: str) -> None:
        if self.xdata:
            self.xdata.discard(appid)

    def has_xdata_list(self, appid: str, name: str) -> bool:
        if self.has_xdata(appid):
            return self.xdata.has_xlist(appid, name)
        else:
            return False

    def get_xdata_list(self, appid: str, name: str) -> List:
        return self.xdata.get_xlist(appid, name)

    def set_xdata_list(self, appid: str, name: str, tags: Iterable) -> None:
        if self.xdata is None:
            self.xdata = XData()
        self.xdata.set_xlist(appid, name, tags)

    def discard_xdata_list(self, appid: str, name: str) -> None:
        if self.xdata:
            self.xdata.discard_xlist(appid, name)

    def replace_xdata_list(self, appid: str, name: str, tags: Iterable) -> None:
        self.xdata.replace_xlist(appid, name, tags)

    def has_reactors(self) -> bool:
        return bool(self.reactors)

    def get_reactors(self) -> List[str]:
        return self.reactors.get() if self.reactors else []

    def set_reactors(self, handles: Iterable[str]) -> None:
        if self.reactors is None:
            self.reactors = Reactors()
        self.reactors.set(handles)

    def append_reactor_handle(self, handle: str) -> None:
        if self.reactors is None:
            self.reactors = Reactors()
        self.reactors.add(handle)

    def discard_reactor_handle(self, handle: str) -> None:
        if self.reactors:
            self.reactors.discard(handle)


class DXFTagStorage(DXFEntity):
    """ Just store all the tags as they are """

    def __init__(self, doc: 'Drawing' = None):
        """ Default constructor """
        super().__init__(doc)
        self.xtags = []  # type: ExtendedTags

    @property
    def base_class(self):
        return self.xtags.subclasses[0]

    @classmethod
    def load(cls, tags: Union[ExtendedTags, Tags], doc: 'Drawing' = None) -> 'DXFTagStorage':
        entity = cls(doc)
        entity.load_tags(tags)
        entity.store_tags(tags)
        return entity

    def store_tags(self, tags: ExtendedTags) -> None:
        # store DXFTYPE, overrides class member
        # 1. tag of 1. subclass is the structure tag (0, DXFTYPE)
        self.xtags = tags
        self.DXFTYPE = self.base_class[0].value

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Write subclass tags as they are
        """
        # base class export is done by parent
        for subclass in self.xtags.subclasses[1:]:
            tagwriter.write_tags(subclass)
        # xdata and embedded objects  export is done by parent

    def destroy(self) -> None:
        del self.xtags
        super().destroy()


LINKED_ENTITIES = {
    'INSERT': 'ATTRIB',
    'POLYLINE': 'VERTEX'
}

# todo: MTEXT attached to ATTRIB & ATTDEF
# This attached MTEXT is a limited MTEXT entity, starting with (0, 'MTEXT') therefor separated entity, but without the
# base class: no handle, no owner nor AppData, and a limited AcDbEntity subclass.
# Detect attached entities (more than MTEXT?) by required but missing handle and owner tags
# use DXFEntity.link_entity() for linking to preceding entity, INSERT & POLYLINE do not have attached entities, so reuse
# of API for ATTRIB & ATTDEF should be safe.


def entity_linker() -> Callable[[DXFEntity], bool]:
    main_entity = None  # type: Optional[DXFEntity]
    prev = None  # type: Optional[DXFEntity] # store preceding entity
    expected = ""

    def entity_linker_(entity: DXFEntity) -> bool:
        nonlocal main_entity, expected, prev
        dxftype = entity.dxftype()  # type: str
        are_linked_entities = False  # INSERT & POLYLINE are not linked entities, they are stored in the entity space
        if main_entity is not None:
            are_linked_entities = True  # VERTEX, ATTRIB & SEQEND are linked tags, they are NOT stored in the entity space
            if dxftype == 'SEQEND':
                # do not store SEQEND entity
                main_entity = None
            # check for valid DXF structure just VERTEX follows POLYLINE and just ATTRIB follows INSERT
            elif dxftype == expected:
                main_entity.link_entity(entity)
            else:
                raise DXFStructureError("expected DXF entity {} or SEQEND".format(dxftype))
        # linked entities
        elif dxftype in ('INSERT', 'POLYLINE'):  # only these two DXF types have this special linked structure
            if dxftype == 'INSERT' and not entity.dxf.get('attribs_follow', 0):
                # INSERT must not have following ATTRIBS, ATTRIB can be a stand alone entity:
                #   INSERT with no ATTRIBS, attribs_follow == 0
                #   ATTRIB as stand alone entity
                #   ....
                #   INSERT with ATTRIBS, attribs_follow == 1
                #   ATTRIB as connected entity
                #   SEQEND
                #
                # Therefore a ATTRIB following an INSERT doesn't mean that these entities are connected.
                pass
            else:
                main_entity = entity
                expected = LINKED_ENTITIES[dxftype]
        # attached entities
        elif (dxftype == 'MTEXT') and (entity.dxf.handle is None):  # attached MTEXT entity
            if prev:

                prev.link_entity(entity)
                are_linked_entities = True
            else:
                raise DXFStructureError("Attached MTEXT entity without a preceding entity.")
        prev = entity
        return are_linked_entities  # caller should know, if *tags* should be stored in the entity space or not

    return entity_linker_


def export_seqend(tagwriter: 'TagWriter', entity: DXFEntity) -> None:
    handle = entity.entitydb.next_handle()
    tagwriter.write_tag2(0, 'SEQEND')
    tagwriter.write_tag2(5, handle)
    if tagwriter.dxfversion > DXF12:
        owner = entity.dxf.owner
        tagwriter.write_tag2(OWNER_CODE, owner)
        tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbEntity')

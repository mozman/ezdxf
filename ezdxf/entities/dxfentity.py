# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
# DXFEntity - Root Entity
from typing import TYPE_CHECKING, List, Any, Iterable, Optional, Union
from ezdxf.clone import clone
from ezdxf import options
from ezdxf.lldxf.types import handle_code, dxftag
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF2000, STRUCTURE_MARKER, OWNER_CODE
from ezdxf.lldxf.const import DXFAttributeError, DXFTypeError, DXFKeyError, DXFValueError
from ezdxf.tools import set_flag_state
from .xdata import XData, EmbeddedObjects
from .appdata import AppData, Reactors, ExtensionDict
import logging
logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFDictionary, Drawing, EntityDB, DXFFactoryType
    from ezdxf.eztypes import Auditor, TagWriter

__all__ = ['DXFNamespace', 'DXFEntity', 'UnknownEntity', 'SubclassProcessor', 'base_class']

"""
DXFEntity() is the base class of **all** DXF entities.

DXFNamespace() manages ass DXF attributes of an entity

New DXF version handling

By introducing the new entity system ezdxf does not care about DXF versions at usage, the
latest supported version is used. The DXF version of the document can be changed at runtime,
but unsupported features of later DXF versions, are just ignored by saving, ezdxf does no
conversion between different DXF versions, ezdxf is still not a CAD application.

"""

ERR_INVALID_DXF_ATTRIB = 'Invalid DXF attribute for entity {}'
ERR_DXF_ATTRIB_NOT_EXITS = 'DXF attribute {} does not exist'


class DXFNamespace:
    """
    Uses the Python object itself as attribute storage, only valid Python names can be used as attrib name.

    """

    def __init__(self, processor: 'SubclassProcessor' = None, entity: 'DXFEntity' = None):
        if processor:
            base_class_ = processor.base_class
            code = handle_code(base_class_[0].value)
            handle = base_class_.get_first_value(code, None)  # CLASS entity has no handle
            owner = base_class_.get_first_value(330, None)  # owner, None for DXF R12 if read from file
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
        """ called if key does not exist """
        if self.is_supported(key):
            value = self.dxf_default_value(key)
            if value is not None:
                return value
            else:
                raise DXFAttributeError(ERR_DXF_ATTRIB_NOT_EXITS.format(key))
        else:
            raise DXFAttributeError(ERR_INVALID_DXF_ATTRIB.format(self.dxftype))

    def __setattr__(self, key: str, value: Any) -> None:
        if self.hasattr(key) or self.is_supported(key):
            self.__dict__[key] = value
        else:
            raise DXFAttributeError(ERR_INVALID_DXF_ATTRIB.format(self.dxftype))

    def __delattr__(self, key: str) -> None:
        if self.hasattr(key):
            del self.__dict__[key]
        else:
            raise DXFAttributeError(ERR_DXF_ATTRIB_NOT_EXITS.format(key))

    def get(self, key: str, default: Any = None) -> Any:
        if self.hasattr(key):
            # do not return the DXF default value
            return self.__dict__[key]
        elif self.is_supported(key):
            # return given default value if `key` is supported
            return default
        else:
            raise DXFAttributeError(ERR_INVALID_DXF_ATTRIB.format(self.dxftype))

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

    def export_dxf_attribute(self, tagwriter: 'TagWriter', name: str, force=False) -> None:
        """
        Exports DXF attribute `name` by `tagwriter`. Does not care about DXF version -> caller

        Args:
            tagwriter: tag writer object
            name: DXF attribute name
            force: wriet default value if attribute is noe set

        """
        attrib = self.dxfattribs.get(name, None)
        if attrib:
            value = self.get(name, None)
            if value is None and force:  # force default value e.g. layer
                value = attrib.default  # default value could be None

            if value is not None:
                tag = dxftag(attrib.code, value)
                tagwriter.write_tag(tag)
        else:
            raise DXFAttributeError(ERR_INVALID_DXF_ATTRIB.format(self.dxftype))

    def export_dxf_attribs(self, tagwriter: 'TagWriter', names: Iterable[str]) -> None:
        """
        Exports many DXF attributes by `tagwriter`.  Does not care about DXF version -> caller

        Args:
            tagwriter: tag writer object
            names: iterable of attribute names

        """
        for name in names:
            self.export_dxf_attribute(tagwriter, name)


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

    def load_dxfattribs_into_namespace(self, dxf: DXFNamespace, subclass_definition: DefSubclass) -> Tags:
        """
        Load all existing DXF attribute into DXFNamespace and return unprocessed tags, without leading subclass marker
        (102, ...).

        Args:
            dxf: target namespace
            subclass_definition: DXF attribute definitions (name=subclass_name, attribs={key=attribute name, value=DXFAttr})

        Returns:
             Tags: unprocessed tags

        """

        def attribs_by_code():
            codes = {}
            for name, dxfattr in subclass_definition.attribs.items():
                codes[dxfattr.code] = name
            return codes

        # r12 has always unprocessed tags, because there are all tags in one subclass and one subclass definition never
        # covers all tags e.g. handle is processed in main_call, so it is an unprocessed tag in AcDbEntity.
        unprocessed_tags = Tags()
        if self.r12:
            tags = self.subclasses[0]
        else:
            tags = self.find_subclass(subclass_definition.name)
            if tags is None:
                return unprocessed_tags

        group_codes = attribs_by_code()
        # iterate without leading subclass marker or for r12 without leading (0, ...) structure tag
        for tag in tags[1:]:
            code, value = tag
            if code in group_codes:
                name = group_codes[code]
                dxf.set(name, value)
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

    def load_tags(self, tags: ExtendedTags) -> None:
        if tags:
            if len(tags.appdata):
                self.setup_app_data(tags.appdata)
            if len(tags.xdata):
                self.xdata = XData(tags.xdata)  # same process for every entity
            if tags.embedded_objects:
                self.embedded_objects = EmbeddedObjects(tags.embedded_objects)  # same process for every entity
            processor = SubclassProcessor(tags)
            self.dxf = self.setup_dxf_attribs(processor)
            # todo: set owner for DXF R12 read from file

    @classmethod
    def new(cls, handle: str, owner: str = None, dxfattribs: dict = None, doc: 'Drawing' = None) -> 'DXFEntity':
        """
        Constructor for building new entities from scratch by ezdxf (trusted environment)

        Args:
            handle: unique DXF entity handle
            owner: owner handle iof entity has an owner else None or '0'
            dxfattribs: DXF attributes to initialize
            doc: DXF document

        """
        if cls.DEFAULT_ATTRIBS is None:
            raise DXFTypeError("new() for DXF type {} not supported".format(cls.DXFTYPE))

        entity = cls(doc)  # bare minimum setup
        entity.dxf.handle = handle
        entity.dxf.owner = owner  # set also for DXF R12 for internal usage
        default_attribs = dict(cls.DEFAULT_ATTRIBS)  # copy
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

    def update_dxf_attribs(self, dxfattribs: dict) -> None:
        for key, value in dxfattribs.items():
            self.dxf.set(key, value)

    def post_new_hook(self):
        pass

    def setup_dxf_attribs(self, processor: SubclassProcessor = None) -> DXFNamespace:
        # hook for inherited classes
        return DXFNamespace(processor, self)

    def setup_app_data(self, appdata: List[Tags]) -> None:
        for data in appdata:
            code, appid = data[0]
            if appid == '{REACTORS':
                self.reactors = Reactors.from_tags(data)
            elif appid == '{XDICTIONARY':
                self.extension_dict = ExtensionDict.from_tags(self, data)
            else:
                self.appdata.set(data)

    @property
    def dxffactory(self) -> 'DXFFactoryType':
        return self.doc.dxffactory

    def get_dxf_attrib(self, key: str, default: Any = None) -> Any:
        self.dxf.get(key, default)

    def set_dxf_attrib(self, key: str, value: Any) -> None:
        self.dxf.set(key, value)

    def del_dxf_attrib(self, key: str) -> None:
        self.dxf.delete(key)

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    def dxftype(self) -> str:
        return self.DXFTYPE

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

    @property
    def is_destroyed(self):
        return not hasattr(self, 'dxf')

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

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        """ Export DXF entity by tagwriter

        This is a key method:

        - has to know the group codes for each attribute
        - has to add subclass tags in correct order
        - has to integrate extended data: ExtensionDict, Reactors, AppData
        - has to maintain the correct tag order (because sometimes order matters)

        """
        # ! first step !
        # write handle, AppData, Reactors, ExtensionDict, owner
        self.export_base_class(tagwriter)

        # this is the entity specific part
        self.export_entity(tagwriter)

        # ! Last step !
        # write xdata, embedded objects
        self.export_xdata(tagwriter)
        self.export_embedded_objects(tagwriter)

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

    def audit(self, auditor: 'Auditor') -> None:
        pass

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


class UnknownEntity(DXFEntity):
    """ Just store all the tags as they are """

    def __init__(self, doc: 'Drawing' = None):
        """ Default constructor """
        super().__init__(doc)
        self.subclasses = []

    @classmethod
    def load(cls, tags: Union[ExtendedTags, Tags], doc: 'Drawing' = None) -> 'UnknownEntity':
        entity = cls(doc)
        entity.load_tags(tags)
        entity.store_tags(tags)
        return entity

    def store_tags(self, tags: ExtendedTags) -> None:
        # store DXFTYPE, overrides class member
        # 1. tag of 1. subclass is the structure tag (0, DXFTYPE)
        self.DXFTYPE = tags.subclasses[0][0].value
        # no need to store base class
        self.subclasses = tags.subclasses[1:]

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Write subclass tags as they are
        """
        # base class export is done by parent
        for subclass in self.subclasses:
            tagwriter.write_tags(subclass)

        # xdata and embedded objects  export is done by parent

    def destroy(self) -> None:
        del self.subclasses
        super().destroy()

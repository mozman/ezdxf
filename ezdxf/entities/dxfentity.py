# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# DXFEntity - Root Entity
# DXFObject - non graphical entities stored in OBJECTS section
# DXFGraphical - graphical DXF entities stored in ENTITIES and BLOCKS sections
#
from typing import TYPE_CHECKING, List, Any, cast, Union, Iterable, Set
from collections import OrderedDict
from ezdxf.lldxf.types import DXFTag, handle_code, dxftag, uniform_appid
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, DXF2000, DXFKeyError
from ezdxf.lldxf.const import DXFAttributeError, DXFTypeError, DXFVersionError, DXFStructureError
from ezdxf.lldxf.const import ACAD_XDICTIONARY, ACAD_REACTORS, XDICT_HANDLE_CODE, REACTOR_HANDLE_CODE, APP_DATA_MARKER
from ezdxf.lldxf.const import STRUCTURE_MARKER, OWNER_CODE

if TYPE_CHECKING:
    from ezdxf.lldxf.tagwriter import TagWriter
    from ezdxf.eztypes import DXFDictionary, Drawing, EntityDB, DXFFactoryType

ERR_INVALID_DXF_ATTRIB = 'Invalid DXF attribute for entity {}'
ERR_DXF_ATTRIB_NOT_EXITS = 'DXF attribute {} does not exist'

main_class = DefSubclass(None, {
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


class DXFNamespace:  # different for every DXF type
    """
    Uses the Python object itself as attribute storage, only valid Python names can be used as attrib name.

    """

    def __init__(self, subclasses: List[Tags], entity: 'DXFEntity'):
        assert len(subclasses)
        mainclass = subclasses[0]

        # bypass __setattr__() because without DXF attributes definition
        self.__dict__['_entity'] = entity
        # value of first tag is always the dxftype e.g. (0, LINE)
        code = handle_code(mainclass[0].value)
        self.handle = mainclass.get_first_value(code, None)  # CLASS entity has no handle
        self.owner = mainclass.get_first_value(330, None)  # owner, None for DXF R12 if read from file

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

    def get(self, key: str, default: Any) -> Any:
        if self.hasattr(key):
            # do not return the DXF default value
            return self.__dict__[key]
        elif self.is_supported(key):
            # return given default value if `key` is supported
            return default
        else:
            raise DXFAttributeError(ERR_INVALID_DXF_ATTRIB.format(self.dxftype))

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

        """

        dxfattr = self.dxfattribs.get(key, None)
        if dxfattr is None:
            return False
        if dxfattr.dxfversion is None:
            return True
        return self._entity.dxfversion >= dxfattr.dxfversion

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


class AppData:
    def __init__(self):
        self.data = OrderedDict()

    def __contains__(self, appid: str) -> bool:
        return uniform_appid(appid) in self.data

    def __len__(self) -> int:
        return len(self.data)

    def get(self, appid: str) -> Tags:
        return self.data[uniform_appid(appid)]

    def add(self, data: List) -> None:
        appid = uniform_appid(data[0][1])
        self.data[appid] = Tags(dxftag(code, value) for code, value in data)

    def new(self, appid: str, tags: Union[Tags, List, Iterable]):
        data = [DXFTag(102, uniform_appid(appid))]
        data.extend(tags)
        data.append(DXFTag(102, '}'))
        self.add(data)

    def delete(self, appid: str):
        _appid = uniform_appid(appid)
        if _appid in self.data:
            del self.data[_appid]
        else:
            raise DXFKeyError("Invalid appid {}".format(appid))

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        for data in self.data.values():
            tagwriter.write_tags(data)


class Reactors:
    """ Handle storage for related reactors.

    Reactors are other objects related to the object that contains this Reactor() instance.

    """

    def __init__(self, handles: Iterable[str] = None):
        self.reactors = None  # type: Set[str]  # stores handle strings
        self.set(handles)

    def __len__(self) -> int:
        return len(self.reactors)

    def __contains__(self, handle):
        return handle in self.reactors

    @classmethod
    def from_tags(cls, tags: Tags = None) -> 'Reactors':
        """
        Create Reactors() instance from tags.

        Expected DXF structure: [(102, '{ACAD_REACTORS'), (330, handle), ...,(102, '}')]

        Args:
            tags: list of DXFTags()

        """
        if tags is None:
            return cls(None)

        if len(tags) < 3:
            raise DXFStructureError("ACAD_REACTORS error")
        return cls((handle.value for handle in tags[1:-1]))

    def get(self) -> List[str]:
        return sorted(self.reactors)

    def set(self, handles: Iterable[str]) -> None:
        self.reactors = set(handles or [])

    def add(self, handle: str) -> None:
        self.reactors.add(handle)

    def discard(self, handle: str):
        self.reactors.discard(handle)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(APP_DATA_MARKER, ACAD_REACTORS)
        for handle in self.get():
            tagwriter.write_tag2(REACTOR_HANDLE_CODE, handle)
        tagwriter.write_tag2(APP_DATA_MARKER, '}')


class ExtensionDict:
    def __init__(self, owner: 'DXFEntity', handle=None):
        self.owner = owner
        # _dict is None -> empty dict
        # _dict as string -> handle to dict
        # _dict as DXFDictionary
        self._xdict = handle  # type: Union[str, DXFDictionary, None]

    @classmethod
    def from_tags(cls, entity: 'DXFEntity', tags: Tags = None):
        if tags is None:
            return cls(entity, None)

        # expected DXF structure: [(102, '{ACAD_XDICTIONARY', (360, handle), (102, '}')]
        if len(tags) != 3 or tags[1].code != XDICT_HANDLE_CODE:
            raise DXFStructureError("ACAD_XDICTIONARY error in entity: " + str(entity))
        return cls(entity, tags[1].value)

    @property
    def doc(self) -> 'Drawing':
        return self.owner.doc

    def get(self) -> 'DXFDictionary':
        """
        Get associated extension dictionary as DXFDictionary() object.

        """
        if self._xdict is None:
            self._xdict = self._new()
        elif isinstance(self._xdict, str):
            # replace handle string by DXFDictionary object
            self._xdict = cast('DXFDictionary', self.owner.entitydb.get(self._xdict))
        return self._xdict

    def _new(self) -> 'DXFDictionary':
        xdict = self.doc.objects.add_dictionary(owner=self.owner.dxf.handle)
        return cast('DXFDictionary', xdict)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        xdict = self._xdict
        if xdict is None:
            return
        handle = xdict if isinstance(xdict, str) else xdict.dxf.handle
        tagwriter.write_tag2(APP_DATA_MARKER, ACAD_XDICTIONARY)
        tagwriter.write_tag2(XDICT_HANDLE_CODE, handle)
        tagwriter.write_tag2(APP_DATA_MARKER, '}')


class XData:
    def __init__(self, xdata: List[Tags]):
        self.data = xdata

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        for tags in self.data:
            tagwriter.write_tags(tags)


class EmbeddedObjects:
    def __init__(self, embedded_objects: List[Tags]):
        self.embedded_objects = embedded_objects

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        for tags in self.embedded_objects:
            tagwriter.write_tags(tags)


class DXFEntity:
    DXFTYPE = 'DXFENTITY'  # storing as class var needs less memory
    DXFATTRIBS = DXFAttributes(main_class)  # DXF attribute definitions
    DEFAULT_ATTRIBS = None
    DEFAULT_R12_ATTRIBS = None

    def __init__(self, tags: ExtendedTags = None, doc: 'Drawing' = None):
        self.doc = doc
        self.appdata = AppData()  # same process for every entity
        self.reactors = None  # type: Reactors
        self.extension_dict = None  # type: ExtensionDict
        if tags is not None:
            self.setup_app_data(tags.appdata)
            self.xdata = XData(tags.xdata)  # same process for every entity
            self.embedded_objects = EmbeddedObjects(tags.embedded_objects)  # same process for every entity
            self.dxf = self.setup_dxf_attribs(tags.subclasses)
            # todo: set owner for DXF R12 read from file
        else:
            self.xdata = None
            self.embedded_objects = None
            self.dxf = self.setup_dxf_attribs(self.default_subclasses())

    @classmethod
    def new(cls, handle: str, owner: str = None, dxfattribs: dict = None, doc: 'Drawing' = None) -> 'DXFEntity':
        dxfversion = doc.dxfversion if doc is not None else DXF12
        if dxfversion <= DXF12 and cls.DEFAULT_R12_ATTRIBS is None:
            raise DXFVersionError("DXF type {} not supported by DXF R12".format(cls.DXFTYPE))
        if cls.DEFAULT_ATTRIBS is None:
            raise DXFTypeError("new() for DXF type {} not supported".format(cls.DXFTYPE))

        entity = cls(None, doc)
        entity.dxf.handle = handle
        entity.dxf.owner = owner  # set also for DXF R12 for internal usage
        dxfversion = doc.dxfversion if doc else DXF12
        default_attribs = dict(cls.DEFAULT_ATTRIBS) if dxfversion > DXF12 else cls.DEFAULT_R12_ATTRIBS
        default_attribs.update(dxfattribs or {})
        entity.update_dxf_attribs(default_attribs)
        entity.post_new_hook()
        return entity

    def update_dxf_attribs(self, dxfattribs: dict) -> None:
        for key, value in dxfattribs.items():
            self.set_dxf_attrib(key, value)

    def default_subclasses(self) -> List[Tags]:
        return [Tags([
            DXFTag(STRUCTURE_MARKER, self.DXFTYPE),
            DXFTag(handle_code(self.DXFTYPE), '0'),
            DXFTag(OWNER_CODE, '0'),
        ])]

    def post_new_hook(self):
        pass

    def setup_dxf_attribs(self, subclasses: List) -> DXFNamespace:
        # hook for inherited classes
        return DXFNamespace(subclasses, self)

    def setup_app_data(self, appdata: List[Tags]) -> None:
        for data in appdata:
            appid = data[0].value
            if appid == '{REACTORS':
                self.reactors = Reactors.from_tags(data)
            elif appid == '{XDICTIONARY':
                self.extension_dict = ExtensionDict.from_tags(self, data)
            else:
                self.appdata.add(data)

    @property
    def dxffactory(self) -> 'DXFFactoryType':
        return self.doc.dxffactory

    @property
    def dxfversion(self) -> str:
        if self.doc:
            return self.doc.dxfversion
        else:
            return DXF12

    def get_dxf_attrib(self, key: str, default: Any) -> Any:
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
        return "{}(#{})".format(self.dxf.dxftype, self.dxf.handle)

    def __repr__(self) -> str:
        """
        Returns a simple string representation including the class.

        """
        return str(self.__class__) + " " + str(self)

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
        if self.dxfversion >= DXF2000:
            tagwriter.write_tag2(handle_code(self.dxf.dxftype), self.dxf.handle)
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
        # base class (handle, appoid, reactors, xdict, owner) export is done by parent class
        pass
        # xdata and embedded objects  export is also done by parent

    def export_xdata(self, tagwriter: 'TagWriter') -> None:
        if self.xdata:
            self.xdata.export_dxf(tagwriter)

    def export_embedded_objects(self, tagwriter: 'TagWriter') -> None:
        if self.embedded_objects:
            self.embedded_objects.export_dxf(tagwriter)

    def has_extension_dict(self) -> bool:
        return self.extension_dict is not None

    def get_extension_dict(self) -> 'DXFDictionary':
        """
        Get associated extension dictionary as DXFDictionary() instance, or create new extension dictionary.

        """

        def new_extension_dict():
            """
            Creates and assigns a new extensions dictionary. Link to an existing extension dictionary will be lost.

            """
            self.extension_dict = ExtensionDict(self)
            return self.extension_dict.get()

        if self.has_extension_dict():
            return self.extension_dict.get()
        else:
            return new_extension_dict()


class UnknownEntity(DXFEntity):
    """ Just store all the tags as they are """

    def __init__(self, tags: ExtendedTags, doc=None):
        super().__init__(tags, doc)
        # no need to store base class
        # but store DXFTYPE, overrides class member
        # 1. tag of 1. subclass is the structure tag (0, DXFTYPE)
        self.DXFTYPE = tags.subclasses[0][0].value
        self._subclasses = tags.subclasses[1:]

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Write subclass tags as they are
        """
        # base class export is done by parent
        for subclass in self._subclasses:
            tagwriter.write_tags(subclass)

        # xdata and embedded objects  export is done by parent

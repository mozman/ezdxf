# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-12
# concept for new entity system

# Goals:
# ------
#
# 1. No more wrapped entities
# 2. Store entities as DXFEntities in the drawing database
# 3. remove separation of legacy and modern tag structure definitions
# 4. still store unknown entities (Map3d...) as bunch of tag, but inside of an special DXFEntity (UnknownEntity)
# 5. preserve actual DXFEntity interface, DXFEntity.dxf seem still a good idea - other methods deprecate slowly
# 6. DXFTag and ExtendedTags are no more the main data types - store dxf attributes as object attributes in
#    sub objects of DXFEntity
# 7. compose modern entities form DXFSubclass() objects, DXF R12 has only one DXFSubclass()
# 8. for saving convert entity to Tags() object, each entity could have its own individual method
#
# new subpackage ezdxf.entities
# every DXF type get a module
from typing import Iterable, List
from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType


def handle_code(dxftype: str) -> int:
    return 105 if dxftype == 'DIMSTYLE' else 5


main_class = DefSubclass(None, {
    'handle': DXFAttr(5),
    'owner': DXFAttr(330, dxfversion='AC1015'),  # Soft-pointer ID/handle to owner BLOCK_RECORD object
    # Application defined data can only appear here:
    # {APPID
    # {ACAD_REACTORS
    # {ACAD_XDICTIONARY
})

entity_subclass = DefSubclass('AcDbEntity', {
    'layer': DXFAttr(8, default='0'),  # layername as string
    'linetype': DXFAttr(6, default='BYLAYER'),  # linetype as string, special names BYLAYER/BYBLOCK
    'color': DXFAttr(62, default=256),  # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER
    'paperspace': DXFAttr(67, default=0),  # 0 .. modelspace, 1 .. paperspace
    # thickness and extrusion is defined in Entity specific subclasses
    'lineweight': DXFAttr(370, dxfversion='AC1015'),  # Stored and moved around as a 16-bit integer
    # Line weight in mm times 100 (e.g. 0.13mm = 13). Smallest line weight is 13 and biggest line weight is 200, values
    # outside this range prevents AutoCAD from loading the file.
    # Special values:
    # LINEWEIGHT_BYLAYER = -1
    # LINEWEIGHT_BYBLOCK = -2
    # LINEWEIGHT_DEFAULT = -3
    'ltscale': DXFAttr(48, default=1.0, dxfversion='AC1015'),  # linetype scale
    'invisible': DXFAttr(60, default=0, dxfversion='AC1015'),  # invisible .. 1, visible .. 0
    'true_color': DXFAttr(420, dxfversion='AC1018'),  # true color as 0x00RRGGBB 24-bit value
    'color_name': DXFAttr(430, dxfversion='AC1018'),  # color name as string
    'transparency': DXFAttr(440, dxfversion='AC1018'),
    # transparency value 0x020000TT 0 = fully transparent / 255 = opaque
    'shadow_mode': DXFAttr(284, dxfversion='AC1021'),  # shadow_mode
    # 0 = Casts and receives shadows
    # 1 = Casts shadows
    # 2 = Receives shadows
    # 3 = Ignores shadows
})


class DXFAttribs:  # different for every DXF type
    """
    Uses the Python object itself as attribute storage, only valid Python names can be used as attrib name.

    Ignore invalid dxf attributes at first for simplicity, DXF validation can be added later.
    Invalid attributes will not be written by the export function.

    """
    # how to implement DXF R12 and DXF R2000+ support by just one DXF attribute definition?
    # for DXF R12 has no subclasses -> use DXF R2000+ definition and just ignore subclasses?

    DXFATTRIBS = DXFAttributes(main_class, entity_subclass)

    def __init__(self, subclasses: List[Tags], doc):
        assert len(subclasses)
        mainclass = subclasses[0]

        # bypass __setattr__() because without DXF attributes definition
        self.__dict__['dxfversion'] = doc.dxfversion
        self.__dict__['dxftype'] = mainclass[0].value  # value of first tag is always the dxftype e.g. (0, LINE)
        code = handle_code(self.dxftype)
        self.handle = mainclass.get_first_value(code, None)  # CLASS entity has no handle
        if self.dxfversion > 'AC1009':
            self.owner = mainclass.get_first_value(330, None)  # owner

    def __getattr__(self, key: str):
        """ called if key does not exist """
        if self.is_supported(key):
            return self.dxf_default_value(key)
        else:
            raise AttributeError()

    def __setattr__(self, key, value):
        if hasattr(self, key) or self.is_supported(key):
            self.__dict__[key] = value
        else:
            raise AttributeError()

    def get(self, key: str, default):
        try:
            return getattr(self, key)
        except AttributeError:
            if self.is_supported(key):
                return default
            else:
                raise AttributeError()

    def set(self, key: str, value):
        self.__setattr__(key, value)

    def delete(self, key: str):
        delattr(self, key)

    def is_supported(self, key: str) -> bool:
        """
        Returns True if DXF attribute `key` is supported else False. Does not grant that attribute `key` really exists.

        """
        dxfattr = self.DXFATTRIBS.get(key, None)
        if dxfattr is None:
            return False
        if dxfattr.dxfversion is None:
            return True
        return self._dxfversion >= dxfattr.dxfversion

    def hasattr(self, key: str) -> bool:
        """
        Returns True if attribute `key` really exists else False.

        Does no check if attribute `key` is supported, but implicit supported if exists.

        """
        return hasattr(self, key)

    def dxf_default_value(self, key: str):
        """
        Returns the default value as defined in the DXF standard.

        """
        attrib = self.DXFATTRIBS.get(key, None)
        if attrib:
            return attrib.default
        else:
            raise AttributeError()


class AppData:
    def __init__(self):
        self.data = dict()

    def __contains__(self, appid):
        return appid in self.data

    def get(self, appid):
        return self.data[appid]

    def add(self, data):
        appid = data[0].value
        self.data[appid] = data

    def new(self, appid, tags):
        data = [DXFTag(102, appid)]
        data.extend(tags)
        data.append(DXFTag(102, '}'))
        self.add(data)

    def delete(self, appid):
        del self.data[appid]

    def export_dxf(self, tagwriter):
        for data in self.data.values():
            tagwriter.write_tags(data)


class Reactors:
    def __init__(self, reactors):
        pass

    def export_dxf(self, tagwriter):
        pass


class ExtensionDict:
    def __init__(self, xdict):
        pass

    def export_dxf(self, tagwriter):
        pass


class XData:
    def __init__(self, xdata):
        self.data = xdata

    def export_dxf(self, tagwriter):
        for tags in self.data:
            tagwriter.write_tags(tags)


class DXFEntity:
    TEMPLATE = None
    CLASS = None
    DXFATTRIBS = {}

    def __init__(self, tags: ExtendedTags = None, doc=None):
        self.doc = doc
        self.appdata = AppData()  # same process for every entity
        self.reactors = None
        self.extension_dict = None
        self.setup_app_data(tags.appdata)
        self.xdata = XData(tags.xdata)  # same process for every entity
        self.embedded_objects = tags.embedded_objects  # same process for every entity
        self.dxf = self.setup_dxf_attribs(tags.subclasses)  # different for every DXF type

    def setup_dxf_attribs(self, subclasses):
        return DXFAttribs(subclasses, self.doc)  # differs for every entity type

    def setup_app_data(self, appdata):
        for data in appdata:
            appid = data[0].value
            if appid == '{REACTORS':
                self.reactors = Reactors(data)
            elif appid == '{XDICTIONARY':
                self.extension_dict = ExtensionDict(data)
            else:
                self.appdata.add(data)

    def export_dxf(self, tagwriter):
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

    def export_base_class(self, tagwriter):
        if self.dxfversion >= 'AC1015':
            tagwriter.write_tag2(handle_code(self.dxf.dxftype), self.dxf.handle)
            self.appdata.export_dxf(tagwriter)
            if self.reactors:
                self.reactors.export_dxf(tagwriter)
            if self.extension_dict:
                self.extension_dict.export_dxf(tagwriter)
            tagwriter.write_tag2(330, self.dxf.owner)
        else:  # DXF R12
            if tagwriter.write_handles:
                tagwriter.write_tag2(handle_code(self.dxf.dxftype), self.dxf.handle)

    def export_entity(self, tagwriter):
        """ Export DXF entity specific data by tagwriter

        This is a key method:

        - has to know the group codes for each attribute
        - has to add subclass tags in correct order
        - has to maintain the correct tag order (because sometimes order matters)

        """
        pass

    def export_xdata(self, tagwriter):
        if self.xdata:
            self.xdata.export_dxf(tagwriter)

    def export_embedded_objects(self, tagwriter):
        if self.embedded_objects:
            for tags in self.embedded_objects:
                tagwriter.write_tags(tags)

    @property
    def dxfversion(self):
        if self.doc:
            return self.doc.dxfversion
        else:
            return 'AC1009'

    def get_dxf_attrib(self, key, default):
        self.dxf.get(key, default)

    def set_dxf_attrib(self, key, value):
        self.dxf.set(key, value)

    def del_dxf_attrib(self, key: str):
        self.dxf.delete(key)


class UnknownAttribs(DXFAttribs):
    def __setattr__(self, key, value):
        raise AttributeError('Unknown entity is immutable.')


class UnknownEntity(DXFEntity):
    """ Just store all the tags as they are """

    def __init__(self, tags: ExtendedTags, doc=None):
        super().__init__(tags, doc)
        # no need to store base class
        self._subclasses = tags.subclasses[1:]

    def setup_dxf_attribs(self, subclasses):
        return UnknownEntity(subclasses, self.doc)

    def export_entity(self, tagwriter):
        """ Write subclass tags as they are
        """
        # base class export is done by parent
        for subclass in self._subclasses:
            tagwriter.write_tags(subclass)

        # xdata and embedded objects  export is done by parent


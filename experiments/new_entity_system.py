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
# 4. still store unknown entities (Map3d...) as bunch of tag, but inside of an special DXFEntity (ForeignEntity)
# 5. preserve actual DXFEntity interface, DXFEntity.dxf seem still a good idea - other methods deprecate slowly
# 6. DXFTag and ExtendedTags are no more the main data types - store dxf attributes as object attributes in
#    sub objects of DXFEntity
# 7. compose modern entities form DXFSubclass() objects, DXF R12 has only one DXFSubclass()
# 8. for saving convert entity to Tags() object, each entity could have its own individual method
#
# new subpackage ezdxf.entities
# every DXF type get a module

from ezdxf.lldxf.extendedtags import ExtendedTags


class DXFAttribs:  # different for every DXF type
    def __init__(self, subclasses, doc):
        pass

    def get_dxf_attrib(self, key, default):
        pass

    def set_dxf_attrib(self, key, value):
        pass

    def del_dxf_attrib(self, key: str):
        pass


class AppData:
    pass


class XData:
    pass


class EmbeddedObjects:
    pass


class DXFNamespace:
    __slots__ = ('_dxfattribs',)

    def __init__(self, dxfattribs):
        super(DXFNamespace, self).__setattr__('_dxfattribs', dxfattribs)

    def __getattr__(self, attrib):
        return self.dxfattribs.get_dxf_attrib(attrib)

    def __setattr__(self, attrib: str, value) -> None:
        return self.dxfattribs.set_dxf_attrib(attrib, value)

    def __delattr__(self, attrib: str) -> None:
        return self.dxfattribs.del_dxf_attrib(attrib)


class DXFEntity:
    TEMPLATE = None
    CLASS = None
    DXFATTRIBS = {}

    def __init__(self, tags: ExtendedTags = None, doc=None):
        self.doc = doc
        self.appdata = AppData(tags.appdata)  # same process for every entity
        self.xdata = XData(tags.xdata)  # same process for every entity
        self.embeddedobjects = EmbeddedObjects(tags.embedded_objects)  # same process for every entity
        self.dxfattribs = self.setup_dxf_attribs(tags.subclasses)  # different for every DXF type
        self.dxf = DXFNamespace(self.dxfattribs)  # # same process for every entity

    def setup_dxf_attribs(self, subclasses):
        return DXFAttribs(subclasses, self.doc)  # differs for every entity type

    def export_dxf(self, tagwriter):
        """ Export DXF entity by tagwriter

        This is a key method:

        - has to know the group codes for each attribute
        - has to add subclass tags in correct order
        - has to integrate extended data: ExtensionDict, Reactors, AppData
        - has to maintain the correct tag order (because sometimes order matters)

        """

        # some features can be done the same way for all entities:
        # ! Last step !
        self.export_xdata(tagwriter)
        self.export_embedded_objects(tagwriter)

    def export_xdata(self, tagwriter):
        pass

    def export_embedded_objects(self, tagwriter):
        pass

    @property
    def dxfversion(self):
        return self.doc.dxfversion

    def get_dxf_attrib(self, key, default):
        self.dxfattribs.get_dxf_attrib(key, default)

    def set_dxf_attrib(self, key, value):
        self.dxfattribs.set_dxf_attrib(key, value)

    def del_dxf_attrib(self, key: str):
        self.dxfattribs.del_dxf_attrib(key)



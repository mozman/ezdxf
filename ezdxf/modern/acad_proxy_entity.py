# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity, DefSubclass, DXFAttr, DXFAttributes
from .dxfobjects import DXFObject

proxy_entity_subclass = DefSubclass('AcDbProxyEntity', {
    'class_id': DXFAttr(90),  # Proxy entity class ID (always 498 for ACAD_PROXY_ENTITY, always 499 for ACAD_PROXY_OBJECT)
    'app_class_id': DXFAttr(91),  # Application entity's class ID. Class IDs are based on the order of the class in the CLASSES section. The first class is given the ID of 500, the next is 501, and so on
    'size_graphic': DXFAttr(92),  # Size of graphics data in bytes
    # Binary graphic data (multiple entries can appear) (optional)
    'size_data': DXFAttr(93),  # Size of graphics data in bytes
    # Binary entity data (multiple entries can appear) (optional)
    # 330 or 340 or 350 or 360 - An object ID (multiple entries can appear) (optional)
    # (94, 0) (indicates end of object ID section)
    'drawing_version': DXFAttr(95),  # Object drawing format when it becomes a proxy (a 32-bit unsigned integer):
    # Low word is AcDbDwgVersion
    # High word is MaintenanceReleaseVersion
    'drawing_format': DXFAttr(70),  # Original custom object data format: 0 = DWG format; 1 = DXF format
})


class ProxyMixin(object):
    __slots__ = ()

    def get_proxy_graphic(self):
        # TODO: get_proxy_graphic()
        raise NotImplementedError()

    def get_proxy_data(self):
        # TODO: get_proxy_data()
        raise NotImplementedError()

    def get_object_ids(self):
        # TODO: get_object_ids()
        raise NotImplementedError()


class ProxyEntity(ModernGraphicEntity, ProxyMixin):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, proxy_entity_subclass)


class ProxyObject(DXFObject, ProxyMixin):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, proxy_entity_subclass)

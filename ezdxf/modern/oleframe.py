# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity, DefSubclass, DXFAttr, DXFAttributes

oleframe_subclass = DefSubclass('AcDbOleFrame', {
    'version': DXFAttr(70),  # OLE version number
    'length': DXFAttr(90),  # Length of binary data
    # 310: Binary data (multiple lines)
    # 1: End of OLE data (the string “OLE”)
})


class OLEFrame(ModernGraphicEntity):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, oleframe_subclass)


ole2frame_subclass = DefSubclass('AcDbOle2Frame', {
    'version': DXFAttr(70),  # OLE version number
    'type': DXFAttr(3),  # content type as string e.g. "Paintbrush Picture"
    'upper_left_corner': DXFAttr(10, xtype='Point3D'),  # Upper-left corner (WCS)
    'lower_right_corner': DXFAttr(11, xtype='Point3D'),  # Upper-left corner (WCS)
    'ole_object_type': DXFAttr(71),  # OLE object type, 1 = Link; 2 = Embedded; 3 = Static
    'ole_tile_mode': DXFAttr(72),  # Tile mode descriptor: 0 = Object resides in model space; 1 = Object resides in paper space
    'length': DXFAttr(90),  # Length of binary data
    # 310: Binary data (multiple lines)
    # 1: End of OLE data (the string “OLE”)
})


class OLE2Frame(ModernGraphicEntity):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, ole2frame_subclass)

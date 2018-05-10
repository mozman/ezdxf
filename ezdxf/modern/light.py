# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity


_LIGHT_TPL = """0
LIGHT
5
0
330
0
100
AcDbEntity
8
0
100
AcDbLight
90
0
1
NAME
70
1
290
1
291
0
40
1.0
72
2
292
0
293
1
73
0
"""

light_subclass = DefSubclass('AcDbLight', {
    'version': DXFAttr(90),  # Version number
    'name': DXFAttr(1),  # Light name
    'type': DXFAttr(70),  # Light type: 1=distant; 2=point; 3=spot;
    'status': DXFAttr(290),  # on/off ???
    'plot_glyph': DXFAttr(291),  # no/yes
    'intensity': DXFAttr(40),
    'location': DXFAttr(10, xtype='Point3D'),  # Light position
    'target': DXFAttr(11, xtype='Point3D'),  # Target location
    'attenuation_type': DXFAttr(72),  # Attenuation type:
    # 0 = None
    # 1 = Inverse Linear
    # 2 = Inverse Square
    'use_attenuation_limits': DXFAttr(292),  # Use attenuation limits
    'attenuation_start_limits': DXFAttr(41),  # Attenuation start limit
    'attenuation_end_limits': DXFAttr(42),  # Attenuation end limit
    'hotspot_angle': DXFAttr(50),  # Hotspot angle
    'falloff_angle': DXFAttr(51),  # Falloff angle
    'cast_shadows': DXFAttr(293),  # Cast shadows
    'shadow_type': DXFAttr(73),  # Shadow Type: 0 = Ray traced shadows; 1 = Shadow maps
    'shadow_map_size': DXFAttr(91),  # Shadow map size
    'shadow_map_softness': DXFAttr(280),  # Shadow map softness

})


class Light(ModernGraphicEntity):
    # Requires AC1021/R2007
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_LIGHT_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, light_subclass)

    @property
    def AcDbLight(self):
        return self.tags.subclasses[2]

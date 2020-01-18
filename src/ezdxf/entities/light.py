# Copyright (c) 2019, Manfred Moitzi
# License: MIT-License
# Created: 2019-03-11
from typing import TYPE_CHECKING
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2007
from ezdxf.lldxf.attributes import DXFAttributes, DefSubclass, DXFAttr, XType
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import acdb_entity, DXFGraphic
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['Light']

acdb_light = DefSubclass('AcDbLight', {
    'version': DXFAttr(90, default=0),  # Version number
    'name': DXFAttr(1, default=''),  # Light name
    'type': DXFAttr(70, default=1),  # Light type: 1=distant; 2=point; 3=spot;
    'status': DXFAttr(290, default=1),  # on/off ???
    'plot_glyph': DXFAttr(291, default=0),  # no/yes
    'intensity': DXFAttr(40, default=1),
    'location': DXFAttr(10, xtype=XType.point3d),  # Light position
    'target': DXFAttr(11, xtype=XType.point3d),  # Target location
    'attenuation_type': DXFAttr(72, default=2),  # Attenuation type:
    # 0 = None
    # 1 = Inverse Linear
    # 2 = Inverse Square
    'use_attenuation_limits': DXFAttr(292, default=0),  # Use attenuation limits
    'attenuation_start_limits': DXFAttr(41),  # Attenuation start limit
    'attenuation_end_limits': DXFAttr(42),  # Attenuation end limit
    'hotspot_angle': DXFAttr(50),  # Hotspot angle
    'falloff_angle': DXFAttr(51),  # Falloff angle
    'cast_shadows': DXFAttr(293, default=1),  # Cast shadows
    'shadow_type': DXFAttr(73, default=0),  # Shadow Type: 0 = Ray traced shadows; 1 = Shadow maps
    'shadow_map_size': DXFAttr(91),  # Shadow map size
    'shadow_map_softness': DXFAttr(280),  # Shadow map softness
})


@register_entity
class Light(DXFGraphic):
    """ DXF LIGHT entity """
    DXFTYPE = 'LIGHT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_light)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2007

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.load_dxfattribs_into_namespace(dxf, acdb_light)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_light.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'version', 'name', 'type', 'status', 'plot_glyph', 'intensity', 'location', 'target', 'attenuation_type',
            'use_attenuation_limits', 'attenuation_start_limits', 'attenuation_end_limits', 'hotspot_angle',
            'falloff_angle', 'cast_shadows', 'shadow_type', 'shadow_map_size', 'shadow_map_softness'
        ])



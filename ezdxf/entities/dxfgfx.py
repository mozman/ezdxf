# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# DXFGraphic - graphical DXF entities stored in ENTITIES and BLOCKS sections
from typing import TYPE_CHECKING, Optional, Tuple, List
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, DXF2000, DXF2004, DXF2007, SUBCLASS_MARKER
from .dxfentity import DXFEntity, base_class, DXFNamespace, SubclassProcessor
from ezdxf.math import OCS
from ezdxf.tools.rgb import int2rgb, rgb2int
from ezdxf.tools import float2transparency, transparency2float

if TYPE_CHECKING:
    from ezdxf.lldxf.tagwriter import TagWriter

acdb_entity = DefSubclass('AcDbEntity', {
    'layer': DXFAttr(8, default='0'),  # layername as string
    'linetype': DXFAttr(6, default='BYLAYER'),  # linetype as string, special names BYLAYER/BYBLOCK
    'color': DXFAttr(62, default=256),  # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER
    'paperspace': DXFAttr(67, default=0),  # 0 .. modelspace, 1 .. paperspace
    # thickness and extrusion is defined in Entity specific subclasses
    'lineweight': DXFAttr(370, default=-1, dxfversion=DXF2000),  # Stored and moved around as a 16-bit integer
    # Line weight in mm times 100 (e.g. 0.13mm = 13). Smallest line weight is 13 and biggest line weight is 200, values
    # outside this range prevents AutoCAD from loading the file.
    # Special values:
    # LINEWEIGHT_BYLAYER = -1
    # LINEWEIGHT_BYBLOCK = -2
    # LINEWEIGHT_DEFAULT = -3
    #
    'ltscale': DXFAttr(48, default=1.0, dxfversion=DXF2000),  # linetype scale
    'invisible': DXFAttr(60, default=0, dxfversion=DXF2000),  # invisible .. 1, visible .. 0
    'true_color': DXFAttr(420, dxfversion=DXF2004),  # true color as 0x00RRGGBB 24-bit value
    'color_name': DXFAttr(430, dxfversion=DXF2004),  # color name as string
    'transparency': DXFAttr(440, dxfversion=DXF2004),
    # transparency value 0x020000TT 0 = fully transparent / 255 = opaque
    'shadow_mode': DXFAttr(284, dxfversion=DXF2007),  # shadow_mode
    # 0 = Casts and receives shadows
    # 1 = Casts shadows
    # 2 = Receives shadows
    # 3 = Ignores shadows
})


class DXFGfx(DXFEntity):
    DXFTYPE = 'DXFGFX'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity)  # DXF attribute definitions

    def setup_dxf_attribs(self, processor: SubclassProcessor = None) -> DXFNamespace:
        dxf = super().setup_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_entity)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass='AcDbEntity')
        return dxf

    def post_new_hook(self):
        # todo: check valid layer name
        # todo: check valid linetype, AutoCAD is very picky
        pass

    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        if self.dxf.hasattr('true_color'):
            return int2rgb(self.dxf.get('true_color'))
        else:
            return None

    @rgb.setter  # line.rgb = (12, 34, 56)
    def rgb(self, rgb: Tuple[int, int, int]) -> None:
        self.dxf.set('true_color', rgb2int(rgb))

    @property
    def transparency(self) -> float:
        # 0.0 = opaque & 1.0 if 100% transparent
        if self.dxf.hasattr('transparency'):
            return transparency2float(self.dxf.get('transparency'))
        else:
            return 0.

    @transparency.setter  # line.transparency = 0.50
    def transparency(self, transparency: float) -> None:
        # 0.0 = opaque & 1.0 if 100% transparent
        self.dxf.set('transparency', float2transparency(transparency))

    def ocs(self) -> Optional[OCS]:
        # extrusion is only defined for 2D entities like Text, Circle, ...
        if self.dxf.is_supported('extrusion'):
            extrusion = self.dxf.get('extrusion', default=(0, 0, 1))
            return OCS(extrusion)
        else:
            return None

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export DXF entity specific data by tagwriter """
        # base class (handle, appoid, reactors, xdict, owner) export is done by parent class
        self.export_acdb_entity(tagwriter)
        # xdata and embedded objects  export is also done by parent

    def export_acdb_entity(self, tagwriter: 'TagWriter'):
        attribs = self.dxf
        # Full control over tag order and YES, sometimes order matters
        dxfversion = tagwriter.dxfversion
        if dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_entity.name)
        # for all DXF versions
        attribs.export_dxf_attribute(tagwriter, 'layer', force=True)
        attribs.export_dxf_attribs(tagwriter, ['linetype', 'color', 'paperspace'])
        if dxfversion >= DXF2000:
            attribs.export_dxf_attribs(tagwriter, ['lineweight', 'ltscale'])
        if dxfversion >= DXF2004:
            attribs.export_dxf_attribs(tagwriter, ['true_color', 'color_name', 'transparency'])
        if dxfversion >= DXF2004:
            attribs.export_dxf_attribute(tagwriter, 'shadow_mode')

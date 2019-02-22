# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# DXFGraphic - graphical DXF entities stored in ENTITIES and BLOCKS sections
from typing import TYPE_CHECKING, Optional, Tuple
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, DXF2000, DXF2004, DXF2007, SUBCLASS_MARKER, DXFInvalidLayerName, DXFInvalidLineType
from ezdxf.lldxf.validator import is_valid_layer_name
from .dxfentity import DXFEntity, base_class, SubclassProcessor
from ezdxf.math import OCS
from ezdxf.tools.rgb import int2rgb, rgb2int
from ezdxf.tools import float2transparency, transparency2float

if TYPE_CHECKING:
    from ezdxf.eztypes import Auditor, TagWriter
    from .dxfentity import DXFNamespace

__all__ = ['DXFGraphic', 'acdb_entity']

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


class DXFGraphic(DXFEntity):
    """
    Base class for all graphical DXF entities like Text() or Line().

    This entities resides in entity spaces like modelspace, any paperspace or blocks.
    """
    DXFTYPE = 'DXFGFX'
    DEFAULT_ATTRIBS = {'layer': '0'}
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity)  # DXF attribute definitions

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        """ Adds subclass processing for 'AcDbEntity', requires previous base class processing by parent class. """
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_entity)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_entity.name)
        return dxf

    def post_new_hook(self):
        ns = self.dxf
        if not is_valid_layer_name(ns.layer):
            raise DXFInvalidLayerName(ns.layer)

        if ns.hasattr('linetype'):
            if ns.linetype not in self.doc.linetypes:
                raise DXFInvalidLineType('Linetype "{}" not defined.'.format(ns.linetype))

    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        """ Returns RGB true color as (red, green, blue) tuple or None if true_color is not set. """
        if self.dxf.hasattr('true_color'):
            return int2rgb(self.dxf.get('true_color'))
        else:
            return None

    @rgb.setter
    def rgb(self, rgb: Tuple[int, int, int]) -> None:
        """ Set RGB true color as (red, green , blue) tuple e.g. (12, 34, 56) . """
        self.dxf.set('true_color', rgb2int(rgb))

    @property
    def transparency(self) -> float:
        """ Get transparency as float value between 0 and 1, 0 is opaque and 1 is fully transparent (invisible) """
        if self.dxf.hasattr('transparency'):
            return transparency2float(self.dxf.get('transparency'))
        else:
            return 0.

    @transparency.setter
    def transparency(self, transparency: float) -> None:
        """ Set transparency as float value between 0 and 1, 0 is opaque and 1 is fully transparent (invisible) """
        self.dxf.set('transparency', float2transparency(transparency))

    def ocs(self) -> Optional[OCS]:
        """
        Return object coordinate system (OCS) for 2D entities like Text() or Circle().
        Returns None for entities without OCS support.

        """
        # extrusion is only defined for 2D entities like Text, Circle, ...
        if self.dxf.is_supported('extrusion'):
            extrusion = self.dxf.get('extrusion', default=(0, 0, 1))
            return OCS(extrusion)
        else:
            return None

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class (handle, appid, reactors, xdict, owner) export is done by parent class
        self.export_acdb_entity(tagwriter)
        # xdata and embedded objects  export is also done by parent

    def export_acdb_entity(self, tagwriter: 'TagWriter'):
        """ Export subclass 'AcDbEntity' as DXF tags. """
        # Full control over tag order and YES, sometimes order matters
        dxfversion = tagwriter.dxfversion
        if dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_entity.name)
        # for all DXF versions
        self.dxf.export_dxf_attribute(tagwriter, 'layer', force=True)
        self.dxf.export_dxf_attribs(tagwriter, ['linetype', 'color', 'paperspace'])
        if dxfversion >= DXF2000:
            self.dxf.export_dxf_attribs(tagwriter, ['lineweight', 'ltscale'])
        if dxfversion >= DXF2004:
            self.dxf.export_dxf_attribs(tagwriter, ['true_color', 'color_name', 'transparency'])
        if dxfversion >= DXF2004:
            self.dxf.export_dxf_attribute(tagwriter, 'shadow_mode')

    def audit(self, auditor: 'Auditor') -> None:
        super().audit(auditor)
        auditor.check_for_valid_layer_name(self)
        auditor.check_if_linetype_exists(self)
        auditor.check_for_valid_color_index(self)
        auditor.check_pointer_target_exists(self, zero_pointer_valid=False)

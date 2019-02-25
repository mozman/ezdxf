# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# DXFGraphic - graphical DXF entities stored in ENTITIES and BLOCKS sections
from typing import TYPE_CHECKING, Optional, Tuple
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, DXF2000, DXF2004, DXF2007, DXFValueError, DXFKeyError, DXFTableEntryError
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXFInvalidLayerName, DXFInvalidLineType, DXFUnsupportedFeature
from ezdxf.math import Vector, UCS
from ezdxf.lldxf.validator import is_valid_layer_name
from .dxfentity import DXFEntity, base_class, SubclassProcessor
from ezdxf.math import OCS
from ezdxf.tools.rgb import int2rgb, rgb2int
from ezdxf.tools import float2transparency, transparency2float

if TYPE_CHECKING:
    from ezdxf.eztypes2 import Auditor, TagWriter, Vertex, Matrix44, BaseLayout, DXFNamespace

__all__ = ['DXFGraphic', 'acdb_entity']

acdb_entity = DefSubclass('AcDbEntity', {
    'layer': DXFAttr(8, default='0'),  # layername as string
    'linetype': DXFAttr(6, default='BYLAYER', optional=True),  # linetype as string, special names BYLAYER/BYBLOCK
    'color': DXFAttr(62, default=256, optional=True),  # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER
    'paperspace': DXFAttr(67, default=0, optional=True),  # 0 .. modelspace, 1 .. paperspace
    # thickness and extrusion is defined in Entity specific subclasses
    # Stored and moved around as a 16-bit integer
    'lineweight': DXFAttr(370, default=-1, dxfversion=DXF2000, optional=True),
    # Line weight in mm times 100 (e.g. 0.13mm = 13). Smallest line weight is 13 and biggest line weight is 200, values
    # outside this range prevents AutoCAD from loading the file.
    # Special values:
    # LINEWEIGHT_BYLAYER = -1
    # LINEWEIGHT_BYBLOCK = -2
    # LINEWEIGHT_DEFAULT = -3
    #
    'ltscale': DXFAttr(48, default=1.0, dxfversion=DXF2000, optional=True),  # linetype scale
    'invisible': DXFAttr(60, default=0, dxfversion=DXF2000, optional=True),  # invisible .. 1, visible .. 0
    'true_color': DXFAttr(420, dxfversion=DXF2004, optional=True),  # true color as 0x00RRGGBB 24-bit value
    'color_name': DXFAttr(430, dxfversion=DXF2004, optional=True),  # color name as string
    'transparency': DXFAttr(440, dxfversion=DXF2004, optional=True),
    # transparency value 0x020000TT 0 = fully transparent / 255 = opaque
    'shadow_mode': DXFAttr(284, dxfversion=DXF2007, optional=True),  # shadow_mode
    # 0 = Casts and receives shadows
    # 1 = Casts shadows
    # 2 = Receives shadows
    # 3 = Ignores shadows
    'material_handle': DXFAttr(347, dxfversion=DXF2007, optional=True),  # shadow_mode
    'plotstyle_handle': DXFAttr(390, dxfversion=DXF2007, optional=True),  # shadow_mode
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

        self.dxf.export_dxf_attribs(tagwriter, [
            'layer', 'linetype', 'material_handle', 'color', 'paperspace', 'lineweight', 'ltscale', 'true_color',
            'color_name', 'transparency', 'plotstyle_handle', 'shadow_mode',
        ])

    def get_layout(self) -> Optional['BaseLayout']:
        if self.dxf.owner is None:  # unlinked entity
            return None
        try:
            return self.doc.layouts.get_layout_by_key(self.dxf.owner)
        except DXFKeyError:
            pass
        try:
            return self.doc.blocks.get_block_layout_by_handle(self.dxf.owner)
        except DXFTableEntryError:
            return None

    def move_to_layout(self, layout: 'BaseLayout', source: 'BaseLayout' = None) -> None:
        """
        Move entity from model space or a paper space layout to another layout. For block layout as source, the
        block layout has to be specified.

        Args:
            layout: any layout (model space, paper space, block)
            source: provide source layout, faster for DXF R12, if entity is in a block layout

        """
        if source is None:
            source = self.get_layout()
            if source is None:
                raise DXFValueError('Source layout for entity not found.')
        source.move_to_layout(self, layout)

    def copy_to_layout(self, layout: 'BaseLayout') -> 'DXFEntity':
        """
        Copy entity to another layout.

        Args:
            layout: any layout (model space, paper space, block)

        Returns: new created entity as DXFEntity() object

        """
        raise NotImplementedError()
        new_entity = self.clone()
        new_entity.dxf.handle = None
        self.entitydb.add(new_entity)
        layout.add_entity(new_entity)
        return new_entity

    # ------------------------------------------------------------------------------------------
    # A simple CAD like interface - but don't expect too much
    # ------------------------------------------------------------------------------------------

    def translate(self, direction: 'Vertex', ignore: bool = False) -> None:
        """
        Translate entity in `direction` if supported, else raises :class:`DXFUnsupportedFeature` except `ignore` is
        True.

        Args:
            direction: translation direction as :class:`Vector` or (x, y, z) tuple
            ignore: don't raise exception if not supported

        """
        direction = Vector(direction)
        if not ignore:
            raise DXFUnsupportedFeature(self.DXFTYPE)

    def scale(self, factor: float, ignore: bool = False) -> None:
        """
        Scale entity uniform by `factor` in x-, y- and z-direction if supported, else raises
        :class:`DXFUnsupportedFeature` except `ignore` is True.

        Args:
            factor: scaling factor for uniform scaling
            ignore: don't raise exception if not supported

        """
        factor = float(factor)
        if not ignore:
            raise DXFUnsupportedFeature(self.DXFTYPE)

    def scale_xyz(self, sx: float = 1, sy: float = 1, sz: float = 1, ignore: bool = False) -> None:
        """
        Scale entity none uniform in x-, y- and z-direction if supported, else raises
        :class:`DXFUnsupportedFeature` except `ignore` is True.

        Hint: scaling by -1 is mirroring

        Args:
            sx: x-axis scaling factor
            sy: y-axis scaling factor
            sz: z-axis scaling factor
            ignore: don't raise exception if not supported

        """
        sx = float(sx)
        sy = float(sy)
        sz = float(sz)
        if not ignore:
            raise DXFUnsupportedFeature(self.DXFTYPE)

    def rotate(self, angle: float, ucs: UCS = None, ignore: bool = False) -> None:
        """
        Rotate entity about the z-axis of `ucs` if supported, else raises :class:`DXFUnsupportedFeature` except
        `ignore` is True. If ucs is None, WCS is used.

        Args:
            angle: rotation angle in degrees (all angles in DXF are degrees)
            ucs: z-axis of ucs is the rotation axis
            ignore: don't raise exception if not supported

        """
        angle = float(angle)
        ucs = ucs or UCS()  # ucs or WCS
        if not ignore:
            raise DXFUnsupportedFeature(self.DXFTYPE)

    def transform(self, matrix: 'Matrix44', ignore: bool = False) -> None:
        """
        Applies a rigid motion transformation to an object if supported, else raises :class:`DXFUnsupportedFeature`
        except `ignore` is True.

        Args:
            matrix: 4 by 4 transformation matrix
            ignore: don't raise exception if not supported

        """
        if not ignore:
            raise DXFUnsupportedFeature(self.DXFTYPE)

    def to_wsc(self, ucs: UCS, ignore: bool = False) -> None:
        """
        Transform entity coordinates into WCS. All coordinates of the entity are treated as ucs coordinates and
        transformed into the WCS. For 2D entities the required OCS transformation is done automatically.

        Args:
            ucs: user coordinate system
            ignore: don't raise exception if not supported

        """
        if not ignore:
            raise DXFUnsupportedFeature(self.DXFTYPE)

    def audit(self, auditor: 'Auditor') -> None:
        super().audit(auditor)
        auditor.check_for_valid_layer_name(self)
        auditor.check_if_linetype_exists(self)
        auditor.check_for_valid_color_index(self)
        auditor.check_pointer_target_exists(self, zero_pointer_valid=False)

# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Iterable

from ezdxf.math import Vector, UCS, OCS
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['Circle']

acdb_circle = DefSubclass('AcDbCircle', {
    'center': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),
    'radius': DXFAttr(40, default=1),
    'thickness': DXFAttr(39, default=0, optional=True),
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=(0, 0, 1), optional=True),
})


@register_entity
class Circle(DXFGraphic):
    """ DXF CIRCLE entity """
    DXFTYPE = 'CIRCLE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_circle)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_circle)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_circle.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_circle.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, ['center', 'radius', 'thickness', 'extrusion'])

    def vertices(self, angles: Iterable[float]) -> Iterable[Vector]:
        """
        Yields vertices of the circle for iterable `angles` in WCS. This method takes into account a local OCS.

        Args:
            angles: iterable of angles in OCS as degrees, angle goes counter clockwise around the extrusion vector,
                    ocs x-axis = 0 deg.

        .. versionadded:: 0.11

        """
        ocs = self.ocs()
        for angle in angles:
            v = Vector.from_deg_angle(angle, self.dxf.radius) + self.dxf.center
            # convert from OCS to WCS
            yield ocs.to_wcs(v)

    def transform_to_wcs(self, ucs: 'UCS') -> None:
        """ Transform CIRCLE from local :class:`ezdxf.math.UCS` coordinates to :ref:`WCS` coordinates.

        Work with local UCS coordinates and transform them later into WCS coordinates.

        .. versionadded:: 0.11

        """
        # Requirement: current coordinates are located in the given UCS
        if self.dxf.hasattr('extrusion'):
            # Transform center from existing OCS to WCS, in this situation the UCS is the WCS.
            center = self.ocs().to_wcs(self.dxf.center)
        else:
            center = self.dxf.center
        # Transform UCS coordinates to the real WCS
        wcs_center = ucs.to_wcs(center)
        if ucs.uz.isclose((0, 0, 1)):
            self.dxf.center = wcs_center
        else:
            self.dxf.center = OCS(ucs.uz).from_wcs(wcs_center)
            self.dxf.extrusion = ucs.uz


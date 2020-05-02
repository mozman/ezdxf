# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Iterable
import math

from ezdxf.math import Vector, UCS, Matrix44, OCS
from ezdxf.math.transformtools import transform_extrusion, transform_length, NonUniformScalingError
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

    def transform_to_wcs(self, ucs: 'UCS') -> 'Circle':
        """ Transform CIRCLE from local :class:`~ezdxf.math.UCS` coordinates to :ref:`WCS` coordinates.

        .. versionadded:: 0.11

        """
        self._ucs_and_ocs_transformation(ucs, vector_names=['center'])
        return self

    def transform(self, m: Matrix44) -> 'Circle':
        """ Transform CIRCLE entity by transformation matrix `m` inplace.

        Raises ``NonUniformScalingError()`` for non uniform scaling.

        .. versionadded:: 0.13

        """
        # OCS entity!
        extrusion, has_uniform_scaling_in_ocs_xy = transform_extrusion(self.dxf.extrusion, m)
        if has_uniform_scaling_in_ocs_xy:
            old_ocs = OCS(self.dxf.extrusion)
            new_ocs = OCS(extrusion)
            self.dxf.extrusion = extrusion
            center_in_wcs = m.transform(old_ocs.to_wcs(self.dxf.center))
            self.dxf.center = new_ocs.from_wcs(center_in_wcs)
            # old_ocs has a uniform scaled xy-plane, direction of radius-vector in
            # the xy-plane is not important, choose x-axis for no reason:
            self.dxf.radius = transform_length((self.dxf.radius, 0, 0), old_ocs, m)
            # thickness vector points in the z-direction of the old_ocs:
            self.dxf.thickness = transform_length((0, 0, self.dxf.thickness), old_ocs, m)
        else:
            raise NonUniformScalingError('CIRCLE does not support non uniform scaling.')
            # Parent function has to catch this Exception and convert this CIRCLE into an ELLIPSE
        return self

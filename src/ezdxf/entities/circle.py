# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Iterable

from ezdxf.math import Vector, Matrix44
from ezdxf.math.transformtools import OCSTransform, NonUniformScalingError
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity, add_entity, replace_entity
from .factory import register_entity
from ezdxf.audit import AuditError

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, Ellipse, Spline, Auditor

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
            yield ocs.to_wcs(v)

    def transform(self, m: Matrix44) -> 'Circle':
        """ Transform CIRCLE entity by transformation matrix `m` inplace.

        Raises ``NonUniformScalingError()`` for non uniform scaling.

        .. versionadded:: 0.13

        """
        ocs = OCSTransform(self.dxf.extrusion, m)
        dxf = self.dxf
        if ocs.scale_uniform:
            dxf.extrusion = ocs.new_extrusion
            dxf.center = ocs.transform_vertex(dxf.center)
            # old_ocs has a uniform scaled xy-plane, direction of radius-vector in
            # the xy-plane is not important, choose x-axis for no reason:
            dxf.radius = ocs.transform_length((dxf.radius, 0, 0))
            if dxf.hasattr('thickness'):
                # thickness vector points in the z-direction of the old_ocs, thickness can be negative
                dxf.thickness = ocs.transform_length((0, 0, dxf.thickness), reflection=dxf.thickness)
        else:
            raise NonUniformScalingError('CIRCLE/ARC does not support non uniform scaling')
            # Parent function has to catch this Exception and convert this CIRCLE/ARC into an ELLIPSE
        return self

    def translate(self, dx: float, dy: float, dz: float) -> 'Circle':
        """ Optimized CIRCLE/ARC translation about `dx` in x-axis, `dy` in y-axis and `dz` in z-axis,
        returns `self` (floating interface).

        .. versionadded:: 0.13

        """
        ocs = self.ocs()
        self.dxf.center = ocs.from_wcs(Vector(dx, dy, dz) + ocs.to_wcs(self.dxf.center))
        return self

    def to_ellipse(self, replace=True) -> 'Ellipse':
        """ Convert CIRCLE/ARC to an :class:`~ezdxf.entities.Ellipse` entity.

        Adds the new ELLIPSE entity to the entity database and to the
        same layout as the source entity.

        Args:
            replace: replace (delete) source entity by ELLIPSE entity if ``True``

        .. versionadded:: 0.13

        """
        from ezdxf.entities import Ellipse
        ellipse = Ellipse.from_arc(self)
        if replace:
            replace_entity(self, ellipse)
        else:
            add_entity(self, ellipse)
        return ellipse

    def to_spline(self, replace=True) -> 'Spline':
        """ Convert CIRCLE/ARC to a :class:`~ezdxf.entities.Spline` entity.

        Adds the new SPLINE entity to the entity database and to the
        same layout as the source entity.

        Args:
            replace: replace (delete) source entity by SPLINE entity if ``True``

        .. versionadded:: 0.13

        """
        from ezdxf.entities import Spline
        spline = Spline.from_arc(self)
        if replace:
            replace_entity(self, spline)
        else:
            add_entity(self, spline)
        return spline

    def audit(self, auditor: 'Auditor') -> None:
        """ Validity check. """
        super().audit(auditor)
        if self.dxf.hasattr('radius') and self.dxf.radius <= 0:
            auditor.fixed_error(
                code=AuditError.INVALID_RADIUS,
                message=f'Deleted entity {str(self)} with invalid radius = {self.dxf.radius}.',
                dxf_entity=self,
            )
            if self.doc and self.doc.entitydb:
                self.entitydb.delete_entity(self)
            else:
                self.destroy()

# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Iterable
import math
from ezdxf.math import Vector, UCS, Matrix44, OCS, linspace, enclosing_angles, X_AXIS
from ezdxf.math.transformtools import OCSTransform

from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import acdb_entity
from .circle import acdb_circle, Circle
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, Vector, UCS

__all__ = ['Arc']

acdb_arc = DefSubclass('AcDbArc', {
    'start_angle': DXFAttr(50, default=0),
    'end_angle': DXFAttr(51, default=360),
})


@register_entity
class Arc(Circle):
    """ DXF ARC entity """
    DXFTYPE = 'ARC'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_circle, acdb_arc)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_arc)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_arc.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        # AcDbCircle export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_arc.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, ['start_angle', 'end_angle'])

    @property
    def start_point(self) -> 'Vector':
        """  Returns the start point of the arc in WCS, takes OCS into account.

        .. versionadded:: 0.11

        """
        v = list(self.vertices([self.dxf.start_angle]))
        return v[0]

    @property
    def end_point(self) -> 'Vector':
        """ Returns the end point of the arc in WCS, takes OCS into account.

        .. versionadded:: 0.11

        """
        v = list(self.vertices([self.dxf.end_angle]))
        return v[0]

    def angles(self, num: int) -> Iterable[float]:
        """ Returns `num` angles from start- to end angle in degrees in counter clockwise order.

        All angles are normalized in the range from [0, 360).

        """
        if num < 2:
            raise ValueError('num >= 2')
        start = self.dxf.start_angle % 360
        stop = self.dxf.end_angle % 360
        if stop <= start:
            stop += 360
        for angle in linspace(start, stop, num=num, endpoint=True):
            yield angle % 360

    def transform_to_wcs(self, ucs: 'UCS') -> 'Arc':
        """ Transform ARC entity from local :class:`~ezdxf.math.UCS` coordinates to :ref:`WCS` coordinates.

        .. versionadded:: 0.11

        """
        self._ucs_and_ocs_transformation(ucs, vector_names=['center'], angle_names=['start_angle', 'end_angle'])
        return self

    def transform(self, m: Matrix44) -> 'Arc':
        """ Transform ARC entity by transformation matrix `m` inplace.

        Raises ``NonUniformScalingError()`` for non uniform scaling.

        .. versionadded:: 0.13

        """
        ocs = OCSTransform(self.dxf.extrusion, m)
        start_angle, mid_angle, end_angle = self.angles(3)
        super().transform(m)

        new_start_angle = ocs.transform_deg_angle(start_angle)
        new_mid_angle = ocs.transform_deg_angle(mid_angle)
        new_end_angle = ocs.transform_deg_angle(end_angle)

        # if drawing the wrong side of the arc
        if enclosing_angles(new_mid_angle, new_start_angle, new_end_angle) != \
                enclosing_angles(mid_angle, start_angle, end_angle):
            new_start_angle, new_end_angle = new_end_angle, new_start_angle
        self.dxf.start_angle = new_start_angle
        self.dxf.end_angle = new_end_angle
        return self

    def transform_2(self, m: Matrix44) -> 'Arc':
        # alternative implementation, but both do not pass test 242/07
        """ Transform ARC entity by transformation matrix `m` inplace.

        Raises ``NonUniformScalingError()`` for non uniform scaling.

        .. versionadded:: 0.13

        """
        # in WCS
        vertices = list(m.transform_vertices(self.vertices((self.dxf.start_angle, self.dxf.end_angle))))
        super().transform(m)

        new_ocs = OCS(self.dxf.extrusion)
        start_point, end_point = new_ocs.points_from_wcs(vertices)
        center = self.dxf.center
        new_start_angle = self.dxf.extrusion.angle_about(X_AXIS, start_point - center)
        new_end_angle = self.dxf.extrusion.angle_about(X_AXIS, end_point - center)
        self.dxf.start_angle = math.degrees(new_start_angle)
        self.dxf.end_angle = math.degrees(new_end_angle)
        return self

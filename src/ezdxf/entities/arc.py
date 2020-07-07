# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Iterable
from ezdxf.math import Vector, Matrix44, linspace, ConstructionArc
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

    def transform(self, m: Matrix44) -> 'Arc':
        """ Transform ARC entity by transformation matrix `m` inplace.

        Raises ``NonUniformScalingError()`` for non uniform scaling.

        .. versionadded:: 0.13

        """
        ocs = OCSTransform(self.dxf.extrusion, m)
        super().transform(m)
        self.dxf.start_angle = ocs.transform_deg_angle(self.dxf.start_angle)
        self.dxf.end_angle = ocs.transform_deg_angle(self.dxf.end_angle)
        return self

    def construction_tool(self) -> ConstructionArc:
        """
        Returns 2D construction tool :class:`ezdxf.math.ConstructionArc`, ignoring the
        extrusion vector.

        .. versionadded:: 0.14

        """
        dxf = self.dxf
        return ConstructionArc(
            dxf.center,
            dxf.radius,
            dxf.start_angle,
            dxf.end_angle,
        )

    def apply_construction_tool(self, arc: ConstructionArc) -> 'Arc':
        """
        Set ARC data from construction tool :class:`ezdxf.math.ConstructionArc`,
        will not change the extrusion vector.

        .. versionadded:: 0.14

        """
        dxf = self.dxf
        dxf.center = Vector(arc.center)
        dxf.radius = arc.radius
        dxf.start_angle = arc.start_angle
        dxf.end_angle = arc.end_angle
        return self  # floating interface

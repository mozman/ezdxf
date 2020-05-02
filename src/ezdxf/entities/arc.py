# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Iterable
import math
from ezdxf.math import Vector, UCS, Matrix44, OCS, normalize_angle
from ezdxf.math.transformtools import transform_angle

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

    def angles(self, count: int) -> Iterable[float]:
        """ Returns `count` angles from start- to end angle in degrees in counter clockwise order.

        All angles are normalized in the range from [0, 360).

        """
        if count < 2:
            raise ValueError('Count >= 2')
        start = self.dxf.start_angle % 360
        end = self.dxf.end_angle % 360
        if end <= start:
            end += 360
        delta = (end - start) / (count - 1)
        for _ in range(count):
            yield start
            start = (start + delta) % 360

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
        old_ocs = OCS(self.dxf.extrusion)
        super().transform(m)
        # todo: transformations can change the arc orientation
        self.dxf.start_angle = math.degrees(
            transform_angle(math.radians(self.dxf.start_angle), old_ocs, self.dxf.extrusion, m))
        self.dxf.end_angle = math.degrees(
            transform_angle(math.radians(self.dxf.end_angle), old_ocs, self.dxf.extrusion, m))
        return self

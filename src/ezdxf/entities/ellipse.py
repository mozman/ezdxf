# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Iterable
import math
from ezdxf.math import Vector, linspace, Matrix44, rytz_axis_construction, angle_to_param
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, UCS

__all__ = ['Ellipse']

acdb_ellipse = DefSubclass('AcDbEllipse', {
    'center': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),
    'major_axis': DXFAttr(11, xtype=XType.point3d, default=Vector(1, 0, 0)),  # relative to the center
    # extrusion does not establish an OCS, it is just the normal vector of the ellipse plane.
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=(0, 0, 1), optional=True),
    'ratio': DXFAttr(40, default=1),  # has to be in range 1e-6 to 1
    'start_param': DXFAttr(41, default=0),  # this value is 0.0 for a full ellipse
    'end_param': DXFAttr(42, default=math.tau),  # this value is 2*pi for a full ellipse
})

HALF_PI = math.pi / 2.0


@register_entity
class Ellipse(DXFGraphic):
    """ DXF ELLIPSE entity """
    DXFTYPE = 'ELLIPSE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_ellipse)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_ellipse)
            if len(tags):
                processor.log_unprocessed_tags(tags, subclass=acdb_ellipse.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_ellipse.name)

        # AutoCAD does not accept a ratio < 1e-6 -> invalid DXF file
        self.dxf.ratio = max(self.dxf.ratio, 1e-6)
        self.dxf.export_dxf_attribs(tagwriter, [
            'center', 'major_axis', 'extrusion', 'ratio', 'start_param', 'end_param',
        ])

    def vertices(self, params: Iterable[float]) -> Iterable[Vector]:
        """
        Yields vertices on ellipse for iterable `params` in WCS.

        Args:
            params: param values in the range from ``0`` to ``2*pi`` in radians, param goes counter clockwise around the
                    extrusion vector, major_axis = local x-axis = 0 rad.

        .. versionadded:: 0.11

        """
        dxf = self.dxf
        major_axis = Vector(dxf.major_axis)  # local x-axis
        extrusion = Vector(dxf.extrusion)  # local z-axis
        minor_axis = extrusion.cross(major_axis)  # local y-axis

        x_unit_vector = major_axis.normalize()
        y_unit_vector = minor_axis.normalize()

        radius_x = major_axis.magnitude
        radius_y = radius_x * dxf.ratio
        center = Vector(dxf.center)
        for param in params:
            # Ellipse params in radians by definition (DXF Reference)
            x = math.cos(param) * radius_x * x_unit_vector
            y = math.sin(param) * radius_y * y_unit_vector

            # Construct WCS coordinates, ELLIPSE is not an OCS entity!
            yield center + x + y

    @property
    def minor_axis(self) -> Vector:
        dxf = self.dxf
        major_axis = Vector(dxf.major_axis)  # local x-axis
        extrusion = Vector(dxf.extrusion)  # local z-axis, normal vector of the ellipse plane
        minor_axis_length = major_axis.magnitude * dxf.ratio
        return extrusion.cross(major_axis).normalize(minor_axis_length)

    @property
    def start_point(self) -> 'Vector':
        v = list(self.vertices([self.dxf.start_param]))
        return v[0]

    @property
    def end_point(self) -> 'Vector':
        v = list(self.vertices([self.dxf.end_param]))
        return v[0]

    def swap_axis(self):
        """ Swap axis and adjust start- and end parameter. """
        self.dxf.major_axis = self.minor_axis
        ratio = 1.0 / self.dxf.ratio
        # AutoCAD does not accept a ratio < 1e-6 -> invalid DXF file
        self.dxf.ratio = max(ratio, 1e-6)

        start_param = self.dxf.start_param
        end_param = self.dxf.end_param
        if math.isclose(start_param, 0) and math.isclose(end_param, math.tau):
            return
        self.dxf.start_param = (start_param - HALF_PI) % math.tau
        self.dxf.end_param = (end_param - HALF_PI) % math.tau

    def params(self, num: int) -> Iterable[float]:
        """ Returns `num` params from start- to end param in counter clockwise order.

        All params are normalized in the range from [0, 2pi).

        """
        if num < 2:
            raise ValueError('num >= 2')
        start = self.dxf.start_param % math.tau
        end = self.dxf.end_param % math.tau
        if end <= start:
            end += math.tau

        for param in linspace(start, end, num):
            yield param % math.tau

    def transform_to_wcs(self, ucs: 'UCS') -> 'Ellipse':
        """ Transform ELLIPSE entity from local :class:`~ezdxf.math.UCS` coordinates to
        :ref:`WCS` coordinates.

        .. versionadded:: 0.11

        """
        # Ellipse is an real 3d entity without OCS
        self.dxf.center = ucs.to_wcs(self.dxf.center)
        self.dxf.major_axis = ucs.direction_to_wcs(self.dxf.major_axis)
        self.dxf.extrusion = ucs.direction_to_wcs(self.dxf.extrusion)
        return self

    @classmethod
    def from_arc(cls, entity: 'DXFGraphic') -> 'Ellipse':
        """ Create new ELLIPSE entity from ARC or CIRCLE entity. New entity has no owner
        and no handle and is not stored in the entity database!

        (internal API)
        """
        assert entity.dxftype() in {'ARC', 'CIRCLE'}
        attribs = entity.dxfattribs(drop={'owner', 'handle', 'thickness'})
        attribs['ratio'] = 1.0

        attribs['start_param'] = math.radians(attribs.pop('start_angle', 0.))
        attribs['end_param'] = math.radians(attribs.pop('end_angle', 360))

        ocs = entity.ocs()
        attribs['center'] = ocs.to_wcs(attribs.pop('center'))
        attribs['major_axis'] = ocs.to_wcs((attribs.pop('radius'), 0, 0))
        return Ellipse.new(dxfattribs=attribs, doc=entity.doc)

    def transform(self, m: Matrix44) -> 'Ellipse':
        """ Transform ELLIPSE entity by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        dxf = self.dxf
        center = m.transform(dxf.center)
        start_param = dxf.start_param % math.tau
        end_param = dxf.end_param % math.tau
        major_axis, minor_axis = m.transform_directions((dxf.major_axis, self.minor_axis))

        # Original ellipse parameters stay untouched until end of transformation
        if not math.isclose(major_axis.dot(minor_axis), 0, abs_tol=1e-9):
            major_axis, minor_axis, ratio = rytz_axis_construction(major_axis, minor_axis)
            adjust_params = True
        else:
            ratio = minor_axis.magnitude / major_axis.magnitude
            adjust_params = False

        if adjust_params and not math.isclose(start_param, end_param, abs_tol=1e-9):
            # open ellipse, adjusting start- and end parameter
            x_axis = major_axis.normalize()
            y_axis = minor_axis.normalize()
            old_param_span = (end_param - start_param) % math.tau

            def param(vec: 'Vector') -> float:
                dy = y_axis.dot(vec) / ratio  # adjust to circle
                dx = x_axis.dot(vec)
                return math.atan2(dy, dx) % math.tau

            # transformed start- and end point of old ellipse
            start_point, end_point = m.transform_vertices(self.vertices((start_param, end_param)))
            start_param = param(start_point - center)
            end_param = param(end_point - center)

            # if drawing the wrong side of the ellipse
            if math.isclose(old_param_span, math.pi, abs_tol=1e-9):
                # todo: equal param span check works well, except for a span of exact pi (180 deg)!
                # check for same relation of start- to end param does not work
                # if (start_param > end_param) != old_param_relation:
                #     start_param, end_param = end_param, start_param
                pass
            else:
                new_param_span = (end_param - start_param) % math.tau
                equal_param_span = math.isclose(old_param_span, new_param_span, abs_tol=1e-9)
                if not equal_param_span:
                    start_param, end_param = end_param, start_param

        dxf.center = center
        dxf.extrusion = major_axis.cross(minor_axis).normalize()
        dxf.major_axis = major_axis
        # AutoCAD does not accept a ratio < 1e-6 -> invalid DXF file
        dxf.ratio = max(ratio, 1e-6)
        dxf.start_param = start_param
        dxf.end_param = end_param
        if dxf.ratio > 1:
            self.swap_axis()
        return self

    def translate(self, dx: float, dy: float, dz: float) -> 'Ellipse':
        """ Optimized ELLIPSE translation about `dx` in x-axis, `dy` in y-axis and `dz` in z-axis,
        returns `self` (floating interface).

        .. versionadded:: 0.13

        """
        self.dxf.center = Vector(dx, dy, dz) + self.dxf.center
        return self

# Created: 28.12.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import math
from ezdxf.algebra import Vector, Ray2D
from ezdxf.algebra import UCS, PassTroughUCS
from ezdxf.lldxf.const import DXFValueError

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType, DimStyle, Dimension


class DimensionBase:
    def __init__(self, dimension: 'Dimension', dimstyle: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS' = None):
        self.drawing = dimension.drawing
        self.layout = layout
        self.dimstyle = dimstyle
        self.dimension = dimension
        self.ucs = ucs or PassTroughUCS()
        self.requires_extrusion = self.ucs.uz != (0, 0, 1)
        if self.requires_extrusion:  # set extrusion vector of DIMENSION entity
            self.dimension.dxf.extrusion = self.ucs.uz

    def default_attributes(self):
        return {
            'layer': self.dimension.dxf.layer,
            'color': self.dimension.dxf.color,
        }

    def wcs(self, point: Vector) -> Vector:
        return self.ucs.to_wcs(point)

    def ocs(self, point: Vector) -> Vector:
        return self.ucs.to_ocs(point)

    def get_text(self, measurement: float) -> str:
        dim = self.dimension.dxf
        if dim.text in ('', '<>'):
            text = str(measurement)
        else:
            text = dim.text
        return text

    def add_line(self, start: Vector, end: Vector) -> None:
        dxfattributes = self.default_attributes()
        self.layout.add_line(self.wcs(start), self.wcs(end), dxfattribs=dxfattributes)

    def add_blockref(self, name: str, insert: Vector, rotation: float = 0,
                     scale: Tuple[float, float] = (1., 1.)) -> None:
        attribs = self.default_attributes()
        attribs['rotation'] = rotation
        sx, sy = scale
        if sx != 1.:
            attribs['xscale'] = sx
        if sy != 1.:
            attribs['yscale'] = sy
        if self.requires_extrusion:
            attribs['extrusion'] = self.ucs.uz

        self.layout.add_blockref(name, insert=self.ocs(insert), dxfattribs=attribs)

    def add_text(self, text, pos, rotation):
        attribs = self.default_attributes()
        attribs['rotation'] = rotation
        dxftext = self.layout.add_text(text, dxfattribs=attribs)
        dxftext.set_pos(self.ocs(pos), align='MIDDLE_CENTER')

    def add_defpoints(self, points):
        attribs = {
            'layer': 'DEFPOINTS',
        }
        for point in points:
            self.layout.add_point(self.wcs(point), dxfattribs=attribs)


class LinearDimension(DimensionBase):
    def render(self):
        dim = self.dimension.dxf
        angle = math.radians(dim.angle)
        ext_angle = angle + math.pi / 2.

        dimline_ray = Ray2D(dim.defpoint, angle=angle)
        ext1_ray = Ray2D(dim.defpoint2, angle=ext_angle)
        ext2_ray = Ray2D(dim.defpoint3, angle=ext_angle)
        dimline_start = dimline_ray.intersect(ext1_ray)
        dimline_end = dimline_ray.intersect(ext2_ray)
        measurement = (dimline_start - dimline_end).magnitude

        dim_text = self.get_text(measurement)

        self.add_line(dimline_start, dimline_end)
        self.add_line(dim.defpoint2, dimline_start)
        self.add_line(dim.defpoint3, dimline_end)
        self.add_blockref('M', insert=dimline_start, rotation=dim.angle)
        self.add_blockref('M', insert=dimline_end, rotation=dim.angle)

        if dim_text != ' ':  # one space suppresses the dimension text
            insert = self.dimension.get_dxf_attrib('text_midpoint')
            if insert is None:
                insert = self.get_text_midpoint(dimline_start, dimline_end)
            text_rotation = self.dimension.get_dxf_attrib('text_rotation', 0)
            self.add_text(dim.text, insert, dim.angle + text_rotation)

        self.add_defpoints([dim.defpoint, dim.defpoint2, dim.defpoint3])

    def get_text_midpoint(self, start: Vector, end: Vector) -> Vector:
        return start.lerp(end)  # center point - temporarily


class DimensionRenderer:
    def dispatch(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS'):
        dim_type = dimension.dim_type
        if dim_type in (0, 1):
            self.linear(dimension, dim_style, layout, ucs)
        elif dim_type == 2:
            self.angular(dimension, dim_style, layout, ucs)
        elif dim_type == 3:
            self.diameter(dimension, dim_style, layout, ucs)
        elif dim_type == 4:
            self.radius(dimension, dim_style, layout, ucs)
        elif dim_type == 5:
            self.angular3p(dimension, dim_style, layout, ucs)
        elif dim_type == 6:
            self.ordinate(dimension, dim_style, layout, ucs)
        else:
            raise DXFValueError("Unknown DIMENSION type: {}".format(dim_type))

    def linear(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS'):
        """
        Call renderer for linear dimension lines: horizontal, vertical and rotated
        """
        render = LinearDimension(dimension, dim_style, layout, ucs)
        render.render()

    def angular(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS'):
        raise NotImplemented

    def diameter(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS'):
        raise NotImplemented

    def radius(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS'):
        raise NotImplemented

    def angular3p(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS'):
        raise NotImplemented

    def ordinate(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS'):
        raise NotImplemented

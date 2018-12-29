# Created: 28.12.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple, Iterable
import math
from ezdxf.algebra import Vector, Ray2D
from ezdxf.algebra import UCS, PassTroughUCS
from ezdxf.lldxf.const import DXFValueError, DXFUndefinedBlockError

if TYPE_CHECKING:
    from ezdxf.eztypes import DimStyle, Dimension, BlockLayout, Vertex


class DimensionBase:
    def __init__(self, dimension: 'Dimension', dim_style: 'DimStyle', block: 'BlockLayout', ucs: 'UCS' = None,
                 text_style: str = None):
        self.drawing = dimension.drawing
        self.dxfversion = self.drawing.dxfversion
        self.block = block
        self.dim_style = dim_style
        self.text_style = self.get_text_style(text_style)
        self.dimension = dimension
        self.ucs = ucs or PassTroughUCS()
        self.requires_extrusion = self.ucs.uz != (0, 0, 1)
        if self.requires_extrusion:  # set extrusion vector of DIMENSION entity
            self.dimension.dxf.extrusion = self.ucs.uz

    @property
    def text_height(self) -> float:
        return self.dim_style.get_dxf_attrib('dimtxt', 1.0)

    @property
    def suppress_extension_line1(self) -> bool:
        return bool(self.dim_style.get_dxf_attrib('dimse1', False))

    @property
    def suppress_extension_line2(self) -> bool:
        return bool(self.dim_style.get_dxf_attrib('dimse2', False))

    def default_attributes(self) -> dict:
        return {
            'layer': self.dimension.dxf.layer,
            'color': self.dimension.dxf.color,
        }

    def wcs(self, point: 'Vertex') -> Vector:
        return self.ucs.to_wcs(point)

    def ocs(self, point: 'Vertex') -> Vector:
        return self.ucs.to_ocs(point)

    def get_text(self, measurement: float) -> str:
        text = self.dimension.dxf.text
        text_fmt = self.get_text_format()
        if text == ' ':  # suppress text
            return ''
        elif text == '' or text == '<>':  # measured distance
            return text_fmt.format(measurement)
        else:  # user override
            return text

    def get_text_style(self, text_style: str = None) -> str:
        if self.dxfversion <= 'AC1009':
            return text_style or 'STANDARD'
        else:
            handle = self.dim_style.get_dxf_attrib('dimtxsty_handle', None)
            if handle:
                style = self.drawing.get_dxf_entity(handle)
                return style.dxf.name
            else:
                return text_style or 'STANDARD'

    def get_text_format(self) -> str:
        return "{:.0f}"

    def add_line(self, start: 'Vertex', end: 'Vertex') -> None:
        dxfattributes = self.default_attributes()
        self.block.add_line(self.wcs(start), self.wcs(end), dxfattribs=dxfattributes)

    def add_blockref(self, name: str, insert: 'Vertex', rotation: float = 0,
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

        self.block.add_blockref(name, insert=self.ocs(insert), dxfattribs=attribs)

    def add_text(self, text: str, pos: 'Vertex', rotation: float) -> None:
        attribs = self.default_attributes()
        attribs['rotation'] = rotation
        attribs['style'] = self.text_style
        attribs['height'] = self.text_height
        dxftext = self.block.add_text(text, dxfattribs=attribs)
        dxftext.set_pos(self.ocs(pos), align='MIDDLE_CENTER')

    def add_defpoints(self, points: Iterable['Vertex']) -> None:
        attribs = {
            'layer': 'DEFPOINTS',
        }
        for point in points:
            self.block.add_point(self.wcs(point), dxfattribs=attribs)


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
        dim.defpoint = dimline_start  # set defpoint to expected location

        # add dimension line
        self.add_dimension_line(dimline_start, dimline_end)

        # add extension line 1
        if not self.suppress_extension_line1:
            self.add_extension_line(dim.defpoint2, dimline_start)

        # add extension line 1
        if not self.suppress_extension_line2:
            self.add_extension_line(dim.defpoint3, dimline_end)

        # add ticks
        self.add_ticks(dimline_start, dimline_end)

        # add text
        dimlfac = self.dim_style.get_dxf_attrib('dimlfac', 1.)
        measurement = (dimline_start - dimline_end).magnitude
        dim_text = self.get_text(measurement * dimlfac)
        if dim_text:
            pos = self.dimension.get_dxf_attrib('text_midpoint', None)
            if pos is None:
                pos = self.get_text_midpoint(dimline_start, dimline_end)
                self.dimension.set_dxf_attrib('text_midpoint', pos)
                self.add_measurement_text(dim_text, pos)

        # add POINT at definition points
        self.add_defpoints([dim.defpoint, dim.defpoint2, dim.defpoint3])

    def add_measurement_text(self, dim_text:str, pos: Vector) -> None:
        angle = self.dimension.get_dxf_attrib('angle', 0)
        text_rotation = self.dimension.get_dxf_attrib('text_rotation', 0)
        self.add_text(dim_text, pos=pos, rotation=angle + text_rotation)

    def add_dimension_line(self, start: 'Vertex', end: 'Vertex') -> None:
        # TODO: DXF attributes
        self.add_line(start, end)

    def add_extension_line(self, start: 'Vertex', end: 'Vertex') -> None:
        # TODO: DXF attributes and start and end adjustments
        self.add_line(start, end)

    def add_ticks(self, start: 'Vertex', end: 'Vertex') -> None:
        dim = self.dimension.dxf
        style = self.dim_style.dxf

        scale = (style.dimasz, style.dimasz)
        blk = style.dimblk
        blocks = self.drawing.blocks
        if blk in blocks:
            blk1 = blk
            blk2 = blk
        else:
            blk1 = style.dimblk1
            if blk1 not in blocks:
                raise DXFUndefinedBlockError('Undefined tick block 1: "{}"'.format(blk1))
            blk2 = style.dimblk2
            if blk2 not in blocks:
                raise DXFUndefinedBlockError('Undefined tick block 2: "{}"'.format(blk2))

        self.add_blockref(blk1, insert=start, rotation=dim.angle, scale=scale)
        self.add_blockref(blk2, insert=end, rotation=dim.angle, scale=scale)

    def get_text_midpoint(self, start: Vector, end: Vector) -> Vector:
        height = self.text_height
        gap = self.dim_style.get_dxf_attrib('dimgap', 0.625)
        dist = height / 2. + gap
        base = end - start
        ortho = base.orthogonal().normalize(dist)
        return start.lerp(end) + ortho


class DimensionRenderer:
    def dispatch(self, dimension: 'Dimension', ucs: 'UCS', text_style: str = None) -> None:
        dwg = dimension.drawing
        dim_style = dimension.dim_style()
        block = dwg.blocks.new_anonymous_block(type_char='D')
        dimension.dxf.geometry = block.name
        dim_type = dimension.dim_type

        if dim_type in (0, 1):
            self.linear(dimension, dim_style, block, ucs, text_style)
        elif dim_type == 2:
            self.angular(dimension, dim_style, block, ucs, text_style)
        elif dim_type == 3:
            self.diameter(dimension, dim_style, block, ucs, text_style)
        elif dim_type == 4:
            self.radius(dimension, dim_style, block, ucs, text_style)
        elif dim_type == 5:
            self.angular3p(dimension, dim_style, block, ucs, text_style)
        elif dim_type == 6:
            self.ordinate(dimension, dim_style, block, ucs, text_style)
        else:
            raise DXFValueError("Unknown DIMENSION type: {}".format(dim_type))

    def linear(self, dimension: 'Dimension', dim_style: 'DimStyle', block: 'BlockLayout', ucs: 'UCS',
               text_style: str = None):
        """
        Call renderer for linear dimension lines: horizontal, vertical and rotated
        """
        render = LinearDimension(dimension, dim_style, block, ucs, text_style)
        render.render()

    def angular(self, dimension: 'Dimension', dim_style: 'DimStyle', block: 'BlockLayout', ucs: 'UCS',
                text_style: str = None):
        raise NotImplemented

    def diameter(self, dimension: 'Dimension', dim_style: 'DimStyle', block: 'BlockLayout', ucs: 'UCS',
                 text_style: str = None):
        raise NotImplemented

    def radius(self, dimension: 'Dimension', dim_style: 'DimStyle', block: 'BlockLayout', ucs: 'UCS',
               text_style: str = None):
        raise NotImplemented

    def angular3p(self, dimension: 'Dimension', dim_style: 'DimStyle', block: 'BlockLayout', ucs: 'UCS',
                  text_style: str = None):
        raise NotImplemented

    def ordinate(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'BlockLayout', ucs: 'UCS',
                 text_style: str = None):
        raise NotImplemented

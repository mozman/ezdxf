# Created: 28.12.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import math
from ezdxf.algebra import Vector, Ray2D
from ezdxf.algebra import UCS, PassTroughUCS
from ezdxf.lldxf.const import DXFValueError, DXFUndefinedBlockError

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType, DimStyle, Dimension


class DimensionBase:
    def __init__(self, dimension: 'Dimension', dimstyle: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS' = None,
                 txtstyle: str = None):
        self.drawing = dimension.drawing
        self.dxfversion = self.drawing.dxfversion
        self.layout = layout
        self.dimstyle = dimstyle
        self.txtstyle = self.get_dim_text_style(txtstyle)
        self.dimension = dimension
        self.ucs = ucs or PassTroughUCS()
        self.requires_extrusion = self.ucs.uz != (0, 0, 1)
        if self.requires_extrusion:  # set extrusion vector of DIMENSION entity
            self.dimension.dxf.extrusion = self.ucs.uz

    @property
    def dim_text_height(self) -> float:
        return self.dimstyle.get_dxf_attrib('dimtxt', 1.0)

    @property
    def suppress_extension_line1(self):
        return bool(self.dimstyle.get_dxf_attrib('dimse1', False))

    @property
    def suppress_extension_line2(self):
        return bool(self.dimstyle.get_dxf_attrib('dimse2', False))

    def default_attributes(self):
        return {
            'layer': self.dimension.dxf.layer,
            'color': self.dimension.dxf.color,
        }

    def wcs(self, point: Vector) -> Vector:
        return self.ucs.to_wcs(point)

    def ocs(self, point: Vector) -> Vector:
        return self.ucs.to_ocs(point)

    def get_dim_text(self, measurement: float) -> str:
        text = self.dimension.dxf.text
        text_fmt = self.get_dim_text_format()
        if text == ' ':  # suppress text
            return ''
        elif text == '' or text == '<>':  # measured distance
            return text_fmt.format(measurement)
        else:  # user override
            return text

    def get_dim_text_style(self, txtstyle=None):
        if self.dxfversion <= 'AC1009':
            return txtstyle or 'STANDARD'
        else:
            handle = self.dimstyle.get_dxf_attrib('dimtxsty_handle', None)
            if handle:
                style = self.drawing.get_dxf_entity(handle)
                return style.dxf.name
            else:
                return txtstyle or 'STANDARD'

    def get_dim_text_format(self) -> str:
        return "{:.0f}"

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
        attribs['style'] = self.txtstyle
        attribs['height'] = self.dim_text_height
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
        dim.defpoint = dimline_start  # set defpoint to expected location

        # add dimension line
        self.add_line(dimline_start, dimline_end)
        if not self.suppress_extension_line1:
            self.add_extension_line(dim.defpoint2, dimline_start)
        if not self.suppress_extension_line2:
            self.add_extension_line(dim.defpoint3, dimline_end)

        self.insert_block_arrows(dimline_start, dimline_end)
        dimlfac = self.dimstyle.get_dxf_attrib('dimlfac', 1.)
        measurement = (dimline_start - dimline_end).magnitude
        dim_text = self.get_dim_text(measurement * dimlfac)
        if dim_text:
            insert = self.dimension.get_dxf_attrib('text_midpoint', None)
            if insert is None:
                insert = self.get_text_midpoint(dimline_start, dimline_end)
                self.dimension.set_dxf_attrib('text_midpoint', insert)
            text_rotation = self.dimension.get_dxf_attrib('text_rotation', 0)
            self.add_text(dim_text, insert, dim.angle + text_rotation)

        self.add_defpoints([dim.defpoint, dim.defpoint2, dim.defpoint3])

    def add_extension_line(self, start: Vector, end: Vector) -> None:
        self.add_line(start, end)

    def insert_block_arrows(self, start: Vector, end: Vector) -> None:
        dim = self.dimension.dxf
        style = self.dimstyle.dxf

        scale = (style.dimasz, style.dimasz)
        blk = style.dimblk
        blocks = self.drawing.blocks
        if blk in blocks:
            blk1 = blk
            blk2 = blk
        else:
            blk1 = style.dimblk1
            if blk1 not in blocks:
                raise DXFUndefinedBlockError('Undefined arrow block 1: {}'.format(blk1))
            blk2 = style.dimblk2
            if blk2 not in blocks:
                raise DXFUndefinedBlockError('Undefined arrow block 2: {}'.format(blk2))

        self.add_blockref(blk1, insert=start, rotation=dim.angle, scale=scale)
        self.add_blockref(blk2, insert=end, rotation=dim.angle, scale=scale)

    def get_text_midpoint(self, start: Vector, end: Vector) -> Vector:
        height = self.dim_text_height
        gap = self.dimstyle.get_dxf_attrib('dimgap', 0.625)
        dist = height / 2. + gap
        base = end - start
        ortho = base.orthogonal().normalize(dist)
        return start.lerp(end) + ortho


class DimensionRenderer:
    def dispatch(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS',
                 txtstyle: str = None) -> None:
        dim_type = dimension.dim_type
        if dim_type in (0, 1):
            self.linear(dimension, dim_style, layout, ucs, txtstyle)
        elif dim_type == 2:
            self.angular(dimension, dim_style, layout, ucs, txtstyle)
        elif dim_type == 3:
            self.diameter(dimension, dim_style, layout, ucs, txtstyle)
        elif dim_type == 4:
            self.radius(dimension, dim_style, layout, ucs, txtstyle)
        elif dim_type == 5:
            self.angular3p(dimension, dim_style, layout, ucs, txtstyle)
        elif dim_type == 6:
            self.ordinate(dimension, dim_style, layout, ucs, txtstyle)
        else:
            raise DXFValueError("Unknown DIMENSION type: {}".format(dim_type))

    def linear(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS',
               txtstyle: str = None):
        """
        Call renderer for linear dimension lines: horizontal, vertical and rotated
        """
        render = LinearDimension(dimension, dim_style, layout, ucs, txtstyle)
        render.render()

    def angular(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS',
                txtstyle: str = None):
        raise NotImplemented

    def diameter(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS',
                 txtstyle: str = None):
        raise NotImplemented

    def radius(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS',
               txtstyle: str = None):
        raise NotImplemented

    def angular3p(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS',
                  txtstyle: str = None):
        raise NotImplemented

    def ordinate(self, dimension: 'Dimension', dim_style: 'DimStyle', layout: 'GenericLayoutType', ucs: 'UCS',
                 txtstyle: str = None):
        raise NotImplemented

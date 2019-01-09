# Created: 28.12.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple, Iterable
import math
from ezdxf.algebra import Vector, ConstructionRay, xround
from ezdxf.algebra import UCS, PassTroughUCS
from ezdxf.lldxf.const import DXFValueError, DXFUndefinedBlockError, MTEXT_ALIGN_FLAGS
from ezdxf.options import options
from ezdxf.tools import suppress_zeros, raise_decimals
from ezdxf.render.arrows import ARROWS, connection_point
from ezdxf.modern.tableentries import get_block_name_by_handle

if TYPE_CHECKING:
    from ezdxf.eztypes import Dimension, BlockLayout, Vertex, DimStyleOverride


class DimensionBase:
    def __init__(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS' = None,
                 override: 'DimStyleOverride' = None):
        self.drawing = dimension.drawing
        self.dimension = dimension
        self.dxfversion = self.drawing.dxfversion
        self.block = block
        if override:
            self.dim_style = override
        else:
            self.dim_style = self.dimension.dimstyle_override()
        self.text_style = self.dim_style.get_text_style(default=options.default_dimension_text_style)
        self.ucs = ucs or PassTroughUCS()
        self.requires_extrusion = self.ucs.uz != (0, 0, 1)
        if self.requires_extrusion:  # set extrusion vector of DIMENSION entity
            self.dimension.dxf.extrusion = self.ucs.uz
        # write override values into dimension entity XDATA section
        self.dim_style.commit()

    @property
    def text_height(self) -> float:
        return self.dim_style.get('dimtxt', 1.0)

    @property
    def suppress_extension_line1(self) -> bool:
        return bool(self.dim_style.get('dimse1', False))

    @property
    def suppress_extension_line2(self) -> bool:
        return bool(self.dim_style.get('dimse2', False))

    @property
    def user_location_override(self) -> bool:
        return self.dimension.get_flag_state(self.dimension.USER_LOCATION_OVERRIDE, name='dimtype')

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
        if text == ' ':  # suppress text
            return ''
        elif text == '' or text == '<>':  # measured distance
            return self.format_text(measurement)
        else:  # user override
            return text

    def get_arrow_names(self) -> Tuple[str, str]:
        def arrow_name(attrib) -> str:
            if self.dxfversion > 'AC1009':
                handle = get_dxf_attr(attrib + '_handle', None)
                if handle == '0':  # special: closed filled
                    pass  # return default value
                elif handle:
                    block_name = get_block_name_by_handle(handle, self.drawing)
                    return ARROWS.arrow_name(block_name)
                return ARROWS.closed_filled
            else:  # DXF12 or no handle -> use block name
                return get_dxf_attr(attrib)

        get_dxf_attr = self.dim_style.get
        dimtsz = get_dxf_attr('dimtsz')
        blk1, blk2 = None, None
        if dimtsz == 0.:
            if bool(get_dxf_attr('dimsah')):
                blk1 = arrow_name('dimblk1')
                blk2 = arrow_name('dimblk2')
            else:
                blk = arrow_name('dimblk')
                blk1 = blk
                blk2 = blk
        return blk1, blk2

    def format_text(self, value: float) -> str:
        dimrnd = self.dim_style.get('dimrnd', None)
        dimdec = self.dim_style.get('dimdec', None)
        dimzin = self.dim_style.get('dimzin', 0)
        dimdsep = self.dim_style.get('dimdsep', '.')
        dimpost = self.dim_style.get('dimpost', '<>')
        return format_text(value, dimrnd, dimdec, dimzin, dimdsep, dimpost)

    def add_line(self, start: 'Vertex', end: 'Vertex', dxfattribs: dict = None) -> None:
        attribs = self.default_attributes()
        if dxfattribs:
            attribs.update(dxfattribs)
        self.block.add_line(self.wcs(start), self.wcs(end), dxfattribs=attribs)

    def add_blockref(self, name: str, insert: 'Vertex', rotation: float = 0,
                     scale: float = 1., reverse=False, dxfattribs: dict = None) -> Vector:
        if name in ARROWS:  # generates automatically BLOCK definitions for arrows if needed
            return self.block.add_arrow_blockref(name, insert=insert, size=scale, rotation=rotation, reverse=reverse,
                                                 dxfattribs=dxfattribs)
        else:
            if name not in self.drawing.blocks:
                raise DXFUndefinedBlockError('Undefined block: "{}"'.format(name))

            attribs = self.default_attributes()
            attribs['rotation'] = rotation
            if scale != 1.:
                attribs['xscale'] = scale
                attribs['yscale'] = scale
            if self.requires_extrusion:
                attribs['extrusion'] = self.ucs.uz
            if dxfattribs:
                attribs.update(dxfattribs)
            self.block.add_blockref(name, insert=self.ocs(insert), dxfattribs=attribs)
            return insert

    def add_text(self, text: str, pos: 'Vertex', rotation: float, align='MIDDLE_CENTER',
                 dxfattribs: dict = None) -> None:
        attribs = self.default_attributes()
        attribs['rotation'] = rotation
        attribs['style'] = self.text_style

        if self.dxfversion > 'AC1009':
            attribs['char_height'] = self.text_height
            attribs['insert'] = pos
            attribs['attachment_point'] = self.dimension.get_dxf_attrib('align', MTEXT_ALIGN_FLAGS.get(align, 5))
            if dxfattribs:
                attribs.update(dxfattribs)
            self.block.add_mtext(text, dxfattribs=attribs)
        else:
            attribs['height'] = self.text_height
            if dxfattribs:
                attribs.update(dxfattribs)
            dxftext = self.block.add_text(text, dxfattribs=attribs)
            dxftext.set_pos(self.ocs(pos), align=align)

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

        # USER_LOCATION_OVERRIDE, moves dimension line location!
        if self.user_location_override:
            dimline_ray = ConstructionRay(dim.text_midpoint, angle=angle)
        else:
            dimline_ray = ConstructionRay(dim.defpoint, angle=angle)

        # extension lines
        ext1_ray = ConstructionRay(dim.defpoint2, angle=ext_angle)
        ext2_ray = ConstructionRay(dim.defpoint3, angle=ext_angle)

        # dimension definition points
        dimline_start = dimline_ray.intersect(ext1_ray)
        dimline_end = dimline_ray.intersect(ext2_ray)
        dim.defpoint = dimline_start  # set defpoint to expected location

        dimlfac = self.dim_style.get('dimlfac', 1.)
        measurement = (dimline_start - dimline_end).magnitude
        dim_text = self.get_text(measurement * dimlfac)

        # add text
        if dim_text:
            text_location = self.text_location(dimline_start, dimline_end)
            self.add_measurement_text(dim_text, text_location)

        # add extension line 1
        if not self.suppress_extension_line1:
            self.add_extension_line(dim.defpoint2, dimline_start)

        # add extension line 1
        if not self.suppress_extension_line2:
            self.add_extension_line(dim.defpoint3, dimline_end)

        blk1, blk2 = self.get_arrow_names()
        # add arrows
        dimline_start, dimline_end = self.add_arrows(dimline_start, dimline_end, blk1, blk2)
        self.add_dimension_line(dimline_start, dimline_end, blk1, blk2)

        # add POINT at definition points
        self.add_defpoints([dim.defpoint, dim.defpoint2, dim.defpoint3])
        self.defpoints_to_wcs()

    def defpoints_to_wcs(self):
        def from_ucs(attr, func):
            point = self.dimension.get_dxf_attrib(attr)
            self.dimension.set_dxf_attrib(attr, func(point))

        from_ucs('defpoint', self.wcs)
        from_ucs('defpoint2', self.wcs)
        from_ucs('defpoint3', self.wcs)
        from_ucs('text_midpoint', self.ocs)

    def add_measurement_text(self, dim_text: str, pos: Vector) -> None:
        attribs = {
            'color': self.dim_style.get('dimclrt', self.dimension.dxf.color)
        }
        angle = self.dimension.get_dxf_attrib('angle', 0)
        text_rotation = self.dimension.get_dxf_attrib('text_rotation', 0)
        self.add_text(dim_text, pos=pos, rotation=angle + text_rotation, dxfattribs=attribs)

    def add_dimension_line(self, start: 'Vertex', end: 'Vertex', blk1: str = None, blk2: str = None) -> None:
        direction = (end - start).normalize()
        extension = direction * self.dim_style.get('dimdle', 0.)
        if blk1 is None or ARROWS.has_extension_line(blk1):
            start = start - extension
        if blk2 is None or ARROWS.has_extension_line(blk2):
            end = end + extension
        # is dimension line crossing text
        attribs = {
            'color': self.dim_style.get('dimclrd', self.dimension.dxf.color)
        }
        self.add_line(start, end, dxfattribs=attribs)

    def add_extension_line(self, start: 'Vertex', end: 'Vertex') -> None:
        direction = (end - start).normalize()
        offset = self.dim_style.get('dimexo', 0.)
        extension = self.dim_style.get('dimexe', 0.)
        start = start + direction * offset
        end = end + direction * extension
        attribs = {
            'color': self.dim_style.get('dimclre', self.dimension.dxf.color)
        }
        self.add_line(start, end, dxfattribs=attribs)

    def add_arrows(self, start: 'Vertex', end: 'Vertex', blk1: str = '', blk2: str = '') -> Tuple[Vector, Vector]:
        dim = self.dimension.dxf
        get_dxf_attr = self.dim_style.get
        attribs = {
            'color': get_dxf_attr('dimclrd', self.dimension.dxf.color),
        }
        dimtsz = get_dxf_attr('dimtsz')
        if dimtsz > 0.:  # oblique stroke, but double the size
            self.block.add_arrow(ARROWS.oblique, insert=start, rotation=dim.angle, size=dimtsz * 2, dxfattribs=attribs)
            self.block.add_arrow(ARROWS.oblique, insert=end, rotation=dim.angle, size=dimtsz * 2, dxfattribs=attribs)
        else:
            scale = get_dxf_attr('dimasz')
            start = self.add_blockref(blk1, insert=start, scale=scale, rotation=dim.angle, reverse=True,
                                      dxfattribs=attribs)
            end = self.add_blockref(blk2, insert=end, scale=scale, rotation=dim.angle, dxfattribs=attribs)
            # test connection point
            # if blk1 not in ARROWS.STROKE_ARROWS:
            #    start = connection_point(blk1, start, scale, dim.angle)
            # if blk2 not in ARROWS.STROKE_ARROWS:
            #    end = connection_point(blk2, end, scale, dim.angle+180)
        return start, end

    def text_vertical_distance(self) -> float:
        """
        Returns the vertical distcance for dimension line to text midpoint. Positive values are above the line, negative
        values are below the line.
        """
        tad = self.dim_style.get('dimtad', 1)
        height = self.text_height
        gap = self.dim_style.get('dimgap', 0.625)
        dist = height / 2. + gap  # above dimline
        if tad == 0:  # center of dimline
            dist = 0
        elif tad == 4:  # below dimline
            dist = -dist
        return dist

    def text_location(self, start: Vector, end: Vector) -> Vector:
        if not self.user_location_override:
            # text_location defines the text location along the dimension line
            # TODO: there are more the possible location than 'center'
            text_location = start.lerp(end)
            self.dimension.set_dxf_attrib('text_midpoint', text_location)
        else:
            # text_location defines the text location along the dimension line
            text_location = self.dimension.get_dxf_attrib('text_midpoint')

        # vertical distance from dimension line to text midpoint, normal to the dimension line
        dist = self.text_vertical_distance()
        # shift text location
        ortho = (end - start).orthogonal().normalize(dist)
        return text_location + ortho


class DimensionRenderer:
    def dispatch(self, dimension: 'Dimension', ucs: 'UCS', override: 'DimStyleOverride' = None) -> None:
        dwg = dimension.drawing
        block = dwg.blocks.new_anonymous_block(type_char='D')
        dimension.dxf.geometry = block.name
        dim_type = dimension.dim_type

        if dim_type in (0, 1):
            self.linear(dimension, block, ucs, override)
        elif dim_type == 2:
            self.angular(dimension, block, ucs, override)
        elif dim_type == 3:
            self.diameter(dimension, block, ucs, override)
        elif dim_type == 4:
            self.radius(dimension, block, ucs, override)
        elif dim_type == 5:
            self.angular3p(dimension, block, ucs, override)
        elif dim_type == 6:
            self.ordinate(dimension, block, ucs, override)
        else:
            raise DXFValueError("Unknown DIMENSION type: {}".format(dim_type))

    def linear(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS', override: 'DimStyleOverride' = None):
        """
        Call renderer for linear dimension lines: horizontal, vertical and rotated
        """
        render = LinearDimension(dimension, block, ucs, override)
        render.render()

    def angular(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS', override: 'DimStyleOverride' = None):
        raise NotImplemented

    def diameter(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS', override: 'DimStyleOverride' = None):
        raise NotImplemented

    def radius(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS', override: 'DimStyleOverride' = None):
        raise NotImplemented

    def angular3p(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS', override: 'DimStyleOverride' = None):
        raise NotImplemented

    def ordinate(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS', override: 'DimStyleOverride' = None):
        raise NotImplemented


def format_text(value: float, dimrnd: float = None, dimdec: int = None, dimzin: int = 0, dimdsep: str = '.',
                dimpost: str = '<>', raisedec=False) -> str:
    if dimrnd is not None:
        value = xround(value, dimrnd)

    if dimdec is None:
        fmt = "{:f}"
        dimzin = dimzin | 8  # remove pending zeros for undefined decimal places, '{:f}'.format(0) -> '0.000000'
    else:
        fmt = "{:." + str(dimdec) + "f}"
    text = fmt.format(value)

    leading = bool(dimzin & 4)
    pending = bool(dimzin & 8)
    text = suppress_zeros(text, leading, pending)
    if raisedec:
        text = raise_decimals(text)
    if dimdsep != '.':
        text = text.replace('.', dimdsep)
    if dimpost:
        if '<>' in dimpost:
            fmt = dimpost.replace('<>', '{}', 1)
            text = fmt.format(text)
        else:
            raise DXFValueError('Invalid dimpost string: "{}"'.format(dimpost))
    return text

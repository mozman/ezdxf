# Created: 28.12.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple, Iterable
import math
from ezdxf.algebra import Vector, ConstructionRay, xround
from ezdxf.algebra import UCS, PassTroughUCS
from ezdxf.lldxf import const
from ezdxf.options import options
from ezdxf.lldxf.const import DXFValueError, DXFUndefinedBlockError
from ezdxf.tools import suppress_zeros, raise_decimals
from ezdxf.render.arrows import ARROWS, connection_point

if TYPE_CHECKING:
    from ezdxf.eztypes import Dimension, BlockLayout, Vertex, DimStyleOverride, Style


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
        self.ucs = ucs or PassTroughUCS()
        self.requires_extrusion = self.ucs.uz != (0, 0, 1)
        if self.requires_extrusion:  # set extrusion vector of DIMENSION entity
            self.dimension.dxf.extrusion = self.ucs.uz

    @property
    def supports_dxf_r2000(self) -> bool:
        return self.dxfversion >= 'AC1015'

    @property
    def user_location_override(self) -> bool:
        return self.dimension.get_flag_state(self.dimension.USER_LOCATION_OVERRIDE, name='dimtype')

    @property
    def text_style_name(self) -> str:
        return self.dim_style.get('dimtxsty', options.default_dimension_text_style)

    @property
    def text_style(self) -> 'Style':
        return self.drawing.styles.get(self.text_style_name)

    @property
    def char_height(self) -> float:
        height = self.text_style.get_dxf_attrib('height', 0)
        if height == 0:  # variable text height (not fixed)
            height = self.dim_style.get('dimtxt', 1.)
        return height

    def text_width(self, text: str) -> float:
        char_width = self.char_height * self.text_style.get_dxf_attrib('width', 1.)
        return len(text) * char_width

    @property
    def text_rotation(self) -> float:
        text_rotation = self.dimension.get_dxf_attrib('text_rotation', None)
        if text_rotation is not None:
            angle = text_rotation  # absolute angle
        else:
            # dimtih - text inside horizontal: not supported by ezdxf, use text_rotation attribute
            # dimtoh - text outside horizontal: not supported by ezdxf, use text_rotation attribute
            # text is aligned to dimension line
            angle = self.dimension.get_dxf_attrib('angle', 0)
            if self.dim_style.get('dimjust', 0) in (3, 4):  # text above extension line, rotated about 90 degrees
                angle += 90.
        return angle

    @property
    def text_gap(self) -> float:
        return self.dim_style.get('dimgap', 0.625)

    @property
    def arrow_size(self) -> float:
        return self.dim_style.get('dimasz')

    def default_attributes(self) -> dict:
        return {
            'layer': self.dimension.dxf.layer,
            'color': self.dimension.dxf.color,
        }

    @property
    def text_movement_rule(self) -> int:
        return self.dim_style.get('dimtmove', 0)

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
                     scale: float = 1., dxfattribs: dict = None) -> Vector:
        if name in ARROWS:  # generates automatically BLOCK definitions for arrows if needed
            self.block.add_arrow_blockref(name, insert=insert, size=scale, rotation=rotation, dxfattribs=dxfattribs)
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
        attribs['style'] = self.text_style_name

        if self.dxfversion > 'AC1009':
            attribs['char_height'] = self.char_height
            attribs['insert'] = pos
            attribs['attachment_point'] = self.dimension.get_dxf_attrib('align', const.MTEXT_ALIGN_FLAGS.get(align, 5))
            if dxfattribs:
                attribs.update(dxfattribs)
            self.block.add_mtext(text, dxfattribs=attribs)
        else:
            attribs['height'] = self.char_height
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

    def add_leader(self, p1: Vector, p2: Vector, p3: Vector, dxfattribs: dict = None) -> None:
        attribs = self.default_attributes()
        if dxfattribs:
            attribs.update(dxfattribs)
        if self.supports_dxf_r2000:
            self.block.add_lwpolyline([p1.xy, p2.xy, p3.xy], dxfattribs=dxfattribs)
        else:
            self.block.add_line(self.wcs(p1), self.wcs(p2), dxfattribs=attribs)
            self.block.add_line(self.wcs(p2), self.wcs(p3), dxfattribs=attribs)


class LinearDimension(DimensionBase):
    def render(self):
        dim = self.dimension.dxf

        angle = math.radians(dim.angle)
        ext_angle = angle + math.pi / 2.

        # text_movement_rule (dimtmove):
        # 0 = Moves the dimension line with dimension text
        # 1 = Adds a leader when dimension text is moved
        # 2 = Allows text to be moved freely without a leader

        if self.user_location_override and self.text_movement_rule == 0:
            # user_location_override also moves dimension line location!
            dimline_ray = ConstructionRay(dim.text_midpoint, angle=angle)
        else:
            dimline_ray = ConstructionRay(dim.defpoint, angle=angle)

        # extension lines
        ext1_ray = ConstructionRay(dim.defpoint2, angle=ext_angle)
        ext2_ray = ConstructionRay(dim.defpoint3, angle=ext_angle)

        # dimension definition points
        dimline_start = dimline_ray.intersect(ext1_ray)
        dimline_end = dimline_ray.intersect(ext2_ray)
        dim.defpoint = dimline_start  # set defpoint to expected location for text_movement_rule == 0

        dimlfac = self.dim_style.get('dimlfac', 1.)
        measurement = (dimline_start - dimline_end).magnitude
        dim_text = self.get_text(measurement * dimlfac)
        text_outside = False

        # add text
        if dim_text:
            dim_text_width = self.text_width(dim_text)
            reqired_text_space = dim_text_width + 2 * (self.arrow_size + self.text_gap)
            text_outside = reqired_text_space < measurement
            if self.dim_style.get('dimtix', 0) == 1:  # force text inside
                text_outside = False

            text_location = self.text_location(dimline_start, dimline_end, dim_text_width, text_outside)
            self.add_measurement_text(dim_text, text_location)

            # add leader
            if self.user_location_override and self.text_movement_rule == 1:
                angle = self.text_rotation
                gap = self.text_gap
                height = self.char_height
                width = dim_text_width
                bounding_box = self.get_text_bounding_box(text_location, angle, width, height, gap)
                target_point = dimline_start.lerp(dimline_end)
                self.add_leader(target_point, bounding_box[0], bounding_box[1])

        # add extension line 1
        if not self.dim_style.get('dimse1', False):  # suppress extension line 1
            start, end = self.extension_line_points(dim.defpoint2, dimline_start)
            self.add_extension_line(start, end, num=1)

        # add extension line 2
        if not self.dim_style.get('dimse2', False):  # suppress extension line 2
            start, end = self.extension_line_points(dim.defpoint3, dimline_end)
            self.add_extension_line(start, end, num=2)

        blk1, blk2 = self.dim_style.get_arrow_names()

        # add arrow symbols (block references)
        dimline_start, dimline_end = self.add_arrows(dimline_start, dimline_end, blk1, blk2)
        self.add_dimension_line(dimline_start, dimline_end, blk1, blk2)

        # add POINT entities at definition points
        self.add_defpoints([dim.defpoint, dim.defpoint2, dim.defpoint3])

        # transform ucs coordinates into WCS and OCS
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
        self.add_text(dim_text, pos=pos, rotation=self.text_rotation, dxfattribs=attribs)

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
        linetype_name = self.dim_style['dimltype']
        if linetype_name is not None:
            attribs['linetype'] = linetype_name

        # lineweight requires DXF R2000 or later
        if self.supports_dxf_r2000:
            attribs['lineweight'] = self.dim_style.get('dimlwd', const.LINEWEIGHT_BYBLOCK)

        self.add_line(start, end, dxfattribs=attribs)

    def extension_line_points(self, start: 'Vertex', end: 'Vertex') -> Tuple[Vector, Vector]:
        """
        Adjust start and end point of extension line by dimension variables DIMEXE, DIMEXO, DIMEXFIX, DIMEXLEN.

        Args:
            start: start point of extension line (measurement point)
            end: end point at dimension line

        Returns: adjusted start and end point

        """
        has_fixed_length = self.dim_style.get('dimexfix', 0)
        direction = (end - start).normalize()
        extension = self.dim_style.get('dimexe', 0.)

        if has_fixed_length:
            fixed_length = self.dim_style.get('dimexlen', extension)
            start = end - (direction * fixed_length)
        else:
            offset = self.dim_style.get('dimexo', 0.)
            start = start + direction * offset
        end = end + direction * extension
        return start, end

    def add_extension_line(self, start: 'Vertex', end: 'Vertex', num: int = 1) -> None:
        attribs = {
            'color': self.dim_style.get('dimclre', self.dimension.dxf.color)
        }
        if num == 1:
            linetype_name = self.dim_style['dimltex1']
        elif num == 2:
            linetype_name = self.dim_style['dimltex2']
        else:
            raise ValueError('invalid argument num, has to be 1 or 2.')

        if linetype_name is not None:
            attribs['linetype'] = linetype_name

        # lineweight requires DXF R2000 or later
        if self.supports_dxf_r2000:
            attribs['lineweight'] = self.dim_style.get('dimlwe', const.LINEWEIGHT_BYBLOCK)

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
            scale = self.arrow_size
            start_angle = dim.angle + 180.
            end_angle = dim.angle
            self.add_blockref(blk1, insert=start, scale=scale, rotation=start_angle, dxfattribs=attribs)  # reverse
            self.add_blockref(blk2, insert=end, scale=scale, rotation=end_angle, dxfattribs=attribs)
            start = connection_point(blk1, start, scale, start_angle)
            end = connection_point(blk2, end, scale, end_angle)

        return start, end

    @property
    def tad_factor(self) -> float:
        """dimtad value as factor: returns 1 for above, 0 for center and -1 for below dimension line"""
        tad = self.dim_style.get('dimtad', 1)
        if tad == 0:
            return 0
        elif tad == 4:
            return -1
        else:
            return 1

    def text_vertical_distance(self) -> float:
        """
        Returns the vertical distance for dimension line to text midpoint. Positive values are above the line, negative
        values are below the line.
        """
        return (self.char_height / 2. + self.text_gap) * self.tad_factor

    def text_location(self, start: Vector, end: Vector, text_width: float, text_outside: bool = False) -> Vector:
        """
        Calculate text midpoint in drawing units.

        Args:
            start: start point of dimension line
            end: end point of dimension line
            text_width: text with in drawing units
            text_outside: place text outside of extension lines, applies only for dimjust = 0, 1 or 2

        """
        if self.user_location_override:
            text_location = self.dimension.get_dxf_attrib('text_midpoint')
            if self.text_movement_rule == 0:
                # text_location defines the text location along the dimension line
                # vertical distance from dimension line to text midpoint, normal to the dimension line
                vdist = self.text_vertical_distance()
            else:  # move text freely by text_midpoint
                return text_location
        else:
            # text_location defines the text location along the dimension line
            justify = self.dim_style.get('dimjust', 0)
            # default location: above the dimension line and centered between extension lines
            text_location = start.lerp(end)
            offset = self.text_gap + self.arrow_size + text_width / 2
            if justify == 1:  # positions the text next to the first extension line
                text_location = start + (end - start).normalize(offset)
            elif justify == 2:  # positions the text next to the second extension line
                text_location = end + (start - end).normalize(offset)
            elif justify in (3, 4):  # positions the text above and aligned with the first/second extension line
                dist = self.text_gap + self.char_height / 2.
                _offset = (start - end).normalize(dist) * self.tad_factor
                if justify == 3:
                    text_location = start + _offset
                else:
                    text_location = end + _offset

            self.dimension.set_dxf_attrib('text_midpoint', text_location)
            if justify in (0, 1, 2):
                vdist = self.text_vertical_distance()
            else:
                vdist = offset

        # lift text location
        ortho = (end - start).orthogonal().normalize(vdist)
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

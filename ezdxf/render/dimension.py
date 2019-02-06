# Created: 28.12.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple, Iterable, List, cast
import math
from ezdxf.math import Vector, ConstructionRay, xround, ConstructionLine, ConstructionBox
from ezdxf.math import UCS, PassTroughUCS
from ezdxf.lldxf import const
from ezdxf.options import options
from ezdxf.lldxf.const import DXFValueError, DXFUndefinedBlockError
from ezdxf.tools import suppress_zeros
from ezdxf.render.arrows import ARROWS, connection_point
from ezdxf.dimstyleoverride import DimStyleOverride

if TYPE_CHECKING:
    from ezdxf.eztypes import Dimension, BlockLayout, Vertex, Drawing, GenericLayoutType


class TextBox(ConstructionBox):
    def __init__(self, center: 'Vertex', width: float, height: float, angle: float, gap: float = 0):
        # width += (2 * gap)  # without real text width, looks better for proportional fonts
        height += (2 * gap)
        super().__init__(center, width, height, angle)


class BaseDimensionRenderer:
    def __init__(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS' = None,
                 override: DimStyleOverride = None):
        self.drawing = dimension.drawing
        self.dimension = dimension
        self.dxfversion = self.drawing.dxfversion
        self.supports_dxf_r2000 = self.dxfversion >= 'AC1015'
        self.block = block
        if override:
            self.dim_style = override
        else:
            self.dim_style = DimStyleOverride(dimension)
        self.ucs = ucs or PassTroughUCS()
        self.requires_extrusion = self.ucs.uz != (0, 0, 1)

        # ezdxf specific attributes beyond DXF reference, therefore not stored in the DSTYLE data
        # Some of these are just an rendering effect, which will be ignored by CAD applications if they modify the
        # DIMENSION entity
        #
        # user location override as UCS coordinates
        self.user_location = self.dim_style.pop('user_location', None)

        # user location override relative to dimline center if True
        self.relative_user_location = self.dim_style.pop('relative_user_location', False)

        # shift text from default text location - implemented as user location override without leader
        self.text_shift_h = self.dim_style.pop('text_shift_h', 0.)  # shift text in text direction
        self.text_shift_v = self.dim_style.pop('text_shift_v', 0.)  # shift text perpendicular to text direction

        # suppress arrow rendering - only rendering is suppressed (rendering effect), all placing related calculations
        # are done without this settings. Used for multi point linear dimensions to avoid double rendering of non arrow
        # ticks.
        self.suppress_arrow1 = self.dim_style.pop('suppress_arrow1', False)
        self.suppress_arrow2 = self.dim_style.pop('suppress_arrow2', False)
        # end of ezdxf specific attributes

        self.default_color = self.dimension.dxf.color
        self.default_layer = self.dimension.dxf.layer
        # ezdxf creates ALWAYS dimension.dxf.attachment_point = 5
        self.attachment_point = 5  # ignored by ezdxf at rendering
        self.horizontal_direction = self.dimension.get_dxf_attrib('horizontal_direction', None)  # ignored by ezdxf

        get = self.dim_style.get
        self.dim_scale = get('dimscale', 1)  # overall scaling
        if self.dim_scale == 0:
            self.dim_scale = 1
        self.dim_measurement_factor = get('dimlfac', 1)

        # text properties
        self.text_style_name = get('dimtxsty', options.default_dimension_text_style)
        self.text_style = self.drawing.styles.get(self.text_style_name)
        self.text_height = self.char_height * self.dim_scale
        self.text_width_factor = self.text_style.get_dxf_attrib('width', 1.)
        self.text_gap = get('dimgap', 0.625) * self.dim_scale
        self.text_rotation = self.dimension.get_dxf_attrib('text_rotation', None)
        self.text_color = get('dimclrt', self.default_color)
        self.text_round = get('dimrnd', None)
        self.text_decimal_places = get('dimdec', None)
        self.text_suppress_zeros = get('dimzin', 0)
        dimdsep = self.dim_style.get('dimdsep', 0)
        self.text_decimal_separator = ',' if dimdsep == 0 else chr(dimdsep)
        self.text_format = self.dim_style.get('dimpost', '<>')
        self.text_fill = self.dim_style.get('dimtfill', 0)  # 0= None, 1=Background, 2=DIMTFILLCLR
        self.text_fill_color = self.dim_style.get('dimtfillclr', 1)
        # text_halign = 0: center; 1: left; 2: right; 3: above ext1; 4: above ext2
        self.text_halign = get('dimjust', 0)

        # text_valign = 0: center; 1: above; 2: farthest away?; 3: JIS?; 4: below (2, 3 ignored by ezdxf)
        self.text_valign = get('dimtad', 0)

        self.text_movement_rule = get('dimtmove', 2)  # move text freely
        if self.text_movement_rule == 0:
            # moves the dimension line with dimension text and makes no sense for ezdxf (just set `base` argument)
            self.text_movement_rule = 2
        self.text_inside_horizontal = get('dimtih', 0)  # ignored by ezdxf
        self.text_outside_horizontal = get('dimtoh', 0)  # ignored by ezdxf
        self.force_text_inside = bool(get('dimtix', 0))

        # arrow properties
        self.tick_size = get('dimtsz') * self.dim_scale
        if self.tick_size > 0:
            self.arrow1_name, self.arrow2_name = None, None
            self.arrow_size = self.tick_size * 2
        else:
            # arrow name or block name if user defined arrow
            self.arrow1_name, self.arrow2_name = self.dim_style.get_arrow_names()
            self.arrow_size = get('dimasz') * self.dim_scale

        # dimension line properties
        self.dim_line_color = get('dimclrd', self.default_color)
        self.dim_line_extension = bool(get('dimdle', False))
        self.dim_linetype = get('dimltype', None)
        self.dim_lineweight = get('dimlwd', const.LINEWEIGHT_BYBLOCK)
        self.suppress_dim1_line = bool(get('dimsd1', False))
        self.suppress_dim2_line = bool(get('dimsd2', False))

        # extension line properties
        self.ext_line_color = get('dimclre', self.default_color)
        self.ext1_linetype_name = get('dimltex1', None)
        self.ext2_linetype_name = get('dimltex2', None)
        self.ext_lineweight = get('dimlwe', const.LINEWEIGHT_BYBLOCK)
        self.suppress_ext1_line = bool(get('dimse1', False))
        self.suppress_ext2_line = bool(get('dimse2', False))
        self.ext_line_extension = get('dimexe', 0.) * self.dim_scale
        self.ext_line_offset = get('dimexo', 0.) * self.dim_scale
        self.ext_line_fixed = bool(get('dimflxon', False))
        self.ext_line_length = get('dimflx', self.ext_line_extension) * self.dim_scale

    def render(self):  # interface definition
        pass

    @property
    def char_height(self) -> float:
        height = self.text_style.get_dxf_attrib('height', 0)
        if height == 0:  # variable text height (not fixed)
            height = self.dim_style.get('dimtxt', 1.)
        return height

    def text_width(self, text: str) -> float:
        char_width = self.text_height * self.text_width_factor
        return len(text) * char_width

    def default_attributes(self) -> dict:
        return {
            'layer': self.default_layer,
            'color': self.default_color,
        }

    def wcs(self, point: 'Vertex') -> Vector:
        return self.ucs.to_wcs(point)

    def ocs(self, point: 'Vertex') -> Vector:
        return self.ucs.to_ocs(point)

    def to_ocs_angle(self, angle: float) -> float:
        return self.ucs.to_ocs_angle_deg(angle)

    def text_override(self, measurement: float) -> str:
        text = self.dimension.dxf.text
        if text == ' ':  # suppress text
            return ''
        elif text == '' or text == '<>':  # measured distance
            return self.format_text(measurement)
        else:  # user override
            return text

    def format_text(self, value: float) -> str:
        return format_text(
            value,
            self.text_round,
            self.text_decimal_places,
            self.text_suppress_zeros,
            self.text_decimal_separator,
            self.text_format,
        )

    def location_override(self, location: 'Vertex', leader=False, relative=False):
        self.dim_style.set_location(location, leader, relative)
        self.user_location = Vector(location)
        self.text_movement_rule = 1 if leader else 2
        self.relative_user_location = relative

    def add_line(self, start: 'Vertex', end: 'Vertex', dxfattribs: dict = None) -> None:
        attribs = self.default_attributes()
        if dxfattribs:
            attribs.update(dxfattribs)
        self.block.add_line(self.wcs(start), self.wcs(end), dxfattribs=attribs)

    def add_blockref(self, name: str, insert: 'Vertex', rotation: float = 0,
                     scale: float = 1., dxfattribs: dict = None) -> Vector:
        attribs = self.default_attributes()
        insert = self.ocs(insert)
        rotation = self.to_ocs_angle(rotation)
        if self.requires_extrusion:
            attribs['extrusion'] = self.ucs.uz
        if name in ARROWS:  # generates automatically BLOCK definitions for arrows if needed
            if dxfattribs:
                attribs.update(dxfattribs)
            self.block.add_arrow_blockref(name, insert=insert, size=scale, rotation=rotation, dxfattribs=attribs)
        else:
            if name not in self.drawing.blocks:
                raise DXFUndefinedBlockError('Undefined block: "{}"'.format(name))
            attribs['rotation'] = rotation
            if scale != 1.:
                attribs['xscale'] = scale
                attribs['yscale'] = scale
            if dxfattribs:
                attribs.update(dxfattribs)
            self.block.add_blockref(name, insert=insert, dxfattribs=attribs)
            return insert

    def add_text(self, text: str, pos: 'Vertex', rotation: float, align='MIDDLE_CENTER',
                 dxfattribs: dict = None) -> None:
        attribs = self.default_attributes()
        attribs['style'] = self.text_style_name
        attribs['color'] = self.text_color
        if self.requires_extrusion:
            attribs['extrusion'] = self.ucs.uz

        if self.supports_dxf_r2000:
            text_direction = self.ucs.to_wcs(Vector.from_deg_angle(rotation)) - self.ucs.origin
            attribs['text_direction'] = text_direction
            attribs['char_height'] = self.text_height
            attribs['insert'] = self.wcs(pos)
            attribs['attachment_point'] = const.MTEXT_ALIGN_FLAGS[align]

            if self.dxfversion >= 'AC1021':
                if self.text_fill:
                    attribs['box_fill_scale'] = 1.1
                    attribs['bg_fill_color'] = self.text_fill_color
                    attribs['bg_fill'] = 3 if self.text_fill == 1 else 1

            if dxfattribs:
                attribs.update(dxfattribs)
            self.block.add_mtext(text, dxfattribs=attribs)
        else:
            attribs['rotation'] = self.ucs.to_ocs_angle_deg(rotation)
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


class LinearDimension(BaseDimensionRenderer):
    def __init__(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS' = None,
                 override: 'DimStyleOverride' = None):
        super().__init__(dimension, block, ucs, override)
        self.oblique_angle = self.dimension.get_dxf_attrib('oblique_angle', 90)
        self.dim_line_angle = self.dimension.get_dxf_attrib('angle', 0)
        self.dim_line_angle_rad = math.radians(self.dim_line_angle)
        self.ext_line_angle = self.dim_line_angle + self.oblique_angle
        self.ext_line_angle_rad = math.radians(self.ext_line_angle)

        if self.text_rotation is None:
            # text_inside_horizontal: not supported by ezdxf, use text_rotation attribute
            # text_outside_horizontal: not supported by ezdxf, use text_rotation attribute
            # text is aligned to dimension line
            self.text_rotation = self.dim_line_angle

        if self.text_halign in (3, 4):  # text above extension line, is always aligned with extension lines
            self.text_rotation = self.ext_line_angle

        self.ext1_line_start = self.dimension.dxf.defpoint2
        self.ext2_line_start = self.dimension.dxf.defpoint3

        ext1_ray = ConstructionRay(self.ext1_line_start, angle=self.ext_line_angle_rad)
        ext2_ray = ConstructionRay(self.ext2_line_start, angle=self.ext_line_angle_rad)
        dim_line_ray = ConstructionRay(self.dimension.dxf.defpoint, angle=self.dim_line_angle_rad)

        self.dim_line_start = dim_line_ray.intersect(ext1_ray)
        self.dim_line_end = dim_line_ray.intersect(ext2_ray)
        self.dimension.dxf.defpoint = self.dim_line_start  # set defpoint to expected location
        self.measurement = (self.dim_line_end - self.dim_line_start).magnitude
        self.text = self.text_override(self.measurement * self.dim_measurement_factor)
        self.text_location = None  # actual calculated or overridden dimension text location
        self.text_box = None  # bounding box of dimension text
        self.is_wide_text = False  # True if text+spacing+arrows  doesn't have enough space between extension lines

        # only for linear dimension in multi point mode
        self.multi_point_mode = override.pop('multi_point_mode', False)
        # 1 .. move wide text up
        # 2 .. move wide text down
        # None .. ignore
        self.move_wide_text = override.pop('move_wide_text', None)

        # place text outside of extension lines, only True if really placed outside
        # for forced text inside, text_outside is False
        self.text_outside = False
        self.dim_text_width = 0  # actual text width in drawing units
        self.text_spacing = self.text_gap * .75  # spacing in front and after dimension text
        self.required_text_space = 0

        # calculate text location
        if self.text:
            self.dim_text_width = self.text_width(self.text)
            self.required_text_space = self.dim_text_width + 2 * (self.arrow_size + self.text_spacing)
            self.is_wide_text = self.required_text_space > self.measurement
            if self.force_text_inside:
                if self.text_halign < 3:
                    self.text_halign = 0  # center text
            else:
                # place text outside if wide text and not forced inside
                self.text_outside = self.is_wide_text

            # use relative text shift to move wide text up or down in multi point mode
            if self.multi_point_mode and self.is_wide_text and self.move_wide_text > 0:
                shift_value = self.text_height + self.text_gap
                if self.move_wide_text == 1:  # move text up
                    self.text_shift_v = shift_value
                    if self.vertical_factor == -1:  # text below dimension line
                        # shift again
                        self.text_shift_v += shift_value
                elif self.move_wide_text == 2:  # move text down
                    self.text_shift_v = -shift_value
                    if self.vertical_factor == 1:  # text above dimension line
                        # shift again
                        self.text_shift_v -= shift_value

            self.text_location = self.get_text_location()
            self.text_box = TextBox(
                center=self.text_location,
                width=self.dim_text_width,
                height=self.text_height,
                angle=self.text_rotation,
                gap=self.text_spacing
            )

        self.required_arrows_space = 2 * self.arrow_size + self.text_gap
        self.arrows_outside = self.required_arrows_space > self.measurement

    @property
    def has_relative_text_movement(self):
        return bool(self.text_shift_h or self.text_shift_v)

    def apply_text_shift(self, location: Vector, text_rotation: float) -> Vector:
        shift_vec = Vector(self.text_shift_h, self.text_shift_v)
        location += shift_vec.rot_z_deg(text_rotation)
        return location

    def add_leader(self, p1: Vector, p2: Vector, p3: Vector, dxfattribs: dict = None) -> Vector:
        def order_points():
            if (p1 - p2).magnitude_xy > (p1 - p3).magnitude_xy:
                return p3, p2
            else:
                return p2, p3

        p2, p3 = order_points()
        self.add_line(p1, p2, dxfattribs)
        self.add_line(p2, p3, dxfattribs)
        return p2

    def render(self):
        # add extension line 1
        if not self.suppress_ext1_line:
            above_ext_line1 = self.text_halign == 3
            start, end = self.extension_line_points(self.ext1_line_start, self.dim_line_start, above_ext_line1)
            self.add_extension_line(start, end, linetype=self.ext1_linetype_name)

        # add extension line 2
        if not self.suppress_ext2_line:
            above_ext_line2 = self.text_halign == 4
            start, end = self.extension_line_points(self.ext2_line_start, self.dim_line_end, above_ext_line2)
            self.add_extension_line(start, end, linetype=self.ext2_linetype_name)

        # add arrow symbols (block references), also adjust dimension line start and end point
        dim_line_start, dim_line_end = self.add_arrows(
            self.dim_line_start,
            self.dim_line_end,
            self.arrows_outside,
        )

        # add dimension line
        self.add_dimension_line(dim_line_start, dim_line_end)

        # add measurement text at last to see text fill properly
        if self.text:
            self.add_measurement_text(self.text, self.text_location, self.text_rotation)
            # add leader
            if self.user_location is not None and self.text_movement_rule == 1:
                target_point = self.dim_line_start.lerp(self.dim_line_end)
                p2, p3, *_ = self.text_box.corners
                defpoint = self.add_leader(target_point, p2, p3)
                self.dimension.dxf.text_midpoint = defpoint

        # add POINT entities at definition points
        self.add_defpoints([self.dim_line_start, self.ext1_line_start, self.ext2_line_start])

        # transform DIMENSION attributes into WCS and OCS
        self.dimension_to_wcs()

    def get_text_location(self) -> Vector:
        """
        Get text midpoint in ucs from user defined location or default text location.

        """
        start = self.dim_line_start
        end = self.dim_line_end

        # apply relative text shift as user location override without leader
        if self.has_relative_text_movement:
            location = self.default_text_location()
            location = self.apply_text_shift(location, self.text_rotation)
            self.location_override(location)

        if self.user_location is not None:
            location = self.user_location
            if self.relative_user_location:
                location = start.lerp(end) + location
            # set text location override
            self.dimension.dxf.text_midpoint = location
        else:
            location = self.default_text_location()

            # project standard text location onto dimension line
            dim_line_vec = end - start
            text_midpoint = start + dim_line_vec.project(location - start)
            self.dimension.dxf.text_midpoint = text_midpoint

        return location

    def default_text_location(self) -> Vector:
        """
        Default text location based on `self.text_halign`, `self.text_valign` and `self.text_outside`

        Returns: text midpoint in ucs as Vector()

        """
        start = self.dim_line_start
        end = self.dim_line_end
        halign = self.text_halign

        # positions the text above and aligned with the first/second extension line
        if halign in (3, 4):
            # horizontal location
            hdist = self.text_gap + self.text_height / 2.
            hvec = (start - end).normalize(hdist)
            location = (start if halign == 3 else end) + hvec
            # vertical location
            vdist = self.ext_line_extension + self.dim_text_width / 2.
            location += Vector.from_deg_angle(self.ext_line_angle).normalize(vdist)
        else:
            # relocate outside text if centered to the second extension line
            if self.text_outside and halign == 0:
                halign = 2
                self.text_halign = halign
            if start == end:
                dim_line_vec = Vector.from_rad_angle(self.dim_line_angle_rad)
            else:
                dim_line_vec = end - start

            if halign == 0:
                location = start.lerp(end)  # center of dimension line
            else:
                hdist = self.required_text_space / 2
                if self.text_outside:  # move text outside
                    hdist = -(hdist + self.arrow_size)

                if halign == 1:  # positions the text next to the first extension line
                    location = start + dim_line_vec.normalize(hdist)
                else:  # positions the text next to the second extension line
                    location = end - dim_line_vec.normalize(hdist)

            # distance from extension line to text midpoint
            vdist = self.text_vertical_distance()
            location += dim_line_vec.orthogonal().normalize(vdist)

        return location

    def add_arrows(self, start: 'Vertex', end: 'Vertex', outside: bool = False) -> Tuple[Vector, Vector]:
        attribs = {
            'color': self.dim_line_color,
        }
        arrow1 = not self.suppress_arrow1
        arrow2 = not self.suppress_arrow2

        if self.tick_size > 0.:  # oblique stroke, but double the size
            if arrow1:
                self.add_blockref(
                    ARROWS.oblique,
                    insert=start,
                    rotation=self.dim_line_angle,
                    scale=self.tick_size * 2,
                    dxfattribs=attribs,
                )
            if arrow2:
                self.add_blockref(
                    ARROWS.oblique,
                    insert=end,
                    rotation=self.dim_line_angle,
                    scale=self.tick_size * 2,
                    dxfattribs=attribs,
                )
        else:
            scale = self.arrow_size
            start_angle = self.dim_line_angle + 180.
            end_angle = self.dim_line_angle
            if outside:
                start_angle, end_angle = end_angle, start_angle
            if arrow1:
                self.add_blockref(self.arrow1_name, insert=start, scale=scale, rotation=start_angle,
                                  dxfattribs=attribs)  # reverse
            if arrow2:
                self.add_blockref(self.arrow2_name, insert=end, scale=scale, rotation=end_angle, dxfattribs=attribs)

            if not outside:
                if arrow1:
                    start = connection_point(self.arrow1_name, start, scale, start_angle)
                if arrow2:
                    end = connection_point(self.arrow2_name, end, scale, end_angle)

        if outside:  # add extension lines to arrows if outside
            def has_arrow_extension(name: str) -> bool:
                return (name is not None) and (name in ARROWS) and (name not in ARROWS.ORIGIN_ZERO)

            def extension_line(arrow_name, outside):
                start = None
                end = None
                arrow_size = self.arrow_size
                two_arrows_length = 2 * arrow_size

                if has_arrow_extension(arrow_name):  # just for arrows
                    start = arrow_size
                    end = two_arrows_length

                if outside:
                    end = two_arrows_length + text_width
                    if start is None:
                        start = 0
                    if text_is_vcenter:
                        end = two_arrows_length
                return start, end

            text_width = self.dim_text_width
            text_is_left = self.text_outside and self.text_halign == 1
            text_is_right = self.text_outside and self.text_halign in (0, 2)
            text_is_vcenter = self.text_valign == 0
            if arrow1:
                start_, end_ = extension_line(self.arrow1_name, text_is_left)
                if start_ is not None:
                    dir_vec = (start - end)
                    self.add_line(
                        start + dir_vec.normalize(start_),
                        start + dir_vec.normalize(end_),
                        dxfattribs=attribs,
                    )
            if arrow2:
                start_, end_ = extension_line(self.arrow2_name, text_is_right)
                if start_ is not None:
                    dir_vec = (end - start)
                    self.add_line(
                        end + dir_vec.normalize(start_),
                        end + dir_vec.normalize(end_),
                        dxfattribs=attribs,
                    )

        return start, end

    def dimension_to_wcs(self) -> None:
        def from_ucs(attr, func):
            point = self.dimension.get_dxf_attrib(attr)
            self.dimension.set_dxf_attrib(attr, func(point))

        from_ucs('defpoint', self.wcs)
        from_ucs('defpoint2', self.wcs)
        from_ucs('defpoint3', self.wcs)
        from_ucs('text_midpoint', self.ocs)
        self.dimension.dxf.angle = self.ucs.to_ocs_angle_deg(self.dimension.dxf.angle)

    def add_measurement_text(self, dim_text: str, pos: Vector, rotation: float) -> None:
        attribs = {
            'color': self.text_color,
        }
        self.add_text(dim_text, pos=pos, rotation=rotation, dxfattribs=attribs)

    def add_dimension_line(self, start: 'Vertex', end: 'Vertex') -> None:
        def order(a: Vector, b: Vector) -> Tuple[Vector, Vector]:
            if (start - a).magnitude < (start - b).magnitude:
                return a, b
            else:
                return b, a
        if start == end:
            direction = Vector.from_rad_angle(self.dim_line_angle_rad)
        else:
            direction = (end - start).normalize()
        extension = direction * self.dim_line_extension
        if self.arrow1_name is None or ARROWS.has_extension_line(self.arrow1_name):
            start = start - extension
        if self.arrow2_name is None or ARROWS.has_extension_line(self.arrow2_name):
            end = end + extension

        attribs = {
            'color': self.dim_line_color
        }
        if self.dim_linetype is not None:
            attribs['linetype'] = self.dim_linetype

        # lineweight requires DXF R2000 or later
        if self.supports_dxf_r2000:
            attribs['lineweight'] = self.dim_lineweight

        if self.text_box:  # is dimension line crossing text
            intersection_points = self.text_box.intersect(ConstructionLine(start, end))
        else:
            intersection_points = []
        if len(intersection_points) == 2:
            # sort all points, line[0-1] - gap - line[2-3]
            intersection_points.extend([start, end])
            p1, p2 = order(intersection_points[0], intersection_points[1])

            if not self.suppress_dim1_line:
                self.add_line(start, p1, dxfattribs=attribs)
            if not self.suppress_dim2_line:
                self.add_line(p2, end, dxfattribs=attribs)

        else:  # no intersection
            self.add_line(start, end, dxfattribs=attribs)

    def extension_line_points(self, start: 'Vertex', end: 'Vertex', text_above_extline=False) -> Tuple[Vector, Vector]:
        """
        Adjust start and end point of extension line by dimension variables DIMEXE, DIMEXO, DIMEXFIX, DIMEXLEN.

        Args:
            start: start point of extension line (measurement point)
            end: end point at dimension line
            text_above_extline: True if text is above and aligned with extension line (halign == 3 or 4)

        Returns: adjusted start and end point

        """
        direction = (end - start).normalize()
        if self.ext_line_fixed:
            start = end - (direction * self.ext_line_length)
        else:
            start = start + direction * self.ext_line_offset
        extension = self.ext_line_extension
        if text_above_extline:
            extension += self.dim_text_width
        end = end + direction * extension
        return start, end

    def add_extension_line(self, start: 'Vertex', end: 'Vertex', linetype: str = None) -> None:
        attribs = {
            'color': self.ext_line_color
        }
        if linetype is not None:
            attribs['linetype'] = linetype

        # lineweight requires DXF R2000 or later
        if self.supports_dxf_r2000:
            attribs['lineweight'] = self.ext_lineweight

        self.add_line(start, end, dxfattribs=attribs)

    @property
    def vertical_factor(self) -> float:
        """text_valign as factor: returns 1 for above, 0 for center and -1 for below dimension line"""
        if self.text_valign == 0:
            return 0
        elif self.text_valign == 4:
            return -1
        else:
            return 1

    def text_vertical_distance(self) -> float:
        """
        Returns the vertical distance for dimension line to text midpoint. Positive values are above the line, negative
        values are below the line.

        """
        return (self.text_height / 2. + self.text_gap) * self.vertical_factor


class DimensionRenderer:
    def dispatch(self, override: 'DimStyleOverride', ucs: 'UCS') -> BaseDimensionRenderer:
        dimension = override.dimension
        dwg = override.drawing
        block = dwg.blocks.new_anonymous_block(type_char='D')
        dimension.dxf.geometry = block.name
        dim_type = dimension.dim_type

        if dim_type in (0, 1):
            return self.linear(dimension, block, ucs, override)
        elif dim_type == 2:
            return self.angular(dimension, block, ucs, override)
        elif dim_type == 3:
            return self.diameter(dimension, block, ucs, override)
        elif dim_type == 4:
            return self.radius(dimension, block, ucs, override)
        elif dim_type == 5:
            return self.angular3p(dimension, block, ucs, override)
        elif dim_type == 6:
            return self.ordinate(dimension, block, ucs, override)
        else:
            raise DXFValueError("Unknown DIMENSION type: {}".format(dim_type))

    def linear(self, dimension: 'Dimension', block: 'BlockLayout', ucs: 'UCS', override: 'DimStyleOverride' = None):
        """
        Call renderer for linear dimension lines: horizontal, vertical and rotated
        """
        return LinearDimension(dimension, block, ucs, override)

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
                dimpost: str = '<>') -> str:
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
    if dimdsep != '.':
        text = text.replace('.', dimdsep)
    if dimpost:
        if '<>' in dimpost:
            fmt = dimpost.replace('<>', '{}', 1)
            text = fmt.format(text)
        else:
            raise DXFValueError('Invalid dimpost string: "{}"'.format(dimpost))
    return text


CAN_SUPPRESS_ARROW1 = {
    ARROWS.dot,
    ARROWS.dot_small,
    ARROWS.dot_blank,
    ARROWS.origin_indicator,
    ARROWS.origin_indicator_2,
    ARROWS.dot_smallblank,
    ARROWS.none,
    ARROWS.oblique,
    ARROWS.box_filled,
    ARROWS.box,
    ARROWS.integral,
    ARROWS.architectural_tick,
}


def sort_projected_points(points: Iterable['Vertex'], angle: float = 0) -> List[Vector]:
    direction = Vector.from_deg_angle(angle)
    projected_vectors = [(direction.project(p), p) for p in points]
    return [p for projection, p in sorted(projected_vectors)]


def multi_point_linear_dimension(
        layout: 'GenericLayoutType',
        base: 'Vertex',
        points: Iterable['Vertex'],
        angle: float = 0,
        ucs: 'UCS' = None,
        avoid_double_rendering: bool = True,
        dimstyle: str = 'EZDXF',
        override: dict = None,
        dxfattribs: dict = None) -> None:
    def suppress_arrow1(dimstyle_override) -> bool:
        arrow_name1, arrow_name2 = dimstyle_override.get_arrow_names()
        if (arrow_name1 is None) or (arrow_name1 in CAN_SUPPRESS_ARROW1):
            return True
        else:
            return False

    points = sort_projected_points(points, angle)
    base = Vector(base)
    override = override or {}
    override['dimtix'] = 1  # do not place measurement text outside
    override['multi_point_mode'] = True
    # 1 .. move wide text up; 2 .. move wide text down; None .. ignore
    # moving text down, looks best combined with text fill bg: DIMTFILL = 1
    move_wide_text = 1
    _suppress_arrow1 = False
    first_run = True

    for p1, p2 in zip(points[:-1], points[1:]):
        _override = dict(override)
        _override['move_wide_text'] = move_wide_text
        if avoid_double_rendering and not first_run:
            _override['dimse1'] = 1
            _override['suppress_arrow1'] = _suppress_arrow1

        style = layout.add_linear_dim(
            base, p1, p2,
            angle=angle,
            dimstyle=dimstyle,
            override=_override,
            dxfattribs=dxfattribs,
        )
        if first_run:
            _suppress_arrow1 = suppress_arrow1(style)

        renderer = cast(LinearDimension, style.render(ucs))
        if renderer.is_wide_text:
            # after wide text switch moving direction
            if move_wide_text == 1:
                move_wide_text = 2
            else:
                move_wide_text = 1
        else:  # reset to move text up
            move_wide_text = 1
        first_run = False

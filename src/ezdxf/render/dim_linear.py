# Copyright (c) 2018-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    Tuple,
    Iterable,
    List,
    cast,
    Optional,
    Dict,
    Any,
)
import math
from ezdxf.math import Vec3, Vec2, ConstructionRay, UCS
from ezdxf.render.arrows import ARROWS, connection_point
from ezdxf.entities.dimstyleoverride import DimStyleOverride

from .dim_base import BaseDimensionRenderer, TextBox

if TYPE_CHECKING:
    from ezdxf.eztypes import Dimension, Vertex, GenericLayoutType


def order_leader_points(p1: Vec2, p2: Vec2, p3: Vec2) -> Tuple[Vec2, Vec2]:
    if (p1 - p2).magnitude > (p1 - p3).magnitude:
        return p3, p2
    else:
        return p2, p3


class LinearDimension(BaseDimensionRenderer):
    """Linear dimension line renderer, used for horizontal, vertical, rotated
    and aligned DIMENSION entities.

    Args:
        dimension: DXF entity DIMENSION
        ucs: user defined coordinate system
        override: dimension style override management object

    """

    def __init__(
        self,
        dimension: "Dimension",
        ucs: "UCS" = None,
        override: "DimStyleOverride" = None,
    ):
        super().__init__(dimension, ucs, override)
        if self.text_movement_rule == 0:  # type: ignore
            # moves the dimension line with dimension text, this makes no sense
            # for ezdxf (just set `base` argument)
            self.text_movement_rule = 2

        self.oblique_angle: float = self.dimension.get_dxf_attrib(
            "oblique_angle", 90
        )
        self.dim_line_angle: float = self.dimension.get_dxf_attrib("angle", 0)
        self.dim_line_angle_rad: float = math.radians(self.dim_line_angle)
        self.ext_line_angle: float = self.dim_line_angle + self.oblique_angle
        self.ext_line_angle_rad: float = math.radians(self.ext_line_angle)

        # text is aligned to dimension line
        self.text_rotation: float = self.dim_line_angle
        if self.text_halign in (  # type: ignore
            3,
            4,
        ):  # text above extension line, is always aligned with extension lines
            self.text_rotation = self.ext_line_angle

        self.ext1_line_start = Vec2(self.dimension.dxf.defpoint2)
        self.ext2_line_start = Vec2(self.dimension.dxf.defpoint3)

        ext1_ray = ConstructionRay(
            self.ext1_line_start, angle=self.ext_line_angle_rad
        )
        ext2_ray = ConstructionRay(
            self.ext2_line_start, angle=self.ext_line_angle_rad
        )
        dim_line_ray = ConstructionRay(
            self.dimension.dxf.defpoint, angle=self.dim_line_angle_rad
        )

        self.dim_line_start: Vec2 = dim_line_ray.intersect(ext1_ray)
        self.dim_line_end: Vec2 = dim_line_ray.intersect(ext2_ray)
        self.dim_line_center: Vec2 = self.dim_line_start.lerp(self.dim_line_end)

        if self.dim_line_start == self.dim_line_end:
            self.dim_line_vec = Vec2.from_angle(self.dim_line_angle_rad)
        else:
            self.dim_line_vec = (
                self.dim_line_end - self.dim_line_start
            ).normalize()

        # set dimension defpoint to expected location - 3D vertex required!
        self.dimension.dxf.defpoint = Vec3(self.dim_line_start)

        self.measurement: float = (
            self.dim_line_end - self.dim_line_start
        ).magnitude
        self.text: str = self.text_override(
            self.measurement * self.dim_measurement_factor
        )

        # only for linear dimension in multi point mode
        self.multi_point_mode = self.dim_style.pop("multi_point_mode", False)

        # 1 .. move wide text up
        # 2 .. move wide text down
        # None .. ignore
        self.move_wide_text: Optional[bool] = self.dim_style.pop(
            "move_wide_text", None
        )

        # actual text width in drawing units
        self.dim_text_width: float = 0

        # arrows
        self.required_arrows_space: float = 2 * self.arrow_size + self.text_gap
        self.arrows_outside: bool = (
            self.required_arrows_space > self.measurement
        )

        # text location and rotation
        if self.text:
            # text width and required space
            self.dim_text_width = self.text_width(self.text)
            if self.dim_tolerance:
                self.dim_text_width += self.tol_text_width  # type: ignore

            elif self.dim_limits:
                # limits show the upper and lower limit of the measurement as
                # stacked values and with the size of tolerances
                measurement = self.measurement * self.dim_measurement_factor
                self.measurement_upper_limit = measurement + self.tol_maximum
                self.measurement_lower_limit = measurement - self.tol_minimum
                self.tol_text_upper = self.format_tolerance_text(
                    self.measurement_upper_limit
                )
                self.tol_text_lower = self.format_tolerance_text(
                    self.measurement_lower_limit
                )
                self.tol_text_width = self.tolerance_text_width(
                    max(len(self.tol_text_upper), len(self.tol_text_lower))
                )

                # only limits are displayed so:
                self.dim_text_width = self.tol_text_width

            if self.multi_point_mode:
                # ezdxf has total control about vertical text position in multi
                # point mode
                self.text_vertical_position = 0.0

            if self.text_valign == 0 and abs(self.text_vertical_position) < 0.7:
                # vertical centered text needs also space for arrows
                required_space = self.dim_text_width + 2 * self.arrow_size
            else:
                required_space = self.dim_text_width
            self.is_wide_text = required_space > self.measurement

            if not self.force_text_inside:
                # place text outside if wide text and not forced inside
                self.text_outside = self.is_wide_text
            elif self.is_wide_text and self.text_halign < 3:  # type: ignore
                # center wide text horizontal
                self.text_halign = 0

            # use relative text shift to move wide text up or down in multi
            # point mode
            if (
                self.multi_point_mode
                and self.is_wide_text
                and self.move_wide_text
            ):
                shift_value = self.text_height + self.text_gap
                if self.move_wide_text == 1:  # move text up
                    self.text_shift_v = shift_value
                    if (
                        self.vertical_placement == -1
                    ):  # text below dimension line
                        # shift again
                        self.text_shift_v += shift_value
                elif self.move_wide_text == 2:  # move text down
                    self.text_shift_v = -shift_value
                    if (
                        self.vertical_placement == 1
                    ):  # text above dimension line
                        # shift again
                        self.text_shift_v -= shift_value

            # get final text location - no altering after this line
            self.text_location: Vec2 = self.get_text_location()

            # text rotation override
            rotation: float = self.text_rotation
            if self.user_text_rotation is not None:
                rotation = self.user_text_rotation
            elif self.text_outside and self.text_outside_horizontal:
                rotation = 0
            elif self.text_inside and self.text_inside_horizontal:
                rotation = 0
            self.text_rotation = rotation

            self.text_box = TextBox(
                center=self.text_location,
                width=self.dim_text_width,
                height=self.text_height,
                angle=self.text_rotation,
                gap=self.text_gap * 0.75,
            )
            if self.text_has_leader:
                p1, p2, *_ = self.text_box.corners
                self.leader1, self.leader2 = order_leader_points(
                    self.dim_line_center, p1, p2
                )
                # not exact what BricsCAD (AutoCAD) expect, but close enough
                self.dimension.dxf.text_midpoint = self.leader1
            else:
                # write final text location into DIMENSION entity
                self.dimension.dxf.text_midpoint = self.text_location

    @property
    def has_relative_text_movement(self):
        return bool(self.text_shift_h or self.text_shift_v)

    def apply_text_shift(self, location: Vec2, text_rotation: float) -> Vec2:
        """Add `self.text_shift_h` and `sel.text_shift_v` to point `location`,
        shifting along and perpendicular to text orientation defined by
        `text_rotation`.

        Args:
            location: location point
            text_rotation: text rotation in degrees

        Returns: new location

        """
        shift_vec = Vec2((self.text_shift_h, self.text_shift_v))
        location += shift_vec.rotate(text_rotation)
        return location

    def render(self, block: "GenericLayoutType") -> None:
        """Main method to create dimension geometry of basic DXF entities in the
        associated BLOCK layout.

        Args:
            block: target BLOCK for rendering

        """
        # call required to setup some requirements
        super().render(block)

        # add extension line 1
        if not self.suppress_ext1_line:
            above_ext_line1 = self.text_halign == 3
            start, end = self.extension_line_points(
                self.ext1_line_start, self.dim_line_start, above_ext_line1
            )
            self.add_extension_line(
                start, end, linetype=self.ext1_linetype_name
            )

        # add extension line 2
        if not self.suppress_ext2_line:
            above_ext_line2 = self.text_halign == 4
            start, end = self.extension_line_points(
                self.ext2_line_start, self.dim_line_end, above_ext_line2
            )
            self.add_extension_line(
                start, end, linetype=self.ext2_linetype_name
            )

        # add arrow symbols (block references), also adjust dimension line start
        # and end point
        dim_line_start, dim_line_end = self.add_arrows()

        # add dimension line
        self.add_dimension_line(dim_line_start, dim_line_end)

        # add measurement text as last entity to see text fill properly
        if self.text:
            if self.supports_dxf_r2000:
                text = self.compile_mtext()
            else:
                text = self.text
            self.add_measurement_text(
                text, self.text_location, self.text_rotation
            )
            if self.text_has_leader:
                self.add_leader(
                    self.dim_line_center, self.leader1, self.leader2
                )

        # add POINT entities at definition points
        self.add_defpoints(
            [self.dim_line_start, self.ext1_line_start, self.ext2_line_start]
        )

    def get_text_location(self) -> Vec2:
        """Get text midpoint in UCS from user defined location or default text
        location.

        """
        # apply relative text shift as user location override without leader
        if self.has_relative_text_movement:
            location = self.default_text_location()
            location = self.apply_text_shift(location, self.text_rotation)
            self.location_override(location)

        if self.user_location is not None:
            location = self.user_location
            if self.relative_user_location:
                location = self.dim_line_center + location
            # define overridden text location as outside
            self.text_outside = True
        else:
            location = self.default_text_location()

        return location

    def default_text_location(self) -> Vec2:
        """Calculate default text location in UCS based on `self.text_halign`,
        `self.text_valign` and `self.text_outside`

        """
        start = self.dim_line_start
        end = self.dim_line_end
        halign = self.text_halign
        # positions the text above and aligned with the first/second extension line
        if halign in (3, 4):
            # horizontal location
            hdist = self.text_gap + self.text_height / 2.0
            hvec = self.dim_line_vec * hdist
            location = (start if halign == 3 else end) - hvec
            # vertical location
            vdist = self.ext_line_extension + self.dim_text_width / 2.0
            location += Vec2.from_deg_angle(self.ext_line_angle).normalize(
                vdist
            )
        else:
            # relocate outside text to center location
            if self.text_outside:
                halign = 0

            if halign == 0:
                location = self.dim_line_center  # center of dimension line
            else:
                hdist = (
                    self.dim_text_width / 2.0 + self.arrow_size + self.text_gap
                )
                if (
                    halign == 1
                ):  # positions the text next to the first extension line
                    location = start + (self.dim_line_vec * hdist)
                else:  # positions the text next to the second extension line
                    location = end - (self.dim_line_vec * hdist)

            if self.text_outside:  # move text up
                vdist = (
                    self.ext_line_extension
                    + self.text_gap
                    + self.text_height / 2.0
                )
            else:
                # distance from extension line to text midpoint
                vdist = self.text_vertical_distance()
            location += self.dim_line_vec.orthogonal().normalize(vdist)

        return location

    def add_arrows(self) -> Tuple[Vec2, Vec2]:
        """
        Add arrows or ticks to dimension.

        Returns: dimension line connection points

        """
        attribs = {
            "color": self.dim_line_color,
        }
        start = self.dim_line_start
        end = self.dim_line_end
        outside = self.arrows_outside
        arrow1 = not self.suppress_arrow1
        arrow2 = not self.suppress_arrow2
        if self.tick_size > 0.0:  # oblique stroke, but double the size
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
            start_angle = self.dim_line_angle + 180.0
            end_angle = self.dim_line_angle
            if outside:
                start_angle, end_angle = end_angle, start_angle

            if arrow1:
                self.add_blockref(
                    self.arrow1_name,  # type: ignore
                    insert=start,
                    scale=scale,
                    rotation=start_angle,
                    dxfattribs=attribs,
                )  # reverse
            if arrow2:
                self.add_blockref(
                    self.arrow2_name,  # type: ignore
                    insert=end,
                    scale=scale,
                    rotation=end_angle,
                    dxfattribs=attribs,
                )

            if not outside:
                # arrows inside extension lines: adjust connection points for
                # the remaining dimension line
                if arrow1:
                    start = connection_point(
                        self.arrow1_name, start, scale, start_angle  # type: ignore
                    )
                if arrow2:
                    end = connection_point(
                        self.arrow2_name, end, scale, end_angle  # type: ignore
                    )
            else:
                # add additional extension lines to arrows placed outside of
                # dimension extension lines
                self.add_arrow_extension_lines()
        return start, end

    def add_arrow_extension_lines(self):
        """Add extension lines to arrows placed outside of dimension extension
        lines. Called by `self.add_arrows()`.

        """

        def has_arrow_extension(name: str) -> bool:
            return (
                (name is not None)
                and (name in ARROWS)
                and (name not in ARROWS.ORIGIN_ZERO)
            )

        attribs = {
            "color": self.dim_line_color,
        }
        start = self.dim_line_start
        end = self.dim_line_end
        arrow_size = self.arrow_size

        if not self.suppress_arrow1 and has_arrow_extension(self.arrow1_name):
            self.add_line(
                start - self.dim_line_vec * arrow_size,
                start - self.dim_line_vec * (2 * arrow_size),
                dxfattribs=attribs,
            )

        if not self.suppress_arrow2 and has_arrow_extension(self.arrow2_name):
            self.add_line(
                end + self.dim_line_vec * arrow_size,
                end + self.dim_line_vec * (2 * arrow_size),
                dxfattribs=attribs,
            )

    def add_measurement_text(
        self, dim_text: str, pos: Vec2, rotation: float
    ) -> None:
        """Add measurement text to dimension BLOCK.

        Args:
            dim_text: dimension text
            pos: text location
            rotation: text rotation in degrees

        """
        attribs = {
            "color": self.text_color,
        }
        self.add_text(
            dim_text, pos=Vec3(pos), rotation=rotation, dxfattribs=attribs
        )

    def add_dimension_line(self, start: Vec2, end: Vec2) -> None:
        """Add dimension line to dimension BLOCK, adds extension DIMDLE if
        required, and uses DIMSD1 or DIMSD2 to suppress first or second part of
        dimension line. Removes line parts hidden by dimension text.

        Args:
            start: dimension line start
            end: dimension line end

        """
        extension = self.dim_line_vec * self.dim_line_extension
        if self.arrow1_name is None or ARROWS.has_extension_line(
            self.arrow1_name
        ):
            start = start - extension
        if self.arrow2_name is None or ARROWS.has_extension_line(
            self.arrow2_name
        ):
            end = end + extension

        attribs = self.dim_line_attributes()

        if self.suppress_dim1_line or self.suppress_dim2_line:
            # TODO: results not as expected, but good enough
            # center should take into account text location
            center = start.lerp(end)
            if not self.suppress_dim1_line:
                self.add_line(
                    start, center, dxfattribs=attribs, remove_hidden_lines=True
                )
            if not self.suppress_dim2_line:
                self.add_line(
                    center, end, dxfattribs=attribs, remove_hidden_lines=True
                )
        else:
            self.add_line(
                start, end, dxfattribs=attribs, remove_hidden_lines=True
            )

    def extension_line_points(
        self, start: Vec2, end: Vec2, text_above_extline=False
    ) -> Tuple[Vec2, Vec2]:
        """Adjust start and end point of extension line by dimension variables
        DIMEXE, DIMEXO, DIMEXFIX, DIMEXLEN.

        Args:
            start: start point of extension line (measurement point)
            end: end point at dimension line
            text_above_extline: True if text is above and aligned with extension line

        Returns: adjusted start and end point

        """
        if start == end:
            direction = Vec2.from_deg_angle(self.ext_line_angle)
        else:
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

    def add_extension_line(
        self, start: "Vertex", end: "Vertex", linetype: str = None
    ) -> None:
        """Add extension lines from dimension line to measurement point."""
        attribs: Dict[str, Any] = {"color": self.ext_line_color}
        if linetype is not None:
            attribs["linetype"] = linetype

        # lineweight requires DXF R2000 or later
        if self.supports_dxf_r2000:
            attribs["lineweight"] = self.ext_lineweight

        self.add_line(start, end, dxfattribs=attribs)

    def transform_ucs_to_wcs(self) -> None:
        """Transforms dimension definition points into WCS or if required into
        OCS.

        Can not be called in __init__(), because inherited classes may be need
        unmodified values.

        """

        def from_ucs(attr, func):
            point = self.dimension.get_dxf_attrib(attr)
            self.dimension.set_dxf_attrib(attr, func(point))

        from_ucs("defpoint", self.ucs.to_wcs)
        from_ucs("defpoint2", self.ucs.to_wcs)
        from_ucs("defpoint3", self.ucs.to_wcs)
        from_ucs("text_midpoint", self.ucs.to_ocs)
        self.dimension.dxf.angle = self.ucs.to_ocs_angle_deg(
            self.dimension.dxf.angle
        )

        if self.requires_extrusion:
            self.dimension.dxf.extrusion = self.ucs.uz


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


def sort_projected_points(
    points: Iterable["Vertex"], angle: float = 0
) -> List[Vec2]:
    direction = Vec2.from_deg_angle(angle)
    projected_vectors = [(direction.project(Vec2(p)), p) for p in points]
    return [p for projection, p in sorted(projected_vectors)]


def multi_point_linear_dimension(
    layout: "GenericLayoutType",
    base: "Vertex",
    points: Iterable["Vertex"],
    angle: float = 0,
    ucs: "UCS" = None,
    avoid_double_rendering: bool = True,
    dimstyle: str = "EZDXF",
    override: dict = None,
    dxfattribs: dict = None,
    discard=False,
) -> None:
    """Creates multiple DIMENSION entities for each point pair in `points`.
    Measurement points will be sorted by appearance on the dimension line
    vector.

    Args:
        layout: target layout (model space, paper space or block)
        base: base point, any point on the dimension line vector will do
        points: iterable of measurement points
        angle: dimension line rotation in degrees (0=horizontal, 90=vertical)
        ucs: user defined coordinate system
        avoid_double_rendering: removes first extension line and arrow of
            following DIMENSION entity
        dimstyle: dimension style name
        override: dictionary of overridden dimension style attributes
        dxfattribs: DXF attributes for DIMENSION entities
        discard: discard rendering result for friendly CAD applications like
            BricsCAD to get a native and likely better rendering result.
            (does not work with AutoCAD)

    """

    def suppress_arrow1(dimstyle_override) -> bool:
        arrow_name1, arrow_name2 = dimstyle_override.get_arrow_names()
        if (arrow_name1 is None) or (arrow_name1 in CAN_SUPPRESS_ARROW1):
            return True
        else:
            return False

    points = sort_projected_points(points, angle)
    base = Vec2(base)
    override = override or {}
    override["dimtix"] = 1  # do not place measurement text outside
    override["dimtvp"] = 0  # do not place measurement text outside
    override["multi_point_mode"] = True
    # 1 .. move wide text up; 2 .. move wide text down; None .. ignore
    # moving text down, looks best combined with text fill bg: DIMTFILL = 1
    move_wide_text = 1
    _suppress_arrow1 = False
    first_run = True

    for p1, p2 in zip(points[:-1], points[1:]):
        _override = dict(override)
        _override["move_wide_text"] = move_wide_text
        if avoid_double_rendering and not first_run:
            _override["dimse1"] = 1
            _override["suppress_arrow1"] = _suppress_arrow1

        style = layout.add_linear_dim(
            Vec3(base),
            Vec3(p1),
            Vec3(p2),
            angle=angle,
            dimstyle=dimstyle,
            override=_override,
            dxfattribs=dxfattribs,
        )
        if first_run:
            _suppress_arrow1 = suppress_arrow1(style)

        renderer = cast(LinearDimension, style.render(ucs, discard=discard))
        if renderer.is_wide_text:
            # after wide text switch moving direction
            if move_wide_text == 1:
                move_wide_text = 2
            else:
                move_wide_text = 1
        else:  # reset to move text up
            move_wide_text = 1
        first_run = False

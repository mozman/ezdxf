# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import math
from typing import TYPE_CHECKING, Tuple, List, Optional, Dict, Any
from abc import abstractmethod
import logging

from ezdxf.math import (
    Vec2,
    Vec3,
    UCS,
    decdeg2dms,
    ellipse_param_span,
)
from ezdxf.entities import DimStyleOverride, Dimension, DXFEntity
from .dim_base import (
    BaseDimensionRenderer,
    get_required_defpoint,
    format_text,
    apply_dimpost,
    TextBox,
    Tolerance,
    Measurement,
    LengthMeasurement,
    compile_mtext,
)
from ezdxf.render.arrows import ARROWS, arrow_length
from ezdxf.tools.text import is_upside_down_text_angle
from ezdxf.math import intersection_line_line_2d

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType

__all__ = ["AngularDimension", "Angular3PDimension", "ArcLengthDimension"]

logger = logging.getLogger("ezdxf")


def has_required_attributes(entity: DXFEntity, attrib_names: List[str]):
    has = entity.dxf.hasattr
    return all(has(attrib_name) for attrib_name in attrib_names)


GRAD = 200.0 / math.pi
DEG = 180.0 / math.pi


def format_angular_text(
    value: float,
    angle_units: int,
    dimrnd: Optional[float],
    dimdec: Optional[int],
    dimzin: int,
    dimdsep: str,
) -> str:
    def decimal_format(_value: float) -> str:
        return format_text(
            _value,
            dimrnd=dimrnd,
            dimdec=dimdec,
            dimzin=dimzin,
            dimdsep=dimdsep,
        )

    def dms_format(_value: float) -> str:
        d, m, s = decdeg2dms(_value)
        return f"{d:.0f}°{m:.0f}'{decimal_format(s)}\""

    # angular_unit:
    # 0 = Decimal degrees
    # 1 = Degrees/minutes/seconds
    # 2 = Grad
    # 3 = Radians

    text = ""
    if angle_units == 0:
        text = decimal_format(value * DEG) + "°"
    elif angle_units == 1:
        text = dms_format(value * DEG)
    elif angle_units == 2:
        text = decimal_format(value * GRAD) + "g"
    elif angle_units == 3:
        text = decimal_format(value) + "r"
    return text


class AngularTolerance(Tolerance):
    def __init__(
        self,
        dim_style: DimStyleOverride,
        cap_height: float = 1.0,
        width_factor: float = 1.0,
        dim_scale: float = 1.0,
        angle_units: int = 0,
    ):
        super().__init__(dim_style, cap_height, width_factor, dim_scale)
        self.angular_units = angle_units

    def format_text(self, value: float) -> str:
        """Rounding and text formatting of tolerance `value`, removes leading
        and trailing zeros if necessary.

        """
        return format_angular_text(
            value=value,
            angle_units=self.angular_units,
            dimrnd=None,
            dimdec=self.decimal_places,
            dimzin=self.suppress_zeros,
            dimdsep=self.text_decimal_separator,
        )


class AngleMeasurement(Measurement):
    def update(self, raw_measurement_value: float) -> None:
        self.raw_value = raw_measurement_value
        self.value = raw_measurement_value
        self.text = self.text_override(raw_measurement_value)

    def format_text(self, value: float) -> str:
        text = format_angular_text(
            value=value,
            angle_units=self.angle_units,
            dimrnd=None,
            dimdec=self.decimal_places,
            dimzin=self.suppress_zeros,
            dimdsep=self.decimal_separator,
        )
        if self.text_post_process_format:
            text = apply_dimpost(text, self.text_post_process_format)
        return text


class _CurvedDimensionLine(BaseDimensionRenderer):
    def __init__(
        self,
        dimension: Dimension,
        ucs: "UCS" = None,
        override: DimStyleOverride = None,
    ):
        super().__init__(dimension, ucs, override)
        # Common parameters for all sub-classes:
        self.center_of_arc: Vec2 = self.get_center_of_arc()
        self.dim_line_radius: float = self.get_dim_line_radius()
        self.ext1_dir: Vec2 = self.get_ext1_dir()
        self.start_angle_rad: float = self.ext1_dir.angle
        self.ext2_dir: Vec2 = self.get_ext2_dir()
        self.end_angle_rad: float = self.ext2_dir.angle
        self.center_angle_rad = (
            self.start_angle_rad
            + ellipse_param_span(self.start_angle_rad, self.end_angle_rad) / 2.0
        )

        # Additional required parameters but calculated later by sub-classes:
        self.ext1_start = Vec2()  # start of 1st extension line
        self.ext2_start = Vec2()  # start of 2nd extension line
        self.arrows_outside = False

        # Class specific setup:
        self.update_measurement()
        if self.tol.has_limits:
            self.tol.update_limits(self.measurement.value)
        self.setup_text_properties()
        self.setup_text_box()

    def render(self, block: "GenericLayoutType") -> None:
        """Main method to create dimension geometry of basic DXF entities in the
        associated BLOCK layout.

        Args:
            block: target BLOCK for rendering

        """
        super().render(block)
        self.add_extension_lines()
        adjust_start_angle, adjust_end_angle = self.add_arrows()

        measurement = self.measurement
        if measurement.text:
            if self.geometry.supports_dxf_r2000:
                text = compile_mtext(measurement, self.tol)
            else:
                text = measurement.text
            self.add_measurement_text(
                text, measurement.text_location, measurement.text_rotation
            )
            if measurement.has_leader:
                leader1, leader2 = self.get_leader_points()
                self.add_leader(self.dim_midpoint, leader1, leader2)
        # requires the TextBox to remove hidden parts of the dimension line
        self.add_dimension_line(adjust_start_angle, adjust_end_angle)
        self.geometry.add_defpoints(self.get_defpoints())

    @property
    def ocs_center_of_arc(self) -> Vec3:
        return self.geometry.ucs.to_ocs(Vec3(self.center_of_arc))

    @property
    def dim_midpoint(self) -> Vec2:
        """Return the midpoint of the dimension line."""
        return self.center_of_arc + Vec2.from_angle(
            self.center_angle_rad, self.dim_line_radius
        )

    @abstractmethod
    def update_measurement(self) -> None:
        """Setup measurement text."""
        pass

    def setup_text_properties(self) -> None:
        """Setup geometric text properties (location, rotation) and the TextBox
        object.
        """
        # text radial direction = center -> text
        text_radial_dir: Vec2  # text "vertical" direction
        measurement = self.measurement
        radius = self.dim_line_radius + measurement.text_vertical_distance()

        # determine text location:
        if measurement.user_location is None:
            # place text in the center of the dimension line
            text_radial_dir = Vec2.from_angle(self.center_angle_rad)
            measurement.text_location = self.center_of_arc + text_radial_dir * radius
        else:
            # place text at user location:
            measurement.text_location = measurement.user_location
            text_radial_dir = (
                measurement.text_location - self.center_of_arc
            ).normalize()

        # set text "horizontal":
        text_tangential_dir = text_radial_dir.orthogonal(ccw=False)

        # apply text relative shift (ezdxf only feature)
        if measurement.text_shift_h:
            measurement.text_location += text_tangential_dir * measurement.text_shift_h
        if measurement.text_shift_v:
            measurement.text_location += text_radial_dir * measurement.text_shift_v

        # Update final text location in the DIMENSION entity:
        self.dimension.dxf.text_midpoint = measurement.text_location

        # apply user text rotation
        if measurement.user_text_rotation is None:
            rotation = text_tangential_dir.angle_deg
        else:
            rotation = measurement.user_text_rotation

        if not self.geometry.requires_extrusion:
            # todo: extrusion vector (0, 0, -1)?
            # Practically all DIMENSION entities are 2D entities,
            # where OCS == WCS, check WCS text orientation:
            wcs_angle = self.geometry.ucs.to_ocs_angle_deg(rotation)
            if is_upside_down_text_angle(wcs_angle):
                rotation += 180.0  # apply to UCS rotation!
        measurement.text_rotation = rotation

    def setup_text_box(self):
        measurement = self.measurement
        self.geometry.set_text_box(
            TextBox(
                center=measurement.text_location,
                width=self.total_text_width(),
                height=measurement.text_height,
                angle=measurement.text_rotation,
                # Arbitrary choice to reduce the too large gap!
                gap=measurement.text_gap * 0.75,
            )
        )

    @abstractmethod
    def get_ext1_dir(self) -> Vec2:
        """Return the direction of the 1st extension line == start angle."""
        pass

    @abstractmethod
    def get_ext2_dir(self) -> Vec2:
        """Return the direction of the 2nd extension line == end angle."""
        pass

    @abstractmethod
    def get_center_of_arc(self) -> Vec2:
        """Return the center of the arc."""
        pass

    @abstractmethod
    def get_dim_line_radius(self) -> float:
        """Return the distance from the center of the arc to the dimension line
        location
        """
        pass

    # @abstractmethod
    def get_leader_points(self) -> Tuple[Vec2, Vec2]:
        pass

    # @abstractmethod
    def get_defpoints(self) -> List[Vec2]:
        return []

    def add_extension_lines(self) -> None:
        ext_lines = self.extension_lines
        if not ext_lines.suppress1:
            self._add_ext_line(
                self.ext1_start, self.ext1_dir, ext_lines.dxfattribs(1)
            )
        if not ext_lines.suppress2:
            self._add_ext_line(
                self.ext2_start, self.ext2_dir, ext_lines.dxfattribs(2)
            )

    def _add_ext_line(
        self, start: Vec2, direction: Vec2, dxfattribs: Dict[str, Any]
    ) -> None:
        start = start + direction * self.extension_lines.offset
        end = self.center_of_arc + direction * (
            self.dim_line_radius + self.extension_lines.extension_above
        )
        self.add_line(start, end, dxfattribs=dxfattribs)

    def add_arrows(self) -> Tuple[float, float]:
        """Add arrows or ticks to dimension.

        Returns: dimension start- and end angle offsets to adjust the
            dimension line

        """
        arrows = self.arrows
        attribs = arrows.dxfattribs()
        radius = self.dim_line_radius
        if abs(radius) < 1e-12:
            return 0.0, 0.0

        start = self.center_of_arc + self.ext1_dir * radius
        end = self.center_of_arc + self.ext2_dir * radius
        angle1 = self.ext1_dir.orthogonal().angle_deg
        angle2 = self.ext2_dir.orthogonal().angle_deg
        outside = self.arrows_outside
        arrow1 = not arrows.suppress1
        arrow2 = not arrows.suppress2
        start_angle_offset = 0.
        end_angle_offset = 0.
        if arrows.tick_size > 0.:  # oblique stroke, but double the size
            if arrow1:
                self.add_blockref(
                    ARROWS.oblique,
                    insert=start,
                    rotation=angle1,
                    scale=arrows.tick_size * 2.,
                    dxfattribs=attribs,
                )
            if arrow2:
                self.add_blockref(
                    ARROWS.oblique,
                    insert=end,
                    rotation=angle2,
                    scale=arrows.tick_size * 2.,
                    dxfattribs=attribs,
                )
        else:
            scale = arrows.arrow_size
            start_angle = angle1 + 180.
            end_angle = angle2
            if outside:
                start_angle, end_angle = end_angle, start_angle

            if arrow1:
                self.add_blockref(
                    arrows.arrow1_name,
                    insert=start,
                    scale=scale,
                    rotation=start_angle,
                    dxfattribs=attribs,
                )  # reverse
            if arrow2:
                self.add_blockref(
                    arrows.arrow2_name,
                    insert=end,
                    scale=scale,
                    rotation=end_angle,
                    dxfattribs=attribs,
                )
            if not outside:
                # arrows inside extension lines:
                # adjust angles for the remaining dimension line
                if arrow1:
                    start_angle_offset = (
                        arrow_length(arrows.arrow1_name, scale) / radius
                    )
                if arrow2:
                    end_angle_offset = (
                        arrow_length(arrows.arrow2_name, scale) / radius
                    )
        return start_angle_offset, end_angle_offset

    def add_dimension_line(
        self, start_offset: float, end_offset: float
    ) -> None:
        self.add_arc(
            self.center_of_arc,
            self.dim_line_radius,
            self.start_angle_rad + start_offset,
            self.end_angle_rad - end_offset,
            dxfattribs=self.dimension_line.dxfattribs(),
            remove_hidden_lines=True,
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
        attribs = self.measurement.dxfattribs()
        self.add_text(dim_text, pos=pos, rotation=rotation, dxfattribs=attribs)


class _AngularCommonBase(_CurvedDimensionLine):
    def init_tolerance(self, scale: float, measurement: Measurement) -> Tolerance:
        return AngularTolerance(
            self.dim_style,
            cap_height=measurement.text_height,
            width_factor=measurement.text_width_factor,
            dim_scale=scale,
            angle_units=measurement.angle_units,
        )

    def init_measurement(self, color: int, scale: float) -> Measurement:
        return AngleMeasurement(
            self.dim_style, self.default_color, self.dim_scale
        )

    def update_measurement(self) -> None:
        measurement = ellipse_param_span(
            self.start_angle_rad, self.end_angle_rad
        )
        self.measurement.update(measurement)


class AngularDimension(_AngularCommonBase):
    """
    Angular dimension line renderer. The dimension line is defined by two lines.

    Supported render types:

    - default location above
    - default location center
    - user defined location, text aligned with dimension line
    - user defined location horizontal text

    Args:
        dimension: DIMENSION entity
        ucs: user defined coordinate system
        override: dimension style override management object

    """

    # Required defpoints:
    # defpoint = start point of 1st leg (group code 10)
    # defpoint4 = end point of 1st leg (group code 15)
    # defpoint3 = start point of 2nd leg (group code 14)
    # defpoint2 = end point of 2nd leg (group code 13)
    # defpoint5 = location of dimension line (group code 16)

    # unsupported or ignored features (at least by BricsCAD):
    # dimtih: text inside horizontal
    # dimtoh: text outside horizontal
    # dimjust: text position horizontal
    # dimdle: dimline extension

    def __init__(
        self,
        dimension: Dimension,
        ucs: "UCS" = None,
        override: DimStyleOverride = None,
    ):
        self.leg1_start = get_required_defpoint(dimension, "defpoint")
        self.leg1_end = get_required_defpoint(dimension, "defpoint4")
        self.leg2_start = get_required_defpoint(dimension, "defpoint3")
        self.leg2_end = get_required_defpoint(dimension, "defpoint2")
        self.dim_line_location = get_required_defpoint(dimension, "defpoint5")
        super().__init__(dimension, ucs, override)
        # The extension line parameters depending on the location of the
        # dimension line related to the definition point.
        # Detect the extension start point.
        # Which definition point is closer to the dimension line:
        self.ext1_start = detect_closer_defpoint(
            direction=self.ext1_dir,
            base=self.dim_line_location,
            p1=self.leg1_start,
            p2=self.leg1_end,
        )
        self.ext2_start = detect_closer_defpoint(
            direction=self.ext2_dir,
            base=self.dim_line_location,
            p1=self.leg2_start,
            p2=self.leg2_end,
        )

    def transform_ucs_to_wcs(self) -> None:
        """Transforms dimension definition points into WCS or if required into
        OCS.
        """

        def from_ucs(attr, func):
            point = self.dimension.get_dxf_attrib(attr)
            self.dimension.set_dxf_attrib(attr, func(point))

        ucs = self.geometry.ucs
        from_ucs("defpoint", ucs.to_wcs)
        from_ucs("defpoint2", ucs.to_wcs)
        from_ucs("defpoint3", ucs.to_wcs)
        from_ucs("defpoint4", ucs.to_wcs)
        from_ucs("defpoint5", ucs.to_wcs)
        from_ucs("text_midpoint", ucs.to_ocs)
        self.dimension.dxf.angle = ucs.to_ocs_angle_deg(
            self.dimension.dxf.angle
        )

    def get_center_of_arc(self) -> Vec2:
        center = intersection_line_line_2d(
            (self.leg1_start, self.leg1_end),
            (self.leg2_start, self.leg2_end),
        )
        if center is None:
            logger.warning(
                f"Invalid colinear or parallel angle legs found in {self.dimension})"
            )
            # This case can not be created by the GUI in BricsCAD, but DXF
            # files can contain any shit!
            # The interpolation of the end-points is an arbitrary choice and
            # maybe not the best choice!
            center = self.leg1_end.lerp(self.leg2_end)
        return center

    def get_dim_line_radius(self) -> float:
        return (self.dim_line_location - self.center_of_arc).magnitude

    def get_ext1_dir(self) -> Vec2:
        center = self.center_of_arc
        start = (
            self.leg1_end
            if self.leg1_start.isclose(center)
            else self.leg1_start
        )
        return (start - center).normalize()

    def get_ext2_dir(self) -> Vec2:
        center = self.center_of_arc
        start = (
            self.leg2_end
            if self.leg2_start.isclose(center)
            else self.leg2_start
        )
        return (start - center).normalize()


class Angular3PDimension(_AngularCommonBase):
    """
    Angular dimension line renderer. The dimension line is defined by three
    points.

    Supported render types:

    - default location above
    - default location center
    - user defined location, text aligned with dimension line
    - user defined location horizontal text

    Args:
        dimension: DIMENSION entity
        ucs: user defined coordinate system
        override: dimension style override management object

    """

    # Required defpoints:
    # defpoint = location of dimension line (group code 10)
    # defpoint2 = 1st leg (group code 13)
    # defpoint3 = 2nd leg (group code 14)
    # defpoint4 = center of angle (group code 15)

    def __init__(
        self,
        dimension: Dimension,
        ucs: "UCS" = None,
        override: DimStyleOverride = None,
    ):
        self.dim_line_location = get_required_defpoint(dimension, "defpoint")
        self.leg1_start = get_required_defpoint(dimension, "defpoint2")
        self.leg2_start = get_required_defpoint(dimension, "defpoint3")
        self.center_of_arc = get_required_defpoint(dimension, "defpoint4")
        super().__init__(dimension, ucs, override)
        self.ext1_start = self.leg1_start
        self.ext2_start = self.leg2_start

    def transform_ucs_to_wcs(self) -> None:
        """Transforms dimension definition points into WCS or if required into
        OCS.
        """

        def from_ucs(attr, func):
            point = self.dimension.get_dxf_attrib(attr)
            self.dimension.set_dxf_attrib(attr, func(point))

        ucs = self.geometry.ucs
        from_ucs("defpoint", ucs.to_wcs)
        from_ucs("defpoint2", ucs.to_wcs)
        from_ucs("defpoint3", ucs.to_wcs)
        from_ucs("defpoint4", ucs.to_wcs)
        from_ucs("text_midpoint", ucs.to_ocs)
        self.dimension.dxf.angle = ucs.to_ocs_angle_deg(
            self.dimension.dxf.angle
        )

    def get_center_of_arc(self) -> Vec2:
        return self.center_of_arc

    def get_dim_line_radius(self) -> float:
        return (self.dim_line_location - self.center_of_arc).magnitude

    def get_ext1_dir(self) -> Vec2:
        return (self.leg1_start - self.center_of_arc).normalize()

    def get_ext2_dir(self) -> Vec2:
        return (self.leg2_start - self.center_of_arc).normalize()


class ArcLengthDimension(_CurvedDimensionLine):
    """
    Arc length dimension line renderer.
    Requires DXF R2004.

    Supported render types:

    - default location above
    - default location center
    - user defined location, text aligned with dimension line
    - user defined location horizontal text

    Args:
        dimension: DXF entity DIMENSION
        ucs: user defined coordinate system
        override: dimension style override management object

    """

    # Required defpoints:
    # defpoint = location of dimension line (group code 10)
    # defpoint2 = 1st arc point (group code 13)
    # defpoint3 = 2nd arc point (group code 14)
    # defpoint4 = center of arc (group code 15)

    def __init__(
        self,
        dimension: Dimension,
        ucs: "UCS" = None,
        override: DimStyleOverride = None,
    ):
        self.dim_line_location = get_required_defpoint(dimension, "defpoint")
        self.leg1_start = get_required_defpoint(dimension, "defpoint2")
        self.leg2_start = get_required_defpoint(dimension, "defpoint3")
        self.center_of_arc = get_required_defpoint(dimension, "defpoint4")
        self.arc_radius = (self.leg1_start - self.center_of_arc).magnitude
        super().__init__(dimension, ucs, override)
        self.ext1_start = self.leg1_start
        self.ext2_start = self.leg2_start

    def init_measurement(self, color: int, scale: float) -> Measurement:
        return LengthMeasurement(
            self.dim_style, self.default_color, self.dim_scale
        )

    def transform_ucs_to_wcs(self) -> None:
        """Transforms dimension definition points into WCS or if required into
        OCS.
        """

        def from_ucs(attr, func):
            point = self.dimension.get_dxf_attrib(attr)
            self.dimension.set_dxf_attrib(attr, func(point))

        ucs = self.geometry.ucs
        from_ucs("defpoint", ucs.to_wcs)
        from_ucs("defpoint2", ucs.to_wcs)
        from_ucs("defpoint3", ucs.to_wcs)
        from_ucs("defpoint4", ucs.to_wcs)
        from_ucs("text_midpoint", ucs.to_ocs)
        self.dimension.dxf.angle = ucs.to_ocs_angle_deg(
            self.dimension.dxf.angle
        )

    def get_center_of_arc(self) -> Vec2:
        return self.center_of_arc

    def get_dim_line_radius(self) -> float:
        return (self.dim_line_location - self.center_of_arc).magnitude

    def get_ext1_dir(self) -> Vec2:
        return (self.ext1_start - self.center_of_arc).normalize()

    def get_ext2_dir(self) -> Vec2:
        return (self.ext2_start - self.center_of_arc).normalize()

    def update_measurement(self) -> None:
        angle = ellipse_param_span(self.start_angle_rad, self.end_angle_rad)
        arc_length = angle * self.arc_radius * 2.0
        self.measurement.update(arc_length)


def detect_closer_defpoint(
    direction: Vec2, base: Vec2, p1: Vec2, p2: Vec2
) -> Vec2:
    # Calculate the projected distance onto the (normalized) direction vector:
    d0 = direction.dot(base)
    d1 = direction.dot(p1)
    d2 = direction.dot(p2)
    # Which defpoint is closer to the base point (d0)?
    if abs(d1 - d0) <= abs(d2 - d0):
        return p1
    return p2

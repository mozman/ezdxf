# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import math
from typing import TYPE_CHECKING, Tuple, List
from abc import abstractmethod
import logging

from ezdxf.math import (
    Vec2,
    Vec3,
    UCS,
    ConstructionBox,
    decdeg2dms,
    ellipse_param_span,
)

from ezdxf.entities import DimStyleOverride, Dimension, DXFEntity
from ezdxf.graphicsfactory import CreatorInterface
from .dim_base import (
    BaseDimensionRenderer,
    get_required_defpoint,
    format_text,
    apply_dimpost,
)
from ezdxf.math import ConstructionCircle, intersection_line_line_2d

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType

__all__ = ["AngularDimension", "Angular3PDimension", "ArcLengthDimension"]

logger = logging.getLogger("ezdxf")


def has_required_attributes(entity: DXFEntity, attrib_names: List[str]):
    has = entity.dxf.hasattr
    return all(has(attrib_name) for attrib_name in attrib_names)


GRAD = 200.0 / math.pi
DEG = 180.0 / math.pi


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

        # Additional required parameters but calculated later by sub-classes:
        self.ext1_start = Vec2()  # start of 1st extension line
        self.ext2_start = Vec2()  # start of 2nd extension line

    def render(self, block: "GenericLayoutType") -> None:
        """Main method to create dimension geometry of basic DXF entities in the
        associated BLOCK layout.

        Args:
            block: target BLOCK for rendering

        """
        super().render(block)
        self.make_measurement_text()
        self.add_extension_lines()
        self.add_arrows()
        self.add_dimension_line()
        if self.text:
            if self.supports_dxf_r2000:
                text = self.compile_mtext()
            else:
                text = self.text
            self.add_measurement_text(
                text, self.text_location, self.text_rotation
            )
            if self.text_has_leader:
                leader1, leader2 = self.get_leader_points()
                self.add_leader(self.dim_midpoint, leader1, leader2)
        self.add_defpoints(self.get_defpoints())

    @property
    def ocs_center_of_arc(self) -> Vec3:
        return self.ucs.to_ocs(Vec3(self.center_of_arc))

    @property
    def dim_midpoint(self) -> Vec2:
        """Return the midpoint of the dimension line."""
        angle = (self.start_angle_rad + self.end_angle_rad) / 2.0
        return self.center_of_arc + Vec2.from_angle(angle, self.dim_line_radius)

    @abstractmethod
    def make_measurement_text(self) -> None:
        """Setup measurement text and the TextBox object."""
        pass

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
        pass

    def add_extension_lines(self) -> None:
        if not self.suppress_ext1_line:
            self.add_ext1_line()
        if not self.suppress_ext2_line:
            self.add_ext2_line()

    def add_ext1_line(self) -> None:
        pass

    def add_ext2_line(self) -> None:
        pass

    def add_arrows(self) -> None:
        pass

    def add_dimension_line(self) -> None:
        pass

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

    def add_dxf_arc(
        self,
        radius: float,
        start_angle: float,
        end_angle: float,
        dxfattribs: dict = None,
        remove_hidden_lines=False,
    ) -> None:
        """Add a ARC entity to the dimension BLOCK. Removes parts of the arc
        hidden by dimension text if `remove_hidden_lines` is True.
        The center of the arc is always :attr: `self.ocs_center_of_arc`.

        Args:
            radius: radius of arc
            start_angle: start angle in radians
            end_angle: end angle in radians
            dxfattribs: additional or overridden DXF attributes
            remove_hidden_lines: removes parts of the arc hidden by dimension
                text if ``True``

        """

        def add_arc(start: float, end: float) -> None:
            """Add ARC entity to geometry block."""
            self.block.add_arc(  # type: ignore
                center=self.ocs_center_of_arc,
                radius=radius,
                start_angle=math.degrees(ocs_angle(start)),
                end_angle=math.degrees(ocs_angle(end)),
                dxfattribs=dxfattribs,
            )

        assert isinstance(self.block, CreatorInterface)
        ocs_angle = self.ucs.to_ocs_angle_rad
        attribs = self.default_attributes()
        if dxfattribs:
            attribs.update(dxfattribs)
        if remove_hidden_lines:
            assert isinstance(self.text_box, ConstructionBox)
            for start, end in visible_arcs(
                self.center_of_arc,
                radius,
                start_angle,
                end_angle,
                self.text_box,
            ):
                add_arc(start, end)
        else:
            add_arc(start_angle, end_angle)


class _AngularCommonBase(_CurvedDimensionLine):
    def make_measurement_text(self) -> None:
        angle = ellipse_param_span(self.start_angle_rad, self.end_angle_rad)
        self.text = self.text_override(angle)  # -> self.format_text()

    def format_text(self, value: float) -> str:
        def decimal_format(value: float) -> str:
            return format_text(
                value,
                dimrnd=self.text_round,
                dimdec=self.text_decimal_places,
                dimzin=self.text_suppress_zeros,
                dimdsep=self.text_decimal_separator,
            )

        def dms_format(value: float) -> str:
            d, m, s = decdeg2dms(value)
            return f"{d:.0f}°{m:.0f}'{decimal_format(s)}\""

        # 0 = Decimal degrees
        # 1 = Degrees/minutes/seconds
        # 2 = Grad
        # 3 = Radians
        fmt = self.dim_style.get("dimaunit", 0)
        text = ""
        if fmt == 0:
            text = decimal_format(value * DEG) + "°"
        elif fmt == 1:
            text = dms_format(value * DEG)
        elif fmt == 2:
            text = decimal_format(value * GRAD) + "g"
        elif fmt == 3:
            text = decimal_format(value) + "r"
        dimpost = self.text_format
        if dimpost:
            text = apply_dimpost(text, dimpost)
        return text


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

    def get_center_of_arc(self) -> Vec2:
        return self.center_of_arc

    def get_dim_line_radius(self) -> float:
        return (self.dim_line_location - self.center_of_arc).magnitude

    def get_ext1_dir(self) -> Vec2:
        return (self.ext1_start - self.center_of_arc).normalize()

    def get_ext2_dir(self) -> Vec2:
        return (self.ext2_start - self.center_of_arc).normalize()

    def make_measurement_text(self) -> None:
        angle = ellipse_param_span(self.start_angle_rad, self.end_angle_rad)
        arc_length = angle * self.arc_radius * 2.0
        self.text = self.text_override(arc_length)  # -> self.format_text()


def visible_arcs(
    center: Vec2,
    radius: float,
    start_angle: float,
    end_angle: float,
    box: ConstructionBox,
) -> List[Tuple[float, float]]:
    """Returns the visible parts of an arc intersecting with a construction box
    as (start angle, end angle) tuples.

    Args:
        center: center of the arc
        radius: radius of the arc
        start_angle: start angle of arc in radians
        end_angle: end angle of arc in radians
        box: construction box which may intersect the arc

    """
    tau = math.tau
    # normalize angles into range 0 to 2pi
    start_angle = start_angle % tau
    end_angle = end_angle % tau
    intersection_angles: List[float] = []  # angles are in the range 0 to 2pi
    circle = ConstructionCircle(center, radius)
    shift_angles = 0.0
    if start_angle > end_angle:  # angles should not pass 0
        shift_angles = tau
        end_angle += tau

    for line in box.border_lines():
        for intersection_point in circle.intersect_ray(line.ray):
            # is the intersection point in the range of the rectangle border
            if line.bounding_box.inside(intersection_point):
                angle = (
                    (intersection_point - center).angle % tau
                ) + shift_angles
                # is angle in range of the arc
                if start_angle < angle < end_angle:
                    # new angle should be different than the last angle added:
                    if intersection_angles and math.isclose(
                        intersection_angles[-1], angle
                    ):
                        continue
                    intersection_angles.append(angle)
    if len(intersection_angles) == 2:
        # Arc has to intersect the box in exact two locations!
        intersection_angles.sort()
        return [
            (start_angle, intersection_angles[0]),
            (intersection_angles[1], end_angle),
        ]
    else:
        # Ignore cases where the start- or the end point is inside the box.
        # Ignore cases where the box touches the arc in one point.
        return [(start_angle, end_angle)]


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

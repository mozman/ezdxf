# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import math
from typing import TYPE_CHECKING, Tuple, List
from abc import abstractmethod

from ezdxf.math import Vec2, Vec3, UCS, ConstructionBox
from ezdxf.entities.dimstyleoverride import DimStyleOverride
from .dim_base import BaseDimensionRenderer
from ezdxf.math import ConstructionCircle

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType, Dimension, DXFEntity

__all__ = ["AngularDimension", "Angular3PDimension", "ArcLengthDimension"]


def has_required_attributes(entity: "DXFEntity", attrib_names: List[str]):
    has = entity.dxf.hasattr
    return all(has(attrib_name) for attrib_name in attrib_names)


class _CurvedDimensionLine(BaseDimensionRenderer):
    def __init__(
        self,
        dimension: "Dimension",
        ucs: "UCS" = None,
        override: "DimStyleOverride" = None,
    ):
        super().__init__(dimension, ucs, override)
        self.start_angle_rad: float = self.get_start_angle_rad()
        self.end_angle_rad: float = self.get_end_angle_rad()
        self.center_of_arc: Vec2 = self.get_center_of_arc()
        self.ocs_center_of_arc = self.ucs.to_ocs(Vec3(self.center_of_arc))
        self.dim_line_center: Vec2 = self.get_dim_line_center()
        self.dim_line_radius: float = self.get_dim_line_radius()

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
                self.add_leader(self.dim_line_center, leader1, leader2)
        self.add_defpoints(self.get_defpoints())

    @abstractmethod
    def make_measurement_text(self) -> None:
        pass

    def get_dim_line_center(self) -> Vec2:
        angle = (self.start_angle_rad + self.end_angle_rad) / 2.0
        return self.center_of_arc + Vec2.from_angle(angle, self.dim_line_radius)

    @abstractmethod
    def get_start_angle_rad(self) -> float:
        pass

    @abstractmethod
    def get_end_angle_rad(self) -> float:
        pass

    @abstractmethod
    def get_center_of_arc(self) -> Vec2:
        pass

    @abstractmethod
    def get_dim_line_radius(self) -> float:
        pass

    @abstractmethod
    def get_leader_points(self) -> Tuple[Vec2, Vec2]:
        pass

    @abstractmethod
    def get_defpoints(self) -> List[Vec2]:
        pass

    def add_extension_lines(self) -> None:
        if not self.suppress_ext1_line:
            self.add_ext1_line()
        if not self.suppress_ext2_line:
            self.add_ext2_line()

    @abstractmethod
    def add_ext1_line(self) -> None:
        pass

    @abstractmethod
    def add_ext2_line(self) -> None:
        pass

    @abstractmethod
    def add_arrows(self) -> None:
        pass

    @abstractmethod
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
            self.block.add_arc(
                center=self.ocs_center_of_arc,
                radius=radius,
                start_angle=math.degrees(ocs_angle(start)),
                end_angle=math.degrees(ocs_angle(end)),
                dxfattribs=dxfattribs,
            )

        ocs_angle = self.ucs.to_ocs_angle_rad
        attribs = self.default_attributes()
        if dxfattribs:
            attribs.update(dxfattribs)
        if remove_hidden_lines:
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


class AngularDimension(_CurvedDimensionLine):
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


class Angular3PDimension(_CurvedDimensionLine):
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

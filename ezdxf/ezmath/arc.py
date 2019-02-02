# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple

from .vector import Vector
from .circle import ConstructionCircle
from .ucs import OCS, UCS
import math

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, GenericLayoutType
    from ezdxf.eztypes import Arc as DXFArc


class ConstructionArc:
    def __init__(self,
                 center: 'Vertex' = (0, 0),
                 radius: float = 1,
                 start_angle: float = 0,
                 end_angle: float = 360,
                 is_counter_clockwise: bool = True):

        self.center = Vector(center)
        self.radius = radius
        if is_counter_clockwise:
            self.start_angle = start_angle
            self.end_angle = end_angle
        else:
            self.start_angle = end_angle
            self.end_angle = start_angle

    @property
    def start_angle_rad(self) -> float:
        return math.radians(self.start_angle)

    @property
    def end_angle_rad(self) -> float:
        return math.radians(self.end_angle)

    @staticmethod
    def validate_start_and_end_point(start_point: 'Vertex', end_point: 'Vertex') -> Tuple[Vector, Vector]:
        start_point = Vector(start_point)
        if start_point.z != 0:
            raise ValueError("z-axis of start point has to be 0.")
        end_point = Vector(end_point)
        if end_point.z != 0:
            raise ValueError("z-axis of end point has to be 0.")
        if start_point == end_point:
            raise ValueError("start- and end point has to be different points.")
        return start_point, end_point

    @classmethod
    def from_2p_angle(cls, start_point: 'Vertex', end_point: 'Vertex', angle: float, ccw: bool = True) -> 'ConstructionArc':
        """
        Create arc from two points and enclosing angle. Additional precondition: arc goes by default in counter
        clockwise orientation from start_point to end_point, can be changed by ccw=False.
        Z-axis of start_point and end_point has to be 0 if given.

        Args:
            start_point: start point (x, y [,z]) as args accepted by Vector()
            end_point: end point (x, y [,z]) as args accepted by Vector()
            angle: enclosing angle in degrees
            ccw: counter clockwise direction True/False

        """
        start_point, end_point = cls.validate_start_and_end_point(start_point, end_point)
        angle = math.radians(angle)
        if angle == 0:
            raise ValueError("angle can not be 0.")
        if ccw is False:
            start_point, end_point = end_point, start_point
        alpha2 = angle / 2.
        distance = end_point.distance(start_point)
        distance2 = distance / 2.
        radius = distance2 / math.sin(alpha2)
        height = distance2 / math.tan(alpha2)
        mid_point = end_point.lerp(start_point, factor=.5)

        distance_vector = end_point - start_point
        height_vector = distance_vector.orthogonal().normalize(height)
        center = mid_point + height_vector

        return ConstructionArc(
            center=center,
            radius=radius,
            start_angle=(start_point - center).angle_deg,
            end_angle=(end_point - center).angle_deg,
            is_counter_clockwise=True,
        )

    @classmethod
    def from_2p_radius(cls, start_point: 'Vertex', end_point: 'Vertex', radius: float, ccw: bool = True,
                       center_is_left: bool = True) -> 'ConstructionArc':
        """
        Create arc from two points and arc radius. Additional precondition: arc goes by default in counter clockwise
        orientation from start_point to end_point can be changed by ccw=False.
        Z-axis of start_point and end_point has to be 0 if given.

        The parameter *center_is_left* defines if the center of the arc is left or right of the line *start point* ->
        *end point*. Parameter ccw=False swaps start- and end point, which inverts the meaning of center_is_left.

        Args:
            start_point: start point (x, y [,z]) as args accepted by Vector()
            end_point: end point (x, y [,z]) as args accepted by Vector()
            radius: arc radius
            ccw: counter clockwise direction True/False
            center_is_left: center point of arc is left of line SP->EP if True, else on the right side of this line

        """
        start_point, end_point = cls.validate_start_and_end_point(start_point, end_point)
        radius = float(radius)
        if radius <= 0:
            raise ValueError("radius has to be > 0.")
        if ccw is False:
            start_point, end_point = end_point, start_point

        mid_point = end_point.lerp(start_point, factor=.5)
        distance = end_point.distance(start_point)
        distance2 = distance / 2.
        height = math.sqrt(radius ** 2 - distance2 ** 2)
        center = mid_point + (end_point - start_point).orthogonal(ccw=center_is_left).normalize(height)

        return ConstructionArc(
            center=center,
            radius=radius,
            start_angle=(start_point - center).angle_deg,
            end_angle=(end_point - center).angle_deg,
            is_counter_clockwise=True,
        )

    @classmethod
    def from_3p(cls, start_point: 'Vertex', end_point: 'Vertex', def_point: 'Vertex', ccw: bool = True) -> 'ConstructionArc':
        """
        Create arc from three points. Additional precondition: arc goes in counter clockwise
        orientation from start_point to end_point. Z-axis of start_point, end_point and def_point has to be 0 if given.

        Args:
            start_point: start point (x, y [,z])  as args accepted by Vector()
            end_point: end point (x, y [,z]) as args accepted by Vector()
            def_point: additional definition point as (x, y [,z]) tuple
            ccw: counter clockwise direction True/False

        """
        start_point, end_point = cls.validate_start_and_end_point(start_point, end_point)
        def_point = Vector(def_point)
        if def_point.z != 0:
            raise ValueError("z-axis of def point has to be 0.")
        if def_point == start_point or def_point == end_point:
            raise ValueError("def point has to be different to start- and end point")

        circle = ConstructionCircle.from_3p(start_point, end_point, def_point)
        center = Vector(circle.center)
        return ConstructionArc(
            center=center,
            radius=circle.radius,
            start_angle=(start_point - center).angle_deg,
            end_angle=(end_point - center).angle_deg,
            is_counter_clockwise=ccw,
        )

    def add_to_layout(self, layout: 'GenericLayoutType', ucs: UCS = None, dxfattribs: dict = None) -> 'DXFArc':
        """
        Add arc as DXF entity to a layout.

        Supports 3D arcs by using an UCS. An ConstructionArc is always defined in the xy-plane, but by using an arbitrary UCS, the
        arc can be placed in 3D space, automatically OCS transformation included.

        Args:
            layout: destination layout (model space, paper space or block)
            ucs: arc properties transformation from ucs to ocs
            dxfattribs: usual DXF attributes supported by ARC

        Returns: DXF ConstructionArc() object

        """

        def ocs_angle(angle):
            point = self.center + Vector.from_deg_angle(angle)
            wcs_point = ucs.to_wcs(point)
            ocs_point = ocs.from_wcs(wcs_point)
            angle = (ocs_point - ocs_center).angle_deg
            return angle

        if ucs is not None:
            if dxfattribs is None:
                dxfattribs = {}
            dxfattribs['extrusion'] = ucs.uz
            ocs = OCS(ucs.uz)
            wcs_center = ucs.to_wcs(self.center)
            ocs_center = ocs.from_wcs(wcs_center)
            arc = self.__class__(radius=self.radius)
            arc.center = ocs_center
            arc.start_angle = ocs_angle(self.start_angle)
            arc.end_angle = ocs_angle(self.end_angle)
        else:
            arc = self

        return layout.add_arc(
            center=arc.center,
            radius=arc.radius,
            start_angle=arc.start_angle,
            end_angle=arc.end_angle,
            dxfattribs=dxfattribs,
        )

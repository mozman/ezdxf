# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

from .vector import Vector
from .circle import Circle
import math


class Arc(object):
    def __init__(self, center=(0, 0), radius=1, start_angle=0, end_angle=360, is_counter_clockwise=True):
        self.center = Vector(center)
        self.radius = radius
        if is_counter_clockwise:
            self.start_angle = start_angle
            self.end_angle = end_angle
        else:
            self.start_angle = end_angle
            self.end_angle = start_angle

    @property
    def start_angle_rad(self):
        return math.radians(self.start_angle)

    @property
    def end_angle_rad(self):
        return math.radians(self.end_angle)

    @staticmethod
    def from_2p_angle(start_point, end_point, angle):
        """
        Create arc from two points and enclosing angle. Additional precondition: arc goes in counter clockwise
        orientation from start_point to end_point. Z-axis of start_point and end_point has to be 0 if given.

        Args:
            start_point: start point as (x, y [,z]) tuple
            end_point: end point as (x, y [,z]) tuple
            angle: enclosing angle in degrees

        Returns: Arc()

        """
        start_point = Vector(start_point)
        if start_point.z != 0:
            raise ValueError("z-axis of start point has to be 0.")
        end_point = Vector(end_point)
        if end_point.z != 0:
            raise ValueError("z-axis of end point has to be 0.")
        angle = math.radians(angle)
        if angle == 0:
            raise ValueError("angle can not be 0.")

        alpha2 = angle / 2.
        distance = end_point.distance(start_point)
        distance2 = distance / 2.
        radius = distance2 / math.sin(alpha2)
        height = distance2 / math.tan(alpha2)
        mid_point = end_point.lerp(start_point, factor=.5)

        distance_vector = end_point - start_point
        height_vector = distance_vector.orthogonal().normalize(height)
        center = mid_point + height_vector

        start_angle = (start_point - center).angle_deg
        end_angle = (end_point - center).angle_deg
        return Arc(center=center, radius=radius, start_angle=start_angle, end_angle=end_angle,
                   is_counter_clockwise=True)

    @staticmethod
    def from_3p(start_point, end_point, def_point):
        """
        Create arc from three points. Additional precondition: arc goes in counter clockwise
        orientation from start_point to end_point. Z-axis of start_point, end_point and def_point has to be 0 if given.

        Args:
            start_point: start point as (x, y [,z]) tuple
            end_point: end point as (x, y [,z]) tuple
            def_point: additional definition point as (x, y [,z]) tuple

        Returns: Arc()

        """
        start_point = Vector(start_point)
        if start_point.z != 0:
            raise ValueError("z-axis of start point has to be 0.")
        end_point = Vector(end_point)
        if end_point.z != 0:
            raise ValueError("z-axis of end point has to be 0.")
        def_point = Vector(def_point)
        if def_point.z != 0:
            raise ValueError("z-axis of def point has to be 0.")

        circle = Circle.from_3p(start_point, end_point, def_point)
        center = Vector(circle.center_point)
        return Arc(
            center=center,
            radius=circle.radius,
            start_angle=(start_point - center).angle_deg,
            end_angle=(end_point - center).angle_deg,
            is_counter_clockwise=True,
        )

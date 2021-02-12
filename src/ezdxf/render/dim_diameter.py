# Created: 30.01.2020
# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.math import Vec2, UCS
from ezdxf.entities.dimstyleoverride import DimStyleOverride

from .dim_radius import RadiusDimension, add_center_mark

if TYPE_CHECKING:
    from ezdxf.eztypes import Dimension


class DiameterDimension(RadiusDimension):
    """
    Diameter dimension line renderer.

    Supported render types:
    - default location inside, text aligned with diameter dimension line
    - default location inside horizontal text
    - default location outside, text aligned with diameter dimension line
    - default location outside horizontal text
    - user defined location, text aligned with diameter dimension line
    - user defined location horizontal text

    Args:
        dimension: DXF entity DIMENSION
        ucs: user defined coordinate system
        override: dimension style override management object

    """

    def _center(self):
        return Vec2(self.dimension.dxf.defpoint).lerp(self.dimension.dxf.defpoint4)

    def __init__(self, dimension: 'Dimension', ucs: 'UCS' = None, override: 'DimStyleOverride' = None):
        # Diameter dimension has the same styles for inside text as radius dimension, except for the
        # measurement text
        super().__init__(dimension, ucs, override)
        self.point_on_circle2 = Vec2(self.dimension.dxf.defpoint)

        # escape diameter sign
        self.text = self.text.replace(self.text_prefix, '%%c')
        if self.dim_limits:
            self.tol_text_lower = self.tol_text_lower.replace(self.text_prefix, '%%c')

    def get_default_text_location(self) -> Vec2:
        """ Returns default text midpoint based on `self.text_valign` and `self.text_outside` """
        if self.text_outside and self.text_outside_horizontal:
            return super().get_default_text_location()

        text_direction = Vec2.from_deg_angle(self.text_rotation)
        vertical_direction = text_direction.orthogonal(ccw=True)
        vertical_distance = self.text_vertical_distance()
        if self.text_inside:
            text_midpoint = self.center
        else:
            hdist = self.dim_text_width / 2. + self.arrow_size + self.text_gap
            text_midpoint = self.point_on_circle + (self.dim_line_vec * hdist)
        return text_midpoint + (vertical_direction * vertical_distance)

    def _add_arrow_1(self, rotate=False):
        if not self.suppress_arrow1:
            return self.add_arrow(self.point_on_circle, rotate=rotate)
        else:
            return self.point_on_circle

    def _add_arrow_2(self, rotate=True):
        if not self.suppress_arrow2:
            return self.add_arrow(self.point_on_circle2, rotate=rotate)
        else:
            return self.point_on_circle2

    def render_default_location(self) -> None:
        """ Create dimension geometry at the default dimension line locations. """

        if self.text_outside:
            connection_point1 = self._add_arrow_1(rotate=True)
            if self.outside_text_force_dimline:
                self.add_diameter_dim_line(connection_point1, self._add_arrow_2())
            else:
                add_center_mark(self)
            if self.text_outside_horizontal:
                self.add_horiz_ext_line_default(connection_point1)
            else:
                self.add_radial_ext_line_default(connection_point1)
        else:
            connection_point1 = self._add_arrow_1(rotate=False)
            if self.text_movement_rule == 1:
                # move text, add leader -> dimline from text to point on circle
                self.add_radial_dim_line_from_text(self.center, connection_point1)
                add_center_mark(self)
            else:
                # dimline from center to point on circle
                self.add_diameter_dim_line(connection_point1, self._add_arrow_2())

    def render_user_location(self) -> None:
        """ Create dimension geometry at user defined dimension locations. """
        preserve_outside = self.text_outside
        leader = self.text_movement_rule != 2
        if not leader:
            self.text_outside = False  # render dimension line like text inside
        # add arrow symbol (block references)
        connection_point1 = self._add_arrow_1(rotate=self.text_outside)

        if self.text_outside:
            if self.outside_text_force_dimline:
                self.add_radial_dim_line(self.point_on_circle)
            else:
                add_center_mark(self)
            if self.text_outside_horizontal:
                self.add_horiz_ext_line_user(connection_point1)
            else:
                self.add_radial_ext_line_user(connection_point1)
        else:
            if self.text_inside_horizontal:
                self.add_horiz_ext_line_user(connection_point1)
            else:
                if self.text_movement_rule == 2:  # move text, no leader!
                    # dimline across the circle
                    connection_point2 = self._add_arrow_2(rotate=True)
                    self.add_line(connection_point1, connection_point2, remove_hidden_lines=True)
                else:
                    # move text, add leader -> dimline from text to point on circle
                    self.add_radial_dim_line_from_text(self.user_location, connection_point1)
                    add_center_mark(self)

        self.text_outside = preserve_outside

    def add_diameter_dim_line(self, start: Vec2, end: Vec2) -> None:
        """  Add diameter dimension line. """
        attribs = self.dim_line_attributes()
        self.add_line(start, end, dxfattribs=attribs, remove_hidden_lines=True)

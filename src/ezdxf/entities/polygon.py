# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import Sequence, Optional
import abc
import copy

from ezdxf.lldxf import const
from ezdxf.lldxf.tags import Tags
from ezdxf import colors
from ezdxf.tools import pattern
from ezdxf.math import Vec3, Matrix44
from ezdxf.math.transformtools import OCSTransform
from .boundary_paths import BoundaryPaths
from .dxfns import SubclassProcessor, DXFNamespace
from .dxfgfx import DXFGraphic
from .gradient import Gradient
from .pattern import Pattern, PatternLine

RGB = colors.RGB

__all__ = ["BasePolygon"]

PATH_CODES = {
    10,
    11,
    12,
    13,
    40,
    42,
    50,
    51,
    42,
    72,
    73,
    74,
    92,
    93,
    94,
    95,
    96,
    97,
    330,
}
PATTERN_DEFINITION_LINE_CODES = {53, 43, 44, 45, 46, 79, 49}


class BasePolygon(DXFGraphic):
    """Base class for the HATCH and the MPOLYGON entity."""

    LOAD_GROUP_CODES = {}

    def __init__(self):
        super().__init__()
        self.paths = BoundaryPaths()
        self.pattern: Optional[Pattern] = None
        self.gradient: Optional[Gradient] = None
        self.seeds = []  # not supported/exported by MPOLYGON

    def _copy_data(self, entity: "BasePolygon") -> None:
        """Copy paths, pattern, gradient, seeds."""
        entity.paths = copy.deepcopy(self.paths)
        entity.pattern = copy.deepcopy(self.pattern)
        entity.gradient = copy.deepcopy(self.gradient)
        entity.seeds = copy.deepcopy(self.seeds)

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> DXFNamespace:
        dxf = super().load_dxf_attribs(processor)
        if processor:
            # Copy without subclass marker:
            tags = Tags(processor.subclasses[2][1:])
            # Removes boundary path data from tags:
            tags = self.load_paths(tags)
            # Removes gradient data from tags:
            tags = self.load_gradient(tags)
            # Removes pattern from tags:
            tags = self.load_pattern(tags)
            # Removes seeds from tags:
            tags = self.load_seeds(tags)

            # Load HATCH DXF attributes from remaining tags:
            processor.fast_load_dxfattribs(
                dxf, self.LOAD_GROUP_CODES, subclass=tags, recover=True
            )
        return dxf

    def load_paths(self, tags: Tags) -> Tags:
        # Find first group code 91 = count of loops, Spline data also contains
        # group code 91!
        try:
            start_index = tags.tag_index(91)
        except const.DXFValueError:
            raise const.DXFStructureError(
                f"{self.dxftype()}: Missing required DXF tag 'Number of "
                f"boundary paths (loops)' (code=91)."
            )

        path_tags = tags.collect_consecutive_tags(
            PATH_CODES, start=start_index + 1
        )
        if len(path_tags):
            self.paths = BoundaryPaths.load_tags(path_tags)
        end_index = start_index + len(path_tags) + 1
        del tags[start_index:end_index]
        return tags

    def load_pattern(self, tags: Tags) -> Tags:
        try:
            # Group code 78 = Number of patter definition lines
            index = tags.tag_index(78)
        except const.DXFValueError:
            # No pattern definition lines found.
            return tags

        pattern_tags = tags.collect_consecutive_tags(
            PATTERN_DEFINITION_LINE_CODES, start=index + 1
        )
        self.pattern = Pattern.load_tags(pattern_tags)

        # Delete pattern data including length tag 78
        del tags[index: index + len(pattern_tags) + 1]
        return tags

    def load_gradient(self, tags: Tags) -> Tags:
        try:
            index = tags.tag_index(450)
        except const.DXFValueError:
            # No gradient data present
            return tags

        # Gradient data is always at the end of the AcDbHatch subclass.
        self.gradient = Gradient.load_tags(tags[index:])
        # Remove gradient data from tags
        del tags[index:]
        return tags

    def load_seeds(self, tags: Tags) -> Tags:
        return tags

    @property
    def has_solid_fill(self) -> bool:
        """``True`` if entity has a solid fill. (read only)"""
        return bool(self.dxf.solid_fill)

    @property
    def has_pattern_fill(self) -> bool:
        """``True`` if entity has a pattern fill. (read only)"""
        return not bool(self.dxf.solid_fill)

    @property
    def has_gradient_data(self) -> bool:
        """``True`` if entity has a gradient fill. A hatch with gradient fill
        has also a solid fill. (read only)
        """
        return bool(self.gradient)

    @property
    def bgcolor(self) -> Optional[RGB]:
        """
        Set pattern fill background color as (r, g, b)-tuple, rgb values
        in the range [0, 255] (read/write/del)

        usage::

            r, g, b = entity.bgcolor  # get pattern fill background color
            entity.bgcolor = (10, 20, 30)  # set pattern fill background color
            del entity.bgcolor  # delete pattern fill background color

        """
        try:
            xdata_bgcolor = self.get_xdata("HATCHBACKGROUNDCOLOR")
        except const.DXFValueError:
            return None
        color = xdata_bgcolor.get_first_value(1071, 0)
        return colors.int2rgb(color)

    @bgcolor.setter
    def bgcolor(self, rgb: RGB) -> None:
        color_value = (
            colors.rgb2int(rgb) | -0b111110000000000000000000000000
        )  # it's magic

        self.discard_xdata("HATCHBACKGROUNDCOLOR")
        self.set_xdata("HATCHBACKGROUNDCOLOR", [(1071, color_value)])

    @bgcolor.deleter
    def bgcolor(self) -> None:
        self.discard_xdata("HATCHBACKGROUNDCOLOR")

    def set_gradient(
        self,
        color1: RGB = (0, 0, 0),
        color2: RGB = (255, 255, 255),
        rotation: float = 0.0,
        centered: float = 0.0,
        one_color: int = 0,
        tint: float = 0.0,
        name: str = "LINEAR",
    ) -> None:
        """Set :class:`Hatch` and :class:`MPolygon` to gradient fill mode and
        removes all pattern fill related data. Gradient support requires
        DXF R2004+.
        A gradient filled hatch is also a solid filled hatch.

        Valid gradient type names are:

            - ``'LINEAR'``
            - ``'CYLINDER'``
            - ``'INVCYLINDER'``
            - ``'SPHERICAL'``
            - ``'INVSPHERICAL'``
            - ``'HEMISPHERICAL'``
            - ``'INVHEMISPHERICAL'``
            - ``'CURVED'``
            - ``'INVCURVED'``

        Args:
            color1: (r, g, b)-tuple for first color, rgb values as int in
                the range [0, 255]
            color2: (r, g, b)-tuple for second color, rgb values as int in
                the range [0, 255]
            rotation: rotation angle in degrees
            centered: determines whether the gradient is centered or not
            one_color: 1 for gradient from `color1` to tinted `color1`
            tint: determines the tinted target `color1` for a one color
                gradient. (valid range 0.0 to 1.0)
            name: name of gradient type, default "LINEAR"

        """
        if self.doc is not None and self.doc.dxfversion < const.DXF2004:
            raise const.DXFVersionError("Gradient support requires DXF R2004")
        if name and name not in const.GRADIENT_TYPES:
            raise const.DXFValueError(f"Invalid gradient type name: {name}")

        self.pattern = None
        self.dxf.solid_fill = 1
        self.dxf.pattern_name = "SOLID"
        self.dxf.pattern_type = const.HATCH_TYPE_PREDEFINED

        gradient = Gradient()
        gradient.color1 = color1
        gradient.color2 = color2
        gradient.one_color = one_color
        gradient.rotation = rotation
        gradient.centered = centered
        gradient.tint = tint
        gradient.name = name
        self.gradient = gradient

    def set_pattern_fill(
        self,
        name: str,
        color: int = 7,
        angle: float = 0.0,
        scale: float = 1.0,
        double: int = 0,
        style: int = 1,
        pattern_type: int = 1,
        definition=None,
    ) -> None:
        """Set :class:`Hatch` and :class:`MPolygon` to pattern fill mode.
        Removes all gradient related data.
        The pattern definition should be designed for scaling
        factor 1. Predefined hatch pattern like "ANSI33" are scaled according
        to the HEADER variable $MEASUREMENT for ISO measurement (m, cm, ... ),
        or imperial units (in, ft, ...), this replicates the behavior of
        BricsCAD.

        Args:
            name: pattern name as string
            color: pattern color as :ref:`ACI`
            angle: angle of pattern fill in degrees
            scale: pattern scaling as float
            double: double size flag
            style: hatch style (0 = normal; 1 = outer; 2 = ignore)
            pattern_type: pattern type (0 = user-defined;
                1 = predefined; 2 = custom)
            definition: list of definition lines and a definition line is a
                4-tuple [angle, base_point, offset, dash_length_items],
                see :meth:`set_pattern_definition`

        """
        self.gradient = None
        self.dxf.solid_fill = 0
        self.dxf.pattern_name = name
        self.dxf.color = color
        self.dxf.pattern_scale = float(scale)
        self.dxf.pattern_angle = float(angle)
        self.dxf.pattern_double = int(double)
        self.dxf.hatch_style = style
        self.dxf.pattern_type = pattern_type

        if definition is None:
            measurement = 1
            if self.doc:
                measurement = self.doc.header.get("$MEASUREMENT", measurement)
            predefined_pattern = (
                pattern.ISO_PATTERN if measurement else pattern.IMPERIAL_PATTERN
            )
            definition = predefined_pattern.get(
                name, predefined_pattern["ANSI31"]
            )
        self.set_pattern_definition(
            definition,
            factor=self.dxf.pattern_scale,
            angle=self.dxf.pattern_angle,
        )

    def set_pattern_definition(
        self, lines: Sequence, factor: float = 1, angle: float = 0
    ) -> None:
        """Setup pattern definition by a list of definition lines and  a
        definition line is a 4-tuple (angle, base_point, offset, dash_length_items),
        the pattern definition should be designed for scaling factor 1 and
        angle 0.

            - angle: line angle in degrees
            - base-point: 2-tuple (x, y)
            - offset: 2-tuple (dx, dy)
            - dash_length_items: list of dash items (item > 0 is a line,
              item < 0 is a gap and item == 0.0 is a point)

        Args:
            lines: list of definition lines
            factor: pattern scaling factor
            angle: rotation angle in degrees

        """
        if factor != 1 or angle:
            lines = pattern.scale_pattern(lines, factor=factor, angle=angle)
        self.pattern = Pattern(
            [PatternLine(line[0], line[1], line[2], line[3]) for line in lines]
        )

    def set_pattern_scale(self, scale: float) -> None:
        """Set scaling of pattern definition to `scale`.

        Starts always from the original base scaling, :code:`set_pattern_scale(1)`
        reset the pattern scaling to the original appearance as defined by the
        pattern designer, but only if the the pattern attribute
        :attr:`dxf.pattern_scale` represents the actual scaling, it is not
        possible to recreate the original pattern scaling from the pattern
        definition itself.

        Args:
            scale: pattern scaling factor

        """
        if not self.has_pattern_fill:
            return
        dxf = self.dxf
        self.pattern.scale(factor=1.0 / dxf.pattern_scale * scale)
        dxf.pattern_scale = scale

    def set_pattern_angle(self, angle: float) -> None:
        """Set rotation of pattern definition to `angle` in degrees.

        Starts always from the original base rotation 0,
        :code:`set_pattern_angle(0)` reset the pattern rotation to the original
        appearance as defined by the pattern designer, but only if the the
        pattern attribute :attr:`dxf.pattern_angle` represents the actual
        rotation, it is not possible to recreate the original rotation from the
        pattern definition itself.

        Args:
            angle: rotation angle in degrees

        """
        if not self.has_pattern_fill:
            return
        dxf = self.dxf
        self.pattern.scale(angle=angle - dxf.pattern_angle)
        dxf.pattern_angle = angle % 360.0

    def transform(self, m: "Matrix44") -> "BasePolygon":
        """Transform entity by transformation matrix `m` inplace."""
        dxf = self.dxf
        ocs = OCSTransform(dxf.extrusion, m)

        elevation = Vec3(dxf.elevation).z
        self.paths.transform(ocs, elevation=elevation)
        dxf.elevation = ocs.transform_vertex(Vec3(0, 0, elevation)).replace(
            x=0, y=0
        )
        dxf.extrusion = ocs.new_extrusion
        # todo scale pattern
        return self

    @abc.abstractmethod
    def set_solid_fill(self, color: int = 7, style: int = 1, rgb: "RGB" = None):
        ...

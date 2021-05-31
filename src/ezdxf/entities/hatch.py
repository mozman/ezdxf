# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    List,
    Tuple,
    Sequence,
    Iterable,
    Optional,
)
import math
import copy

from ezdxf.lldxf import const
from ezdxf.lldxf import validator
from ezdxf.lldxf.attributes import (
    DXFAttr,
    DXFAttributes,
    DefSubclass,
    XType,
    RETURN_DEFAULT,
    group_code_mapping,
)
from ezdxf.lldxf.tags import Tags, group_tags
from ezdxf import colors as clr
from ezdxf.tools import pattern
from ezdxf.math import (
    Vec3,
    Vec2,
    Matrix44,
    NULLVEC,
    Z_AXIS,
)
from ezdxf.math.transformtools import OCSTransform
from .boundary_paths import TPath, BoundaryPaths
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter,
        DXFNamespace,
        Drawing,
        RGB,
        DXFEntity,
        Vertex,
    )

__all__ = [
    "BasePolygon",
    "Hatch",
    "Gradient",
    "Pattern",
    "PatternLine",
]

GRADIENT_CODES = {450, 451, 452, 453, 460, 461, 462, 463, 470, 421, 63}
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

    def _copy_data(self, entity: "Hatch") -> None:
        """Copy paths, pattern, gradient, seeds."""
        entity.paths = copy.deepcopy(self.paths)
        entity.pattern = copy.deepcopy(self.pattern)
        entity.gradient = copy.deepcopy(self.gradient)
        entity.seeds = copy.deepcopy(self.seeds)

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
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
        """``True`` if hatch has a solid fill. (read only)"""
        return bool(self.dxf.solid_fill)

    @property
    def has_pattern_fill(self) -> bool:
        """``True`` if hatch has a pattern fill. (read only)"""
        return not bool(self.dxf.solid_fill)

    @property
    def has_gradient_data(self) -> bool:
        """``True`` if hatch has a gradient fill. A hatch with gradient fill
        has also a solid fill. (read only)
        """
        return bool(self.gradient)

    @property
    def bgcolor(self) -> Optional["RGB"]:
        """
        Property background color as (r, g, b)-tuple, rgb values in the
        range [0, 255] (read/write/del)

        usage::

            color = hatch.bgcolor  # get background color as (r, g, b) tuple
            hatch.bgcolor = (10, 20, 30)  # set background color
            del hatch.bgcolor  # delete background color

        """
        try:
            xdata_bgcolor = self.get_xdata("HATCHBACKGROUNDCOLOR")
        except const.DXFValueError:
            return None
        color = xdata_bgcolor.get_first_value(1071, 0)
        return clr.int2rgb(color)

    @bgcolor.setter
    def bgcolor(self, rgb: "RGB") -> None:
        color_value = (
            clr.rgb2int(rgb) | -0b111110000000000000000000000000
        )  # it's magic

        self.discard_xdata("HATCHBACKGROUNDCOLOR")
        self.set_xdata("HATCHBACKGROUNDCOLOR", [(1071, color_value)])

    @bgcolor.deleter
    def bgcolor(self) -> None:
        self.discard_xdata("HATCHBACKGROUNDCOLOR")

    def set_solid_fill(self, color: int = 7, style: int = 1, rgb: "RGB" = None):
        """Set :class:`Hatch` to solid fill mode and removes all gradient and
        pattern fill related data.

        Args:
            color: :ref:`ACI`, (0 = BYBLOCK; 256 = BYLAYER)
            style: hatch style (0 = normal; 1 = outer; 2 = ignore)
            rgb: true color value as (r, g, b)-tuple - has higher priority
                than `color`. True color support requires DXF R2000.

        """
        self.gradient = None
        if self.has_pattern_fill:
            self.pattern = None
            self.dxf.solid_fill = 1

        # If a true color value is present, the color value is ignored by AutoCAD
        self.dxf.color = color
        self.dxf.hatch_style = style
        self.dxf.pattern_name = "SOLID"
        self.dxf.pattern_type = const.HATCH_TYPE_PREDEFINED
        if rgb is not None:
            self.rgb: "RGB" = rgb

    def set_gradient(
        self,
        color1: "RGB" = (0, 0, 0),
        color2: "RGB" = (255, 255, 255),
        rotation: float = 0.0,
        centered: float = 0.0,
        one_color: int = 0,
        tint: float = 0.0,
        name: str = "LINEAR",
    ) -> None:
        """Set :class:`Hatch` to gradient fill mode and removes all pattern
        fill related data. Gradient support requires DXF DXF R2004.
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
        if name not in const.GRADIENT_TYPES:
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
        """Set :class:`Hatch` to pattern fill mode. Removes all gradient
        related data. The pattern definition should be designed for scaling
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
        """Setup hatch patten definition by a list of definition lines and  a
        definition line is a 4-tuple [angle, base_point, offset, dash_length_items],
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


acdb_hatch = DefSubclass(
    "AcDbHatch",
    {
        # This subclass can also represent a MPolygon, whatever this is, never seen
        # such a MPolygon in the wild.
        # x- and y-axis always equal 0, z-axis represents the elevation:
        "elevation": DXFAttr(10, xtype=XType.point3d, default=NULLVEC),
        "extrusion": DXFAttr(
            210,
            xtype=XType.point3d,
            default=Z_AXIS,
            validator=validator.is_not_null_vector,
            fixer=RETURN_DEFAULT,
        ),
        # Hatch pattern name:
        "pattern_name": DXFAttr(2, default="SOLID"),
        # HATCH: Solid fill flag:
        # 0 = pattern fill
        # 1 = solid fill
        "solid_fill": DXFAttr(
            70,
            default=1,
            validator=validator.is_integer_bool,
            fixer=RETURN_DEFAULT,
        ),
        # HATCH: associativity flag
        # 0 = non-associative
        # 1 = associative
        "associative": DXFAttr(
            71,
            default=0,
            validator=validator.is_integer_bool,
            fixer=RETURN_DEFAULT,
        ),
        # 91: Number of boundary paths (loops)
        # following: Boundary path data. Repeats number of times specified by
        # code 91. See Boundary Path Data
        # Hatch style:
        # 0 = Hatch “odd parity” area (Normal style)
        # 1 = Hatch outermost area only (Outer style)
        # 2 = Hatch through entire area (Ignore style)
        "hatch_style": DXFAttr(
            75,
            default=const.HATCH_STYLE_NESTED,
            validator=validator.is_in_integer_range(0, 3),
            fixer=RETURN_DEFAULT,
        ),
        # Hatch pattern type:
        # 0 = User-defined
        # 1 = Predefined
        # 2 = Custom
        "pattern_type": DXFAttr(
            76,
            default=const.HATCH_TYPE_PREDEFINED,
            validator=validator.is_in_integer_range(0, 3),
            fixer=RETURN_DEFAULT,
        ),
        # Hatch pattern angle (pattern fill only) in degrees:
        "pattern_angle": DXFAttr(52, default=0),
        # Hatch pattern scale or spacing (pattern fill only):
        "pattern_scale": DXFAttr(
            41,
            default=1,
            validator=validator.is_not_zero,
            fixer=RETURN_DEFAULT,
        ),
        # Hatch pattern double flag (pattern fill only):
        # 0 = not double
        # 1 = double
        "pattern_double": DXFAttr(
            77,
            default=0,
            validator=validator.is_integer_bool,
            fixer=RETURN_DEFAULT,
        ),
        # 78: Number of pattern definition lines
        # following: Pattern line data. Repeats number of times specified by
        # code 78. See Pattern Data
        # Pixel size used to determine the density to perform various intersection
        # and ray casting operations in hatch pattern computation for associative
        # hatches and hatches created with the Flood method of hatching
        "pixel_size": DXFAttr(47, optional=True),
        # Number of seed points
        "n_seed_points": DXFAttr(
            98,
            default=0,
            validator=validator.is_greater_or_equal_zero,
            fixer=RETURN_DEFAULT,
        ),
        # 10, 20: Seed point (in OCS) 2D point (multiple entries)
        # 450 Indicates solid hatch or gradient; if solid hatch, the values for the
        # remaining codes are ignored but must be present. Optional;
        #
        # if code 450 is in the file, then the following codes must be in the
        # file: 451, 452, 453, 460, 461, 462, and 470.
        # If code 450 is not in the file, then the following codes must not be
        # in the file: 451, 452, 453, 460, 461, 462, and 470
        #
        #   0 = Solid hatch
        #   1 = Gradient
        #
        # 451 Zero is reserved for future use
        # 452 Records how colors were defined and is used only by dialog code:
        #
        #   0 = Two-color gradient
        #   1 = Single-color gradient
        #
        # 453 Number of colors:
        #
        #   0 = Solid hatch
        #   2 = Gradient
        #
        # 460 Rotation angle in radians for gradients (default = 0, 0)
        # 461 Gradient definition; corresponds to the Centered option on the
        #     Gradient Tab of the Boundary Hatch and Fill dialog box. Each gradient
        #     has two definitions, shifted and non-shifted. A Shift value describes
        #     the blend of the two definitions that should be used. A value of 0.0
        #     means only the non-shifted version should be used, and a value of 1.0
        #     means that only the shifted version should be used.
        #
        # 462 Color tint value used by dialog code (default = 0, 0; range is 0.0 to
        #     1.0). The color tint value is a gradient color and controls the degree
        #     of tint in the dialog when the Hatch group code 452 is set to 1.
        #
        # 463 Reserved for future use:
        #
        #   0 = First value
        #   1 = Second value
        #
        # 470 String (default = LINEAR)
    },
)
acdb_hatch_group_code = group_code_mapping(acdb_hatch)


@register_entity
class Hatch(BasePolygon):
    """DXF HATCH entity"""

    DXFTYPE = "HATCH"
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_hatch)
    MIN_DXF_VERSION_FOR_EXPORT = const.DXF2000
    LOAD_GROUP_CODES = acdb_hatch_group_code

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        super().export_entity(tagwriter)
        tagwriter.write_tag2(const.SUBCLASS_MARKER, acdb_hatch.name)
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "elevation",
                "extrusion",
                "pattern_name",
                "solid_fill",
                "associative",
            ],
        )
        self.paths.export_dxf(tagwriter, self.dxftype())
        self.dxf.export_dxf_attribs(tagwriter, ["hatch_style", "pattern_type"])
        if self.pattern:
            self.dxf.export_dxf_attribs(
                tagwriter, ["pattern_angle", "pattern_scale", "pattern_double"]
            )
            self.pattern.export_dxf(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, ["pixel_size"])
        self.export_seeds(tagwriter)
        if self.gradient:
            self.gradient.export_dxf(tagwriter)

    def load_seeds(self, tags: Tags) -> Tags:
        try:
            start_index = tags.tag_index(98)
        except const.DXFValueError:
            return tags
        seed_data = tags.collect_consecutive_tags(
            {98, 10, 20}, start=start_index
        )

        # Remove seed data from tags:
        del tags[start_index: start_index + len(seed_data) + 1]

        # Just process vertices with group code 10
        self.seeds = [value for code, value in seed_data if code == 10]
        return tags

    def export_seeds(self, tagwriter: "TagWriter"):
        tagwriter.write_tag2(98, len(self.seeds))
        for seed in self.seeds:
            tagwriter.write_vertex(10, seed[:2])

    def remove_dependencies(self, other: "Drawing" = None) -> None:
        """Remove all dependencies from actual document. (internal API)"""
        if not self.is_alive:
            return

        super().remove_dependencies()
        self.remove_association()

    def remove_association(self):
        """Remove associated path elements."""
        if self.dxf.associative:
            self.dxf.associative = 0
            for path in self.paths:
                path.source_boundary_objects = []

    def associate(self, path: TPath, entities: Iterable["DXFEntity"]):
        """Set association from hatch boundary `path` to DXF geometry `entities`.

        A HATCH entity can be associative to a base geometry, this association
        is **not** maintained nor verified by `ezdxf`, so if you modify the base
        geometry the geometry of the boundary path is not updated and no
        verification is done to check if the associated geometry matches
        the boundary path, this opens many possibilities to create
        invalid DXF files: USE WITH CARE!

        """
        # I don't see this as a time critical operation, do as much checks as
        # needed to avoid invalid DXF files.
        if not self.is_alive:
            raise const.DXFStructureError("HATCH entity is destroyed")

        doc = self.doc
        owner = self.dxf.owner
        handle = self.dxf.handle
        if doc is None or owner is None or handle is None:
            raise const.DXFStructureError(
                "virtual entity can not have associated entities"
            )

        for entity in entities:
            if not entity.is_alive or entity.is_virtual:
                raise const.DXFStructureError(
                    "associated entity is destroyed or a virtual entity"
                )
            if doc is not entity.doc:
                raise const.DXFStructureError(
                    "associated entity is from a different document"
                )
            if owner != entity.dxf.owner:
                raise const.DXFStructureError(
                    "associated entity is from a different layout"
                )

            path.source_boundary_objects.append(entity.dxf.handle)
            entity.append_reactor_handle(handle)
        self.dxf.associative = 1 if len(path.source_boundary_objects) else 0

    def set_seed_points(self, points: Iterable[Tuple[float, float]]) -> None:
        """Set seed points, `points` is an iterable of (x, y)-tuples.
        I don't know why there can be more than one seed point.
        All points in :ref:`OCS` (:attr:`Hatch.dxf.elevation` is the Z value)

        """
        points = list(points)
        if len(points) < 1:
            raise const.DXFValueError(
                "Param points should be an iterable of 2D points and requires at "
                "least one point."
            )
        self.seeds = list(points)
        self.dxf.n_seed_points = len(self.seeds)


def _transform_2d_ocs_vertices(
    ucs, vertices, elevation, extrusion
) -> List[Tuple[float, float]]:
    ocs_vertices = (Vec3(x, y, elevation) for x, y in vertices)
    return [
        (v.x, v.y)
        for v in ucs.ocs_points_to_ocs(ocs_vertices, extrusion=extrusion)
    ]


class Pattern:
    def __init__(self, lines: Iterable["PatternLine"] = None):
        self.lines: List["PatternLine"] = list(lines) if lines else []

    @classmethod
    def load_tags(cls, tags: Tags) -> "Pattern":
        grouped_line_tags = group_tags(tags, splitcode=53)
        return cls(
            PatternLine.load_tags(line_tags) for line_tags in grouped_line_tags
        )

    def clear(self) -> None:
        """Delete all pattern definition lines."""
        self.lines = []

    def add_line(
        self,
        angle: float = 0,
        base_point: "Vertex" = (0, 0),
        offset: "Vertex" = (0, 0),
        dash_length_items: Iterable[float] = None,
    ) -> None:
        """Create a new pattern definition line and add the line to the
        :attr:`Pattern.lines` attribute.

        """
        assert (
            dash_length_items is not None
        ), "argument 'dash_length_items' is None"
        self.lines.append(
            PatternLine(angle, base_point, offset, dash_length_items)
        )

    def export_dxf(self, tagwriter: "TagWriter", force=False) -> None:
        if len(self.lines) or force:
            tagwriter.write_tag2(78, len(self.lines))
            for line in self.lines:
                line.export_dxf(tagwriter)

    def __str__(self) -> str:
        return "[" + ",".join(str(line) for line in self.lines) + "]"

    def as_list(self) -> List:
        return [line.as_list() for line in self.lines]

    def scale(self, factor: float = 1, angle: float = 0) -> None:
        """Scale and rotate pattern.

        Be careful, this changes the base pattern definition, maybe better use
        :meth:`Hatch.set_pattern_scale` or :meth:`Hatch.set_pattern_angle`.

        Args:
            factor: scaling factor
            angle: rotation angle in degrees

        """
        scaled_pattern = pattern.scale_pattern(
            self.as_list(), factor=factor, angle=angle
        )
        self.clear()
        for line in scaled_pattern:
            self.add_line(*line)


class PatternLine:
    def __init__(
        self,
        angle: float = 0,
        base_point: "Vertex" = (0, 0),
        offset: "Vertex" = (0, 0),
        dash_length_items: Iterable[float] = None,
    ):
        self.angle: float = float(angle)  # in degrees
        self.base_point: Vec2 = Vec2(base_point)
        self.offset: Vec2 = Vec2(offset)
        self.dash_length_items: List[float] = (
            [] if dash_length_items is None else list(dash_length_items)
        )
        # dash_length_items = [item0, item1, ...]
        # item > 0 is line, < 0 is gap, 0.0 = dot;

    @staticmethod
    def load_tags(tags: Tags) -> "PatternLine":
        p = {53: 0, 43: 0, 44: 0, 45: 0, 46: 0}
        dash_length_items = []
        for tag in tags:
            code, value = tag
            if code == 49:
                dash_length_items.append(value)
            else:
                p[code] = value
        return PatternLine(
            p[53], (p[43], p[44]), (p[45], p[46]), dash_length_items
        )

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        write_tag = tagwriter.write_tag2
        write_tag(53, self.angle)
        write_tag(43, self.base_point.x)
        write_tag(44, self.base_point.y)
        write_tag(45, self.offset.x)
        write_tag(46, self.offset.y)
        write_tag(79, len(self.dash_length_items))
        for item in self.dash_length_items:
            write_tag(49, item)

    def __str__(self):
        return (
            f"[{self.angle}, {self.base_point}, {self.offset}, "
            f"{self.dash_length_items}]"
        )

    def as_list(self) -> List:
        return [
            self.angle,
            self.base_point,
            self.offset,
            self.dash_length_items,
        ]


class Gradient:
    def __init__(self):
        # 1 for gradient by default, 0 for Solid
        self.kind: int = 1
        self.number_of_colors: int = 2
        self.color1: RGB = (0, 0, 0)
        self.aci1: Optional[int] = None
        self.color2: RGB = (255, 255, 255)
        self.aci2: Optional[int] = None

        # 1 = use a smooth transition between color1 and a specified tint
        self.one_color: int = 0

        # Use degree NOT radians for rotation, because there should be one
        # system for all angles:
        self.rotation: float = 0.0
        self.centered: float = 0.0
        self.tint: float = 0.0
        self.name: str = "LINEAR"

    @classmethod
    def load_tags(cls, tags: Tags) -> "Gradient":
        gdata = cls()
        assert tags[0].code == 450
        gdata.kind = tags[0].value  # 0 = solid; 1 = gradient
        first_color_value = True
        first_aci_value = True
        for code, value in tags:
            if code == 460:
                gdata.rotation = math.degrees(value)
            elif code == 461:
                gdata.centered = value
            elif code == 452:
                gdata.one_color = value
            elif code == 462:
                gdata.tint = value
            elif code == 470:
                gdata.name = value
            elif code == 453:
                gdata.number_of_colors = value
            elif code == 63:
                if first_aci_value:
                    gdata.aci1 = value
                    first_aci_value = False
                else:
                    gdata.aci2 = value
            elif code == 421:
                if first_color_value:
                    gdata.color1 = clr.int2rgb(value)
                    first_color_value = False
                else:
                    gdata.color2 = clr.int2rgb(value)
        return gdata

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        # Tag order matters!
        write_tag = tagwriter.write_tag2
        write_tag(450, self.kind)  # gradient or solid
        write_tag(451, 0)  # reserved for the future

        # rotation angle in radians:
        write_tag(460, math.radians(self.rotation))
        write_tag(461, self.centered)
        write_tag(452, self.one_color)
        write_tag(462, self.tint)
        write_tag(453, self.number_of_colors)
        if self.number_of_colors > 0:
            write_tag(463, 0)  # first value, see DXF standard
            if self.aci1 is not None:
                # code 63 "color as ACI" could be left off
                write_tag(63, self.aci1)
            write_tag(421, clr.rgb2int(self.color1))  # first color
        if self.number_of_colors > 1:
            write_tag(463, 1)  # second value, see DXF standard
            if self.aci2 is not None:
                # code 63 "color as ACI" could be left off
                write_tag(63, self.aci2)
            write_tag(421, clr.rgb2int(self.color2))  # second color
        write_tag(470, self.name)

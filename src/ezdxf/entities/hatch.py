# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING, List, Tuple, Union, Sequence, Iterable,
    Optional,
)
import math
import copy
from ezdxf.lldxf import const
from ezdxf.lldxf import validator
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, XType, RETURN_DEFAULT,
    group_code_mapping
)
from ezdxf.lldxf.tags import Tags, group_tags
from ezdxf.lldxf.const import (
    SUBCLASS_MARKER, DXF2000, DXF2004, DXF2010,
    DXFStructureError,
)
from ezdxf import colors as clr
from ezdxf.tools import pattern
from ezdxf.math import (
    Vec3, Vec2, Matrix44, angle_to_param, param_to_angle, BSpline,
    open_uniform_knot_vector, ConstructionEllipse, NULLVEC, Z_AXIS,
)
from ezdxf.math.bspline import global_bspline_interpolation
from ezdxf.math.bulge import bulge_to_arc
from ezdxf.math.transformtools import OCSTransform, NonUniformScalingError
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter, DXFNamespace, Drawing, RGB, DXFEntity, Vertex,
    )

TPath = Union['PolylinePath', 'EdgePath']

__all__ = ['Hatch', 'Gradient', 'Pattern', 'PolylinePath', 'EdgePath']

acdb_hatch = DefSubclass('AcDbHatch', {
    # This subclass can also represent a MPolygon, whatever this is, never seen
    # such a MPolygon in the wild.

    # x- and y-axis always equal 0, z-axis represents the elevation:
    'elevation': DXFAttr(10, xtype=XType.point3d, default=NULLVEC),

    'extrusion': DXFAttr(
        210, xtype=XType.point3d, default=Z_AXIS,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),

    # Hatch pattern name:
    'pattern_name': DXFAttr(2, default='SOLID'),

    # HATCH: Solid fill flag:
    # 0 = pattern fill
    # 1 = solid fill
    # MPolygon: the version of MPolygon
    'solid_fill': DXFAttr(
        70, default=1, alias='mp_version',
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),

    # MPolygon: pattern fill color as the ACI
    'mp_pattern_fill_color': DXFAttr(63, default=const.BYLAYER, optional=True),

    # HATCH: associativity flag
    # 0 = non-associative
    # 1 = associative
    # MPolygon: solid-fill flag
    # 0 = lacks solid fill
    # 1 = has solid fill
    'associative': DXFAttr(
        71, default=0, alias='mp_solid_fill',
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
    'hatch_style': DXFAttr(
        75, default=const.HATCH_STYLE_NESTED,
        validator=validator.is_in_integer_range(0, 3),
        fixer=RETURN_DEFAULT,
    ),

    # Hatch pattern type:
    # 0 = User-defined
    # 1 = Predefined
    # 2 = Custom
    'pattern_type': DXFAttr(
        76, default=const.HATCH_TYPE_PREDEFINED,
        validator=validator.is_in_integer_range(0, 3),
        fixer=RETURN_DEFAULT,
    ),

    # Hatch pattern angle (pattern fill only) in degrees:
    'pattern_angle': DXFAttr(52, default=0),

    # Hatch pattern scale or spacing (pattern fill only):
    'pattern_scale': DXFAttr(
        41, default=1,
        validator=validator.is_not_zero,
        fixer=RETURN_DEFAULT,
    ),

    # For MPolygon, boundary annotation flag:
    # 0 = boundary is not an annotated boundary
    # 1 = boundary is an annotated boundary
    'mp_annotated_boundary': DXFAttr(
        73, default=0, optional=True,
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),

    # Hatch pattern double flag (pattern fill only):
    # 0 = not double
    # 1 = double
    'pattern_double': DXFAttr(
        77, default=0,
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),

    # 78: Number of pattern definition lines
    # following: Pattern line data. Repeats number of times specified by
    # code 78. See Pattern Data

    # Pixel size used to determine the density to perform various intersection
    # and ray casting operations in hatch pattern computation for associative
    # hatches and hatches created with the Flood method of hatching
    'pixel_size': DXFAttr(47, optional=True),

    # Number of seed points
    'n_seed_points': DXFAttr(
        98, default=0,
        validator=validator.is_greater_or_equal_zero,
        fixer=RETURN_DEFAULT,
    ),
    # 10, 20: Seed point (in OCS) 2D point (multiple entries)

    # For MPolygon, offset vector in OCS
    'mp_offset_vector': DXFAttr(11, xtype=XType.point3d, optional=True),

    # For MPolygon, number of degenerate boundary paths (loops), where a
    # degenerate boundary path is a border that is ignored by the hatch:
    'mp_degenerated_loops': DXFAttr(99, optional=True),

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
})
acdb_hatch_group_code = group_code_mapping(acdb_hatch)
GRADIENT_CODES = {
    450, 451, 452, 453, 460, 461, 462, 463, 470, 421, 63
}
PATH_CODES = {
    10, 11, 12, 13, 40, 42, 50, 51, 42, 72, 73, 74, 92, 93, 94, 95, 96, 97, 330
}
PATTERN_DEFINITION_LINE_CODES = {
    53, 43, 44, 45, 46, 79, 49
}


@register_entity
class Hatch(DXFGraphic):
    """ DXF HATCH entity """
    DXFTYPE = 'HATCH'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_hatch)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self):
        super().__init__()
        self.paths = BoundaryPaths()
        self.pattern: Optional[Pattern] = None
        self.gradient: Optional[Gradient] = None
        self.seeds = []

    def _copy_data(self, entity: 'Hatch') -> None:
        """ Copy paths, pattern, gradient, seeds. """
        entity.paths = copy.deepcopy(self.paths)
        entity.pattern = copy.deepcopy(self.pattern)
        entity.gradient = copy.deepcopy(self.gradient)
        entity.seeds = copy.deepcopy(self.seeds)

    def remove_dependencies(self, other: 'Drawing' = None) -> None:
        """ Remove all dependencies from actual document. (internal API) """
        if not self.is_alive:
            return

        super().remove_dependencies()
        self.remove_association()

    def remove_association(self):
        """ Remove associated path elements.

        .. versionadded:: 0.13

        """
        if self.dxf.associative:
            self.dxf.associative = 0
            for path in self.paths:
                path.source_boundary_objects = []

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
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
                dxf, acdb_hatch_group_code, subclass=tags, recover=True)
        return dxf

    def load_paths(self, tags: Tags) -> Tags:
        # Find first group code 91 = count of loops, Spline data also contains
        # group code 91!
        try:
            start_index = tags.tag_index(91)
        except const.DXFValueError:
            raise const.DXFStructureError(
                "HATCH: Missing required DXF tag 'Number of boundary paths "
                "(loops)' (code=91)."
            )

        path_tags = tags.collect_consecutive_tags(
            PATH_CODES, start=start_index + 1)
        if len(path_tags):
            self.paths = BoundaryPaths.load_tags(path_tags)
        end_index = start_index + len(path_tags) + 1
        del tags[start_index: end_index]
        return tags

    def load_pattern(self, tags: Tags) -> Tags:
        try:
            # Group code 78 = Number of patter definition lines
            index = tags.tag_index(78)
        except const.DXFValueError:
            # No pattern definition lines found.
            return tags

        pattern_tags = tags.collect_consecutive_tags(
            PATTERN_DEFINITION_LINE_CODES, start=index + 1)
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
        try:
            start_index = tags.tag_index(98)
        except const.DXFValueError:
            return tags
        seed_data = tags.collect_consecutive_tags(
            {98, 10, 20}, start=start_index)

        # Remove seed data from tags:
        del tags[start_index: start_index + len(seed_data) + 1]

        # Just process vertices with group code 10
        self.seeds = [value for code, value in seed_data if code == 10]
        return tags

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_hatch.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'elevation', 'extrusion', 'pattern_name', 'solid_fill',
            'mp_pattern_fill_color', 'associative',
        ])
        self.paths.export_dxf(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, ['hatch_style', 'pattern_type'])
        if self.pattern:
            self.dxf.export_dxf_attribs(tagwriter, [
                'pattern_angle', 'pattern_scale', 'pattern_double'])
            self.pattern.export_dxf(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, [
            'mp_annotated_boundary', 'pixel_size'])
        self.export_seeds(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, [
            'mp_offset_vector', 'mp_degenerated_loops'])
        if self.gradient:
            self.gradient.export_dxf(tagwriter)

    def export_seeds(self, tagwriter: 'TagWriter'):
        tagwriter.write_tag2(98, len(self.seeds))
        for seed in self.seeds:
            tagwriter.write_vertex(10, seed[:2])

    @property
    def has_solid_fill(self) -> bool:
        """ ``True`` if hatch has a solid fill. (read only) """
        return bool(self.dxf.solid_fill)

    @property
    def has_pattern_fill(self) -> bool:
        """ ``True`` if hatch has a pattern fill. (read only) """
        return not bool(self.dxf.solid_fill)

    @property
    def has_gradient_data(self) -> bool:
        """ ``True`` if hatch has a gradient fill. A hatch with gradient fill
        has also a solid fill. (read only)
        """
        return bool(self.gradient)

    @property
    def bgcolor(self) -> Optional['RGB']:
        """
        Property background color as (r, g, b)-tuple, rgb values in the
        range [0, 255] (read/write/del)

        usage::

            color = hatch.bgcolor  # get background color as (r, g, b) tuple
            hatch.bgcolor = (10, 20, 30)  # set background color
            del hatch.bgcolor  # delete background color

        """
        try:
            xdata_bgcolor = self.get_xdata('HATCHBACKGROUNDCOLOR')
        except const.DXFValueError:
            return None
        color = xdata_bgcolor.get_first_value(1071, 0)
        return clr.int2rgb(color)

    @bgcolor.setter
    def bgcolor(self, rgb: 'RGB') -> None:
        color_value = clr.rgb2int(
            rgb) | -0b111110000000000000000000000000  # it's magic

        self.discard_xdata('HATCHBACKGROUNDCOLOR')
        self.set_xdata('HATCHBACKGROUNDCOLOR', [(1071, color_value)])

    @bgcolor.deleter
    def bgcolor(self) -> None:
        self.discard_xdata('HATCHBACKGROUNDCOLOR')

    def set_solid_fill(self, color: int = 7, style: int = 1, rgb: 'RGB' = None):
        """ Set :class:`Hatch` to solid fill mode and removes all gradient and
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
        self.dxf.pattern_name = 'SOLID'
        self.dxf.pattern_type = const.HATCH_TYPE_PREDEFINED
        if rgb is not None:
            self.rgb: 'RGB' = rgb

    def set_gradient(self,
                     color1: 'RGB' = (0, 0, 0),
                     color2: 'RGB' = (255, 255, 255),
                     rotation: float = 0.,
                     centered: float = 0.,
                     one_color: int = 0,
                     tint: float = 0.,
                     name: str = 'LINEAR') -> None:
        """ Set :class:`Hatch` to gradient fill mode and removes all pattern
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
        if self.doc is not None and self.drawing.dxfversion < DXF2004:
            raise const.DXFVersionError("Gradient support requires DXF R2004")
        if name not in const.GRADIENT_TYPES:
            raise const.DXFValueError(f'Invalid gradient type name: {name}')

        self.pattern = None
        self.dxf.solid_fill = 1
        self.dxf.pattern_name = 'SOLID'
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

    def set_pattern_fill(self, name: str, color: int = 7, angle: float = 0.,
                         scale: float = 1., double: int = 0,
                         style: int = 1, pattern_type: int = 1,
                         definition=None) -> None:
        """ Set :class:`Hatch` to pattern fill mode. Removes all gradient
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
                measurement = self.doc.header.get('$MEASUREMENT', measurement)
            predefined_pattern = pattern.ISO_PATTERN if measurement else pattern.IMPERIAL_PATTERN
            definition = predefined_pattern.get(
                name, predefined_pattern['ANSI31'])
        self.set_pattern_definition(
            definition,
            factor=self.dxf.pattern_scale,
            angle=self.dxf.pattern_angle,
        )

    def set_pattern_definition(self, lines: Sequence, factor: float = 1,
                               angle: float = 0) -> None:
        """ Setup hatch patten definition by a list of definition lines and  a
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

        .. versionchanged:: 0.13
            added `angle` argument

        """
        if factor != 1 or angle:
            lines = pattern.scale_pattern(lines, factor=factor, angle=angle)
        self.pattern = Pattern(
            [PatternLine(line[0], line[1], line[2], line[3]) for line in lines])

    def set_pattern_scale(self, scale: float) -> None:
        """ Set scaling of pattern definition to `scale`.

        Starts always from the original base scaling, :code:`set_pattern_scale(1)`
        reset the pattern scaling to the original appearance as defined by the
        pattern designer, but only if the the pattern attribute
        :attr:`dxf.pattern_scale` represents the actual scaling, it is not
        possible to recreate the original pattern scaling from the pattern
        definition itself.

        Args:
            scale: pattern scaling factor

        .. versionadded:: 0.13

        """
        if not self.has_pattern_fill:
            return
        dxf = self.dxf
        self.pattern.scale(factor=1.0 / dxf.pattern_scale * scale)
        dxf.pattern_scale = scale

    def set_pattern_angle(self, angle: float) -> None:
        """ Set rotation of pattern definition to `angle` in degrees.

        Starts always from the original base rotation 0,
        :code:`set_pattern_angle(0)` reset the pattern rotation to the original
        appearance as defined by the pattern designer, but only if the the
        pattern attribute :attr:`dxf.pattern_angle` represents the actual
        rotation, it is not possible to recreate the original rotation from the
        pattern definition itself.

        Args:
            angle: rotation angle in degrees

        .. versionadded:: 0.13

        """
        if not self.has_pattern_fill:
            return
        dxf = self.dxf
        self.pattern.scale(angle=angle - dxf.pattern_angle)
        dxf.pattern_angle = angle % 360.0

    def set_seed_points(self, points: Iterable[Tuple[float, float]]) -> None:
        """ Set seed points, `points` is an iterable of (x, y)-tuples.
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

    def transform(self, m: 'Matrix44') -> 'Hatch':
        """ Transform HATCH entity by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        dxf = self.dxf
        ocs = OCSTransform(dxf.extrusion, m)

        elevation = Vec3(dxf.elevation).z
        self.paths.transform(ocs, elevation=elevation)
        dxf.elevation = ocs.transform_vertex(Vec3(0, 0, elevation)).replace(
            x=0, y=0)
        dxf.extrusion = ocs.new_extrusion
        # todo scale pattern
        return self

    def associate(self, path: TPath, entities: Iterable['DXFEntity']):
        """ Set association from hatch boundary `path` to DXF geometry `entities`.

        A HATCH entity can be associative to a base geometry, this association
        is **not** maintained nor verified by `ezdxf`, so if you modify the base
        geometry the geometry of the boundary path is not updated and no
        verification is done to check if the associated geometry matches
        the boundary path, this opens many possibilities to create
        invalid DXF files: USE WITH CARE!

        """
        self.dxf.associative = 1
        hatch_dxf_handle = self.dxf.handle
        for entity in entities:
            path.source_boundary_objects.append(entity.dxf.handle)
            entity.append_reactor_handle(hatch_dxf_handle)


class BoundaryPaths:
    def __init__(self, paths: List[TPath] = None):
        self.paths: List[TPath] = paths or []

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, item):
        return self.paths[item]

    @classmethod
    def load_tags(cls, tags: Tags) -> 'BoundaryPaths':
        paths = []
        assert tags[0].code == 92
        grouped_path_tags = group_tags(tags, splitcode=92)
        for path_tags in grouped_path_tags:
            path_type_flags = path_tags[0].value
            is_polyline_path = bool(path_type_flags & 2)
            path = PolylinePath.load_tags(
                path_tags) if is_polyline_path else EdgePath.load_tags(
                path_tags)
            path.path_type_flags = path_type_flags
            paths.append(path)
        return cls(paths)

    def clear(self) -> None:
        """ Remove all boundary paths. """
        self.paths = []

    def external_paths(self) -> Iterable[TPath]:
        """ Iterable of external paths, could be empty. """
        for b in self.paths:
            if b.path_type_flags & const.BOUNDARY_PATH_EXTERNAL:
                yield b

    def outermost_paths(self) -> Iterable[TPath]:
        """ Iterable of outermost paths, could be empty. """
        for b in self.paths:
            if b.path_type_flags & const.BOUNDARY_PATH_OUTERMOST:
                yield b

    def default_paths(self) -> Iterable[TPath]:
        """ Iterable of default paths, could be empty. """
        not_default = const.BOUNDARY_PATH_OUTERMOST + const.BOUNDARY_PATH_EXTERNAL
        for b in self.paths:
            if bool(b.path_type_flags & not_default) is False:
                yield b

    def rendering_paths(self, hatch_style: int = const.HATCH_STYLE_NESTED
                        ) -> Iterable[TPath]:
        """ Iterable of paths to process for rendering, filters unused
        boundary paths according to the given hatch style:

        - NESTED: use all boundary paths
        - OUTERMOST: use EXTERNAL and OUTERMOST boundary paths
        - IGNORE: ignore all paths except EXTERNAL boundary paths

        Yields paths in order of EXTERNAL, OUTERMOST and DEFAULT.

        """

        def path_type_enum(flags) -> int:
            if flags & const.BOUNDARY_PATH_EXTERNAL:
                return 0
            elif flags & const.BOUNDARY_PATH_OUTERMOST:
                return 1
            return 2

        paths = sorted(
            (path_type_enum(p.path_type_flags), i, p)
            for i, p in enumerate(self.paths)
        )
        ignore = 1  # EXTERNAL only
        if hatch_style == const.HATCH_STYLE_NESTED:
            ignore = 3
        elif hatch_style == const.HATCH_STYLE_OUTERMOST:
            ignore = 2
        return (p for path_type, _, p in paths if path_type < ignore)

    def add_polyline_path(self, path_vertices: Sequence[Tuple[float, ...]],
                          is_closed: bool = True,
                          flags: int = 1) -> 'PolylinePath':
        """ Create and add a new :class:`PolylinePath` object.

        Args:
            path_vertices: list of polyline vertices as (x, y) or
                (x, y, bulge)-tuples.
            is_closed: 1 for a closed polyline else 0
            flags: external(1) or outermost(16) or default (0)

        """
        new_path = PolylinePath()
        new_path.set_vertices(path_vertices, is_closed)
        new_path.path_type_flags = flags | const.BOUNDARY_PATH_POLYLINE
        self.paths.append(new_path)
        return new_path

    def add_edge_path(self, flags: int = 1) -> 'EdgePath':
        """ Create and add a new :class:`EdgePath` object.

        Args:
            flags: external(1) or outermost(16) or default (0)

        """
        new_path = EdgePath()
        new_path.path_type_flags = flags
        self.paths.append(new_path)
        return new_path

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(91, len(self.paths))
        for path in self.paths:
            path.export_dxf(tagwriter)

    def transform(self, ocs: OCSTransform, elevation: float = 0) -> None:
        """ Transform HATCH boundary paths.

        These paths are 2d elements, placed in the OCS of the HATCH.

        """
        if not ocs.scale_uniform:
            self.polyline_to_edge_path(just_with_bulge=True)
            self.arc_edges_to_ellipse_edges()

        for path in self.paths:
            path.transform(ocs, elevation=elevation)

    def polyline_to_edge_path(self, just_with_bulge=True) -> None:
        """ Convert polyline paths including bulge values to line- and arc edges.

        Args:
            just_with_bulge: convert only polyline paths including bulge
                values if ``True``

        """

        def _edges(points) -> Iterable[Union[LineEdge, ArcEdge]]:
            prev_point = None
            prev_bulge = None
            for x, y, bulge in points:
                point = Vec3(x, y)
                if prev_point is None:
                    prev_point = point
                    prev_bulge = bulge
                    continue

                if prev_bulge != 0:
                    arc = ArcEdge()
                    arc.center, start_angle, end_angle, arc.radius = bulge_to_arc(
                        prev_point, point, prev_bulge)
                    chk_point = arc.center + Vec2.from_angle(start_angle,
                                                             arc.radius)
                    arc.ccw = chk_point.isclose(prev_point, abs_tol=1e-9)
                    arc.start_angle = math.degrees(start_angle) % 360.0
                    arc.end_angle = math.degrees(end_angle) % 360.0
                    if math.isclose(arc.start_angle,
                                    arc.end_angle) and math.isclose(
                        arc.start_angle, 0):
                        arc.end_angle = 360.0
                    yield arc
                else:
                    line = LineEdge()
                    line.start = (prev_point.x, prev_point.y)
                    line.end = (point.x, point.y)
                    yield line

                prev_point = point
                prev_bulge = bulge

        def to_edge_path(polyline_path) -> EdgePath:
            edge_path = EdgePath()
            vertices = list(polyline_path.vertices)
            if polyline_path.is_closed:
                vertices.append(vertices[0])
            edge_path.edges = list(_edges(vertices))
            return edge_path

        for path_index, path in enumerate(self.paths):
            if path.PATH_TYPE == 'PolylinePath':
                if just_with_bulge and not path.has_bulge():
                    continue
                self.paths[path_index] = to_edge_path(path)

    def arc_edges_to_ellipse_edges(self) -> None:
        """ Convert all arc edges to ellipse edges. """

        def to_ellipse(arc: ArcEdge) -> EllipseEdge:
            ellipse = EllipseEdge()
            ellipse.center = arc.center
            ellipse.ratio = 1.0
            ellipse.major_axis = (arc.radius, 0.0)
            ellipse.start_angle = arc.start_angle
            ellipse.end_angle = arc.end_angle
            ellipse.ccw = arc.ccw
            return ellipse

        for path in self.paths:
            if path.PATH_TYPE == 'EdgePath':
                edges = path.edges
                for edge_index, edge in enumerate(edges):
                    if edge.EDGE_TYPE == 'ArcEdge':
                        edges[edge_index] = to_ellipse(edge)

    def ellipse_edges_to_spline_edges(self, num: int = 32) -> None:
        """
        Convert all ellipse edges to spline edges (approximation).

        Args:
            num: count of control points for a **full** ellipse, partial
                ellipses have proportional fewer control points but at least 3.

        """

        def to_spline_edge(e: EllipseEdge) -> SplineEdge:
            # No OCS transformation needed, source ellipse and target spline
            # reside in the same OCS.
            # ezdxf stores angles always in counter-clockwise orientation.
            # DXF conversion is done at export, see also ArcEdge.load_tags()
            # for explanation.

            ellipse = ConstructionEllipse(
                center=e.center, major_axis=e.major_axis, ratio=e.ratio,
                start_param=e.start_param, end_param=e.end_param,
            )
            count = max(int(float(num) * ellipse.param_span / math.tau), 3)
            tool = BSpline.ellipse_approximation(ellipse, count)
            spline = SplineEdge()
            spline.degree = tool.degree
            if not e.ccw:
                tool = tool.reverse()

            spline.control_points = Vec2.list(tool.control_points)
            spline.knot_values = tool.knots()
            spline.weights = tool.weights()
            return spline

        for path_index, path in enumerate(self.paths):
            if path.PATH_TYPE == 'EdgePath':
                edges = path.edges
                for edge_index, edge in enumerate(edges):
                    if edge.EDGE_TYPE == 'EllipseEdge':
                        edges[edge_index] = to_spline_edge(edge)

    def spline_edges_to_line_edges(self, factor: int = 8) -> None:
        """ Convert all spline edges to line edges (approximation).

        Args:
            factor: count of approximation segments = count of control
                points x factor

        """

        def to_line_edges(spline_edge):
            weights = spline_edge.weights
            if len(spline_edge.control_points):
                bspline = BSpline(
                    control_points=spline_edge.control_points,
                    order=spline_edge.degree + 1,
                    knots=spline_edge.knot_values,
                    weights=weights if len(weights) else None,
                )
            elif len(spline_edge.fit_points):
                bspline = BSpline.from_fit_points(spline_edge.fit_points,
                                                  spline_edge.degree)
            else:
                raise DXFStructureError(
                    'SplineEdge() without control points or fit points.')
            segment_count = (max(len(bspline.control_points), 3) - 1) * factor
            vertices = list(bspline.approximate(segment_count))
            for v1, v2 in zip(vertices[:-1], vertices[1:]):
                edge = LineEdge()
                edge.start = v1.vec2
                edge.end = v2.vec2
                yield edge

        for path in self.paths:
            if path.PATH_TYPE == 'EdgePath':
                new_edges = []
                for edge in path.edges:
                    if edge.EDGE_TYPE == 'SplineEdge':
                        new_edges.extend(to_line_edges(edge))
                    else:
                        new_edges.append(edge)
                path.edges = new_edges

    def ellipse_edges_to_line_edges(self, num: int = 64) -> None:
        """ Convert all ellipse edges to line edges (approximation).

        Args:
            num: count of control points for a **full** ellipse, partial
                ellipses have proportional fewer control points but at least 3.

        """

        def to_line_edges(edge):
            ellipse = ConstructionEllipse(
                center=edge.center,
                major_axis=edge.major_axis,
                ratio=edge.ratio,
                start_param=edge.start_param,
                end_param=edge.end_param,
            )
            segment_count = max(int(float(num) * ellipse.param_span / math.tau),
                                3)
            params = ellipse.params(segment_count + 1)
            if not edge.ccw:
                params = reversed(list(params))
            vertices = list(ellipse.vertices(params))
            for v1, v2 in zip(vertices[:-1], vertices[1:]):
                line = LineEdge()
                line.start = v1.vec2
                line.end = v2.vec2
                yield line

        for path in self.paths:
            if path.PATH_TYPE == 'EdgePath':
                new_edges = []
                for edge in path.edges:
                    if edge.EDGE_TYPE == 'EllipseEdge':
                        new_edges.extend(to_line_edges(edge))
                    else:
                        new_edges.append(edge)
                path.edges = new_edges

    def all_to_spline_edges(self, num: int = 64) -> None:
        """ Convert all bulge, arc and ellipse edges to spline edges
        (approximation).

        Args:
            num: count of control points for a **full** circle/ellipse, partial
                circles/ellipses have proportional fewer control points but at
                least 3.

        """
        self.polyline_to_edge_path(just_with_bulge=True)
        self.arc_edges_to_ellipse_edges()
        self.ellipse_edges_to_spline_edges(num)

    def all_to_line_edges(self, num: int = 64, spline_factor: int = 8) -> None:
        """ Convert all bulge, arc and ellipse edges to spline edges and
        approximate this splines by line edges.

        Args:
            num: count of control points for a **full** circle/ellipse, partial
                circles/ellipses have proportional fewer control points but at
                least 3.
            spline_factor: count of spline approximation segments = count of
                control points x spline_factor

        """
        self.polyline_to_edge_path(just_with_bulge=True)
        self.arc_edges_to_ellipse_edges()
        self.ellipse_edges_to_line_edges(num)
        self.spline_edges_to_line_edges(spline_factor)

    def has_critical_elements(self) -> bool:
        """ Returns ``True`` if any boundary path has bulge values or arc edges
        or ellipse edges.

        """
        for path in self.paths:
            if path.PATH_TYPE == 'PolylinePath':
                return path.has_bulge()
            else:
                for edge in path.edges:
                    if edge.EDGE_TYPE in {'ArcEdge', 'EllipseEdge'}:
                        return True
        return False


def pop_source_boundary_objects_tags(path_tags: Tags) -> List[str]:
    source_boundary_object_tags = []
    while len(path_tags):
        if path_tags[-1].code in (97, 330):
            last_tag = path_tags.pop()
            if last_tag.code == 330:
                source_boundary_object_tags.append(last_tag.value)
            else:  # code == 97
                # result list does not contain the length tag!
                source_boundary_object_tags.reverse()
                return source_boundary_object_tags
        else:
            # No source boundary objects found - entity is not valid for AutoCAD
            return []


def export_source_boundary_objects(tagwriter: 'TagWriter',
                                   handles: Sequence[str]):
    tagwriter.write_tag2(97, len(handles))
    for handle in handles:
        tagwriter.write_tag2(330, handle)


class PolylinePath:
    PATH_TYPE = 'PolylinePath'

    def __init__(self):
        self.path_type_flags: int = const.BOUNDARY_PATH_POLYLINE
        self.is_closed = False
        # List of 2D coordinates with bulge values (x, y, bulge);
        # bulge default = 0.0
        self.vertices: List[Tuple[float, float, float]] = []
        self.source_boundary_objects: List[str] = []  # (330, handle) tags

    @classmethod
    def load_tags(cls, tags: Tags) -> 'PolylinePath':
        path = PolylinePath()
        path.source_boundary_objects = pop_source_boundary_objects_tags(tags)
        for tag in tags:
            code, value = tag
            if code == 10:  # vertex coordinates
                # (x, y, bulge); bulge default = 0.0
                path.vertices.append((value[0], value[1], 0.0))
            elif code == 42:  # bulge value
                x, y, bulge = path.vertices.pop()
                # Last coordinates with new bulge value
                path.vertices.append((x, y, value))
            elif code == 72:
                pass  # ignore this value
            elif code == 73:
                path.is_closed = value
            elif code == 92:
                path.path_type_flags = value
            elif code == 93:  # number of polyline vertices
                pass  # ignore this value
        return path

    def set_vertices(self, vertices: Sequence[Sequence[float]],
                     is_closed: bool = True) -> None:
        """ Set new `vertices` as new polyline path, a vertex has to be a
        (x, y) or a (x, y, bulge)-tuple.

        """
        new_vertices = []
        for vertex in vertices:
            if len(vertex) == 2:
                x, y = vertex
                bulge = 0
            elif len(vertex) == 3:
                x, y, bulge = vertex
            else:
                raise const.DXFValueError(
                    "Invalid vertex format, expected (x, y) or (x, y, bulge)")
            new_vertices.append((x, y, bulge))
        self.vertices = new_vertices
        self.is_closed = is_closed

    def clear(self) -> None:
        """ Removes all vertices and all handles to associated DXF objects
        (:attr:`source_boundary_objects`).
        """
        self.vertices = []
        self.is_closed = False
        self.source_boundary_objects = []

    def has_bulge(self) -> bool:
        return any(bulge for x, y, bulge in self.vertices)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        has_bulge = self.has_bulge()
        write_tag = tagwriter.write_tag2

        write_tag(92, int(self.path_type_flags))
        write_tag(72, int(has_bulge))
        write_tag(73, int(self.is_closed))
        write_tag(93, len(self.vertices))
        for x, y, bulge in self.vertices:
            tagwriter.write_vertex(10, (float(x), float(y)))
            if has_bulge:
                write_tag(42, float(bulge))

        export_source_boundary_objects(tagwriter, self.source_boundary_objects)

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        """ Transform polyline path.
        """
        has_non_uniform_scaling = not ocs.scale_uniform

        def _transform():
            for x, y, bulge in self.vertices:
                # PolylinePaths() with arcs should be converted to
                # EdgePath(in BoundaryPath.transform()).
                if bulge and has_non_uniform_scaling:
                    raise NonUniformScalingError(
                        'Polyline path with arcs does not support non-uniform scaling')
                v = ocs.transform_vertex(Vec3(x, y, elevation))
                yield v.x, v.y, bulge

        if self.vertices:
            self.vertices = list(_transform())


class EdgePath:
    PATH_TYPE = 'EdgePath'

    def __init__(self):
        self.path_type_flags = const.BOUNDARY_PATH_DEFAULT
        self.edges = []
        self.source_boundary_objects = []

    def __iter__(self):
        return iter(self.edges)

    @classmethod
    def load_tags(cls, tags: Tags) -> 'EdgePath':
        edge_path = cls()
        edge_path.source_boundary_objects = pop_source_boundary_objects_tags(
            tags)
        edge_groups = group_tags(tags, splitcode=72)
        for edge_tags in edge_groups:
            edge_path.edges.append(edge_path.load_edge(edge_tags))
        return edge_path

    @staticmethod
    def load_edge(tags: Tags) -> 'EdgeTypes':
        edge_type = tags[0].value
        if 0 < edge_type < 5:
            return EDGE_CLASSES[edge_type].load_tags(tags[1:])
        else:
            raise const.DXFStructureError(
                f"HATCH: unknown edge type: {edge_type}")

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        """ Transform edge boundary paths. """
        for edge in self.edges:
            edge.transform(ocs, elevation=elevation)

    def add_line(self, start: Sequence[float],
                 end: Sequence[float]) -> 'LineEdge':
        """ Add a :class:`LineEdge` from `start` to `end`.

        Args:
            start: start point of line, (x, y)-tuple
            end: end point of line, (x, y)-tuple

        """
        line = LineEdge()
        line.start = start
        line.end = end
        self.edges.append(line)
        return line

    def add_arc(self, center: Tuple[float, float],
                radius: float = 1.,
                start_angle: float = 0.,
                end_angle: float = 360.,
                ccw: bool = True) -> 'ArcEdge':
        """ Add an :class:`ArcEdge`.

        Args:
            center: center point of arc, (x, y)-tuple
            radius: radius of circle
            start_angle: start angle of arc in degrees
            end_angle: end angle of arc in degrees
            ccw: ``True`` for counter clockwise ``False`` for
                clockwise orientation

        """
        arc = ArcEdge()
        arc.center = center
        arc.radius = radius
        arc.start_angle = start_angle
        arc.end_angle = end_angle
        arc.ccw = bool(ccw)
        self.edges.append(arc)
        return arc

    def add_ellipse(self, center: Tuple[float, float],
                    major_axis: Tuple[float, float] = (1., 0.),
                    ratio: float = 1.,
                    start_angle: float = 0.,
                    end_angle: float = 360.,
                    ccw: bool = True) -> 'EllipseEdge':
        """ Add an :class:`EllipseEdge`.

        Args:
            center: center point of ellipse, (x, y)-tuple
            major_axis: vector of major axis as (x, y)-tuple
            ratio: ratio of minor axis to major axis as float
            start_angle: start angle of arc in degrees
            end_angle: end angle of arc in degrees
            ccw: ``True`` for counter clockwise ``False`` for
                clockwise orientation

        """
        if ratio > 1.:
            raise const.DXFValueError("Parameter 'ratio' has to be <= 1.0")
        ellipse = EllipseEdge()
        ellipse.center = center
        ellipse.major_axis = major_axis
        ellipse.ratio = ratio
        ellipse.start_angle = start_angle
        ellipse.end_angle = end_angle
        ellipse.ccw = bool(ccw)
        self.edges.append(ellipse)
        return ellipse

    def add_spline(self, fit_points: Iterable['Vertex'] = None,
                   control_points: Iterable['Vertex'] = None,
                   knot_values: Iterable[float] = None,
                   weights: Iterable[float] = None,
                   degree: int = 3,
                   periodic: int = 0,
                   start_tangent: 'Vertex' = None,
                   end_tangent: 'Vertex' = None,
                   ) -> 'SplineEdge':
        """ Add a :class:`SplineEdge`.

        Args:
            fit_points: points through which the spline must go, at least 3 fit
                points are required. list of (x, y)-tuples
            control_points: affects the shape of the spline, mandatory and
                AutoCAD crashes on invalid data. list of (x, y)-tuples
            knot_values: (knot vector) mandatory and AutoCAD crashes on invalid
                data. list of floats; `ezdxf` provides two tool functions to
                calculate valid knot values: :func:`ezdxf.math.uniform_knot_vector`,
                :func:`ezdxf.math.open_uniform_knot_vector` (default if ``None``)
            weights: weight of control point, not mandatory, list of floats.
            degree: degree of spline (int)
            periodic: 1 for periodic spline, 0 for none periodic spline
            start_tangent: start_tangent as 2d vector, optional
            end_tangent: end_tangent as 2d vector, optional

        .. warning::

            Unlike for the spline entity AutoCAD does not calculate the
            necessary `knot_values` for the spline edge itself. On the contrary,
            if the `knot_values` in the spline edge are missing or invalid
            AutoCAD **crashes**.

        """
        spline = SplineEdge()
        if fit_points is not None:
            spline.fit_points = Vec2.list(fit_points)
        if control_points is not None:
            spline.control_points = Vec2.list(control_points)
        if knot_values is not None:
            spline.knot_values = list(knot_values)
        else:
            spline.knot_values = list(
                open_uniform_knot_vector(len(spline.control_points),
                                         degree + 1))
        if weights is not None:
            spline.weights = list(weights)
        spline.degree = degree
        spline.rational = int(bool(len(spline.weights)))
        spline.periodic = int(periodic)
        if start_tangent is not None:
            spline.start_tangent = Vec2(start_tangent)
        if end_tangent is not None:
            spline.end_tangent = Vec2(end_tangent)
        self.edges.append(spline)
        return spline

    def add_spline_control_frame(self,
                                 fit_points: Iterable[Tuple[float, float]],
                                 degree: int = 3,
                                 method: str = 'distance') -> 'SplineEdge':
        bspline = global_bspline_interpolation(fit_points=fit_points,
                                               degree=degree, method=method)
        return self.add_spline(
            fit_points=fit_points,
            control_points=bspline.control_points,
            knot_values=bspline.knot_values(),
        )

    def clear(self) -> None:
        """ Delete all edges."""
        self.edges = []

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(92, int(self.path_type_flags))
        tagwriter.write_tag2(93, len(self.edges))
        for edge in self.edges:
            edge.export_dxf(tagwriter)
        export_source_boundary_objects(tagwriter, self.source_boundary_objects)


def _transform_2d_ocs_vertices(ucs, vertices, elevation, extrusion) -> List[
    Tuple[float, float]]:
    ocs_vertices = (Vec3(x, y, elevation) for x, y in vertices)
    return [(v.x, v.y) for v in
            ucs.ocs_points_to_ocs(ocs_vertices, extrusion=extrusion)]


class LineEdge:
    EDGE_TYPE = "LineEdge"

    def __init__(self):
        self.start = Vec2((0, 0))
        self.end = Vec2((0, 0))

    @classmethod
    def load_tags(cls, tags: Tags) -> 'LineEdge':
        edge = cls()
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.start = Vec2(value)
            elif code == 11:
                edge.end = Vec2(value)
        return edge

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(72, 1)  # edge type

        x, y, *_ = self.start
        tagwriter.write_tag2(10, float(x))
        tagwriter.write_tag2(20, float(y))

        x, y, *_ = self.end
        tagwriter.write_tag2(11, float(x))
        tagwriter.write_tag2(21, float(y))

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        self.start = ocs.transform_2d_vertex(self.start, elevation)
        self.end = ocs.transform_2d_vertex(self.end, elevation)


class ArcEdge:
    EDGE_TYPE = "ArcEdge"

    def __init__(self):
        self.center = Vec2((0., 0.))
        self.radius: float = 1.
        self.start_angle: float = 0.
        self.end_angle: float = 360.
        self.ccw: bool = True

    @classmethod
    def load_tags(cls, tags: Tags) -> 'ArcEdge':
        edge = cls()
        start = 0.0
        end = 0.0
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.center = Vec2(value)
            elif code == 40:
                edge.radius = value
            elif code == 50:
                start = value
            elif code == 51:
                end = value
            elif code == 73:
                edge.ccw = bool(value)

        # The DXF format stores the clockwise oriented start- and end angles
        # for HATCH arc- and ellipse edges as complementary angle (360-angle).
        # This is a problem in many ways for processing clockwise oriented
        # angles correct, especially rotation transformation won't work.
        # Solution: convert clockwise angles into counter-clockwise angles
        # and swap start- and end angle at loading and exporting:
        if edge.ccw:
            edge.start_angle = start
            edge.end_angle = end
        else:
            edge.start_angle = 360.0 - end
            edge.end_angle = 360.0 - start
        return edge

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(72, 2)  # edge type
        x, y, *_ = self.center
        if self.ccw:
            start = self.start_angle
            end = self.end_angle
        else:
            # swap and convert to complementary angles: see ArcEdge.load_tags()
            # for explanation
            start = 360.0 - self.end_angle
            end = 360.0 - self.start_angle
        tagwriter.write_tag2(10, float(x))
        tagwriter.write_tag2(20, float(y))
        tagwriter.write_tag2(40, self.radius)
        tagwriter.write_tag2(50, start)
        tagwriter.write_tag2(51, end)
        tagwriter.write_tag2(73, int(self.ccw))

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        self.center = ocs.transform_2d_vertex(self.center, elevation)
        self.start_angle = ocs.transform_deg_angle(self.start_angle)
        self.end_angle = ocs.transform_deg_angle(self.end_angle)


class EllipseEdge:
    EDGE_TYPE = "EllipseEdge"

    def __init__(self):
        self.center = Vec2((0., 0.))
        # Endpoint of major axis relative to center point (in OCS)
        self.major_axis = Vec2((1., 0.))
        self.ratio: float = 1.
        self.start_angle: float = 0.  # start param, not a real angle
        self.end_angle: float = 360.  # end param, not a real angle
        self.ccw: bool = True

    @property
    def start_param(self) -> float:
        return angle_to_param(self.ratio, math.radians(self.start_angle))

    @start_param.setter
    def start_param(self, param: float) -> None:
        self.start_angle = math.degrees(param_to_angle(self.ratio, param))

    @property
    def end_param(self) -> float:
        return angle_to_param(self.ratio, math.radians(self.end_angle))

    @end_param.setter
    def end_param(self, param: float) -> None:
        self.end_angle = math.degrees(param_to_angle(self.ratio, param))

    @classmethod
    def load_tags(cls, tags: Tags) -> 'EllipseEdge':
        edge = cls()
        start = 0.0
        end = 0.0
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.center = Vec2(value)
            elif code == 11:
                edge.major_axis = Vec2(value)
            elif code == 40:
                edge.ratio = value
            elif code == 50:
                start = value
            elif code == 51:
                end = value
            elif code == 73:
                edge.ccw = bool(value)

        if edge.ccw:
            edge.start_angle = start
            edge.end_angle = end
        else:
            # swap and convert to complementary angles: see ArcEdge.load_tags()
            # for explanation
            edge.start_angle = 360.0 - end
            edge.end_angle = 360.0 - start

        return edge

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(72, 3)  # edge type
        x, y, *_ = self.center
        tagwriter.write_tag2(10, float(x))
        tagwriter.write_tag2(20, float(y))
        x, y, *_ = self.major_axis
        tagwriter.write_tag2(11, float(x))
        tagwriter.write_tag2(21, float(y))
        tagwriter.write_tag2(40, self.ratio)
        if self.ccw:
            start = self.start_angle
            end = self.end_angle
        else:
            # swap and convert to complementary angles: see ArcEdge.load_tags()
            # for explanation
            start = 360.0 - self.end_angle
            end = 360.0 - self.start_angle

        tagwriter.write_tag2(50, start)
        tagwriter.write_tag2(51, end)
        tagwriter.write_tag2(73, int(self.ccw))

    def construction_tool(self):
        """ Returns ConstructionEllipse() for the OCS representation. """
        return ConstructionEllipse(
            center=Vec3(self.center),
            major_axis=Vec3(self.major_axis),
            extrusion=Vec3(0, 0, 1),
            ratio=self.ratio,
            # ConstructionEllipse() is always in ccw orientation
            start_param=self.start_param if self.ccw else self.end_param,
            end_param=self.end_param if self.ccw else self.start_param,
        )

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        e = self.construction_tool()

        # Transform old OCS representation to WCS
        ocs_to_wcs = ocs.old_ocs.to_wcs
        e.center = ocs_to_wcs(e.center.replace(z=elevation))
        e.major_axis = ocs_to_wcs(e.major_axis)
        e.extrusion = ocs.old_extrusion

        # Apply matrix transformation
        e.transform(ocs.m)

        # Transform WCS representation to new OCS
        wcs_to_ocs = ocs.new_ocs.from_wcs
        self.center = wcs_to_ocs(e.center).vec2
        self.major_axis = wcs_to_ocs(e.major_axis).vec2
        self.ratio = e.ratio

        # ConstructionEllipse() is always in ccw orientation
        self.start_param = e.start_param if self.ccw else e.end_param
        self.end_param = e.end_param if self.ccw else e.start_param

        if ocs.new_extrusion.isclose(e.extrusion, abs_tol=1e-9):
            # ellipse extrusion matches new hatch extrusion
            pass
        elif ocs.new_extrusion.isclose(-e.extrusion, abs_tol=1e-9):
            # ellipse extrusion is opposite to new hatch extrusion
            self.start_angle, self.end_angle = -self.end_angle, -self.start_angle
        else:
            raise ArithmeticError(
                'Invalid EllipseEdge() transformation, please send bug report.')

        # normalize angles in range 0 to 360 degrees
        self.start_angle = self.start_angle % 360.0
        self.end_angle = self.end_angle % 360.0
        if math.isclose(self.end_angle, 0):
            self.end_angle = 360.0


class SplineEdge:
    EDGE_TYPE = "SplineEdge"

    def __init__(self):
        self.degree: int = 3  # code = 94
        self.rational: int = 0  # code = 73
        self.periodic: int = 0  # code = 74
        self.knot_values: List[float] = []
        self.control_points: List[Vec2] = []
        self.fit_points: List[Vec2] = []
        self.weights: List[float] = []
        # do not set tangents by default to (0, 0)
        self.start_tangent: Optional[Vec2] = None
        self.end_tangent: Optional[Vec2] = None

    @classmethod
    def load_tags(cls, tags: Tags) -> 'SplineEdge':
        edge = cls()
        for tag in tags:
            code, value = tag
            if code == 94:
                edge.degree = value
            elif code == 73:
                edge.rational = value
            elif code == 74:
                edge.periodic = value
            elif code == 40:
                edge.knot_values.append(value)
            elif code == 42:
                edge.weights.append(value)
            elif code == 10:
                edge.control_points.append(Vec2(value))
            elif code == 11:
                edge.fit_points.append(Vec2(value))
            elif code == 12:
                edge.start_tangent = Vec2(value)
            elif code == 13:
                edge.end_tangent = Vec2(value)
        return edge

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        if len(self.weights):
            if len(self.weights) == len(self.control_points):
                self.rational = 1
            else:
                raise const.DXFValueError(
                    "SplineEdge: count of control points and count of weights mismatch")
        else:
            self.rational = 0

        write_tag = tagwriter.write_tag2
        write_tag(72, 4)  # edge type
        write_tag(94, int(self.degree))
        write_tag(73, int(self.rational))
        write_tag(74, int(self.periodic))
        write_tag(95, len(self.knot_values))  # number of knots
        write_tag(96, len(self.control_points))  # number of control points
        # build knot values list
        # knot values have to be present and valid, otherwise AutoCAD crashes
        if len(self.knot_values):
            for value in self.knot_values:
                write_tag(40, float(value))
        else:
            raise const.DXFValueError(
                "SplineEdge: missing required knot values")

        # build control points
        # control points have to be present and valid, otherwise AutoCAD crashes
        cp = Vec2.generate(self.control_points)
        if self.rational:
            for point, weight in zip(cp, self.weights):
                write_tag(10, float(point.x))
                write_tag(20, float(point.y))
                write_tag(42, float(weight))
        else:
            for x, y in cp:
                write_tag(10, float(x))
                write_tag(20, float(y))

        # build optional fit points
        if len(self.fit_points) > 0:
            write_tag(97, len(self.fit_points))
            for x, y, *_ in self.fit_points:
                write_tag(11, float(x))
                write_tag(21, float(y))
        elif tagwriter.dxfversion >= DXF2010:
            # (97, 0) len tag required by AutoCAD 2010+
            write_tag(97, 0)

        if self.start_tangent is not None:
            x, y, *_ = self.start_tangent
            write_tag(12, float(x))
            write_tag(22, float(y))

        if self.end_tangent is not None:
            x, y, *_ = self.end_tangent
            write_tag(13, float(x))
            write_tag(23, float(y))

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        self.control_points = list(
            ocs.transform_2d_vertex(v, elevation) for v in self.control_points)
        self.fit_points = list(
            ocs.transform_2d_vertex(v, elevation) for v in self.fit_points)
        if self.start_tangent is not None:
            t = Vec3(self.start_tangent).replace(z=elevation)
            self.start_tangent = ocs.transform_direction(t).vec2
        if self.end_tangent is not None:
            t = Vec3(self.end_tangent).replace(z=elevation)
            self.end_tangent = ocs.transform_direction(t).vec2


EDGE_CLASSES = [None, LineEdge, ArcEdge, EllipseEdge, SplineEdge]
EdgeTypes = Union[LineEdge, ArcEdge, EllipseEdge, SplineEdge]


class Pattern:
    def __init__(self, lines: Iterable['PatternLine'] = None):
        self.lines: List['PatternLine'] = list(lines) if lines else []

    @classmethod
    def load_tags(cls, tags: Tags) -> 'Pattern':
        grouped_line_tags = group_tags(tags, splitcode=53)
        return cls(
            PatternLine.load_tags(line_tags) for line_tags in grouped_line_tags)

    def clear(self) -> None:
        """ Delete all pattern definition lines. """
        self.lines = []

    def add_line(self,
                 angle: float = 0,
                 base_point: 'Vertex' = (0, 0),
                 offset: 'Vertex' = (0, 0),
                 dash_length_items: Iterable[float] = None) -> None:
        """ Create a new pattern definition line and add the line to the
        :attr:`Pattern.lines` attribute.

        """
        assert dash_length_items is not None, "argument 'dash_length_items' is None"
        self.lines.append(
            PatternLine(angle, base_point, offset, dash_length_items))

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        if len(self.lines):
            tagwriter.write_tag2(78, len(self.lines))
            for line in self.lines:
                line.export_dxf(tagwriter)

    def __str__(self) -> str:
        return "[" + ",".join(str(line) for line in self.lines) + "]"

    def as_list(self) -> List:
        return [line.as_list() for line in self.lines]

    def scale(self, factor: float = 1, angle: float = 0) -> None:
        """ Scale and rotate pattern.

        Be careful, this changes the base pattern definition, maybe better use
        :meth:`Hatch.set_pattern_scale` or :meth:`Hatch.set_pattern_angle`.

        Args:
            factor: scaling factor
            angle: rotation angle in degrees

        .. versionadded:: 0.13

        """
        scaled_pattern = pattern.scale_pattern(self.as_list(), factor=factor,
                                               angle=angle)
        self.clear()
        for line in scaled_pattern:
            self.add_line(*line)


class PatternLine:
    def __init__(self,
                 angle: float = 0,
                 base_point: 'Vertex' = (0, 0),
                 offset: 'Vertex' = (0, 0),
                 dash_length_items: Iterable[float] = None):
        self.angle: float = float(angle)  # in degrees
        self.base_point: Vec2 = Vec2(base_point)
        self.offset: Vec2 = Vec2(offset)
        self.dash_length_items: List[
            float] = [] if dash_length_items is None else list(
            dash_length_items)
        # dash_length_items = [item0, item1, ...]
        # item > 0 is line, < 0 is gap, 0.0 = dot;

    @staticmethod
    def load_tags(tags: Tags) -> 'PatternLine':
        p = {53: 0, 43: 0, 44: 0, 45: 0, 46: 0}
        dash_length_items = []
        for tag in tags:
            code, value = tag
            if code == 49:
                dash_length_items.append(value)
            else:
                p[code] = value
        return PatternLine(p[53], (p[43], p[44]), (p[45], p[46]),
                           dash_length_items)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
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
        return "[{0.angle}, {0.base_point}, {0.offset}, {0.dash_length_items}]".format(
            self)

    def as_list(self) -> List:
        return [self.angle, self.base_point, self.offset,
                self.dash_length_items]


class Gradient:
    def __init__(self):
        # 1 for gradient by default, 0 for Solid
        self.kind: int = 1
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
        self.name: str = 'LINEAR'

    @classmethod
    def load_tags(cls, tags: Tags) -> 'Gradient':
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

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        # Tag order matters!
        write_tag = tagwriter.write_tag2
        write_tag(450, self.kind)  # gradient or solid
        write_tag(451, 0)  # reserved for the future

        # rotation angle in radians:
        write_tag(460, math.radians(self.rotation))
        write_tag(461, self.centered)
        write_tag(452, self.one_color)
        write_tag(462, self.tint)
        write_tag(453, 2)  # number of colors
        write_tag(463, 0)  # first value, see DXF standard
        if self.aci1 is not None:
            write_tag(63, self.aci1)
        # code == 63 "color as ACI" can be left off
        write_tag(421, clr.rgb2int(self.color1))  # first color
        write_tag(463, 1)  # second value, see DXF standard
        if self.aci2 is not None:
            write_tag(63, self.aci2)  # code 63 "color as ACI" could be left off
        write_tag(421, clr.rgb2int(self.color2))  # second color
        write_tag(470, self.name)

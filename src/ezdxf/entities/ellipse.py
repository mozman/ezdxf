# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable
import math
from ezdxf.lldxf import validator
from ezdxf.math import (
    Vec3, Matrix44, NULLVEC, X_AXIS, Z_AXIS, ellipse, ConstructionEllipse, OCS
)
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, XType, RETURN_DEFAULT,
    group_code_mapping
)
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity, add_entity, replace_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, Spline

__all__ = ['Ellipse']

MIN_RATIO = 1e-6
MAX_RATIO = 1.0


def is_valid_ratio(ratio: float) -> bool:
    return MIN_RATIO <= abs(ratio) <= MAX_RATIO


def fix_ratio(ratio: float) -> float:
    sign = -1 if ratio < 0 else +1
    ratio = abs(ratio)
    if ratio < MIN_RATIO:
        return MIN_RATIO * sign
    elif ratio > MAX_RATIO:
        return MAX_RATIO * sign
    return ratio * sign


acdb_ellipse = DefSubclass('AcDbEllipse', {
    'center': DXFAttr(10, xtype=XType.point3d, default=NULLVEC),

    # Major axis vector from 'center':
    'major_axis': DXFAttr(
        11, xtype=XType.point3d, default=X_AXIS,
        validator=validator.is_not_null_vector,

    ),

    # The extrusion vector does not establish an OCS, it is just the normal
    # vector of the ellipse plane:
    'extrusion': DXFAttr(
        210, xtype=XType.point3d, default=Z_AXIS,
        optional=True,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),
    # Ratio has to be in the range from 1e-6 to 1, but could be negative:
    'ratio': DXFAttr(
        40, default=MAX_RATIO,
        validator=is_valid_ratio,
        fixer=fix_ratio
    ),
    # Start of ellipse, this value is 0.0 for a full ellipse:
    'start_param': DXFAttr(41, default=0),

    # End of ellipse, this value is 2*pi for a full ellipse:
    'end_param': DXFAttr(42, default=math.tau),
})
acdb_ellipse_group_code = group_code_mapping(acdb_ellipse)
HALF_PI = math.pi / 2.0


@register_entity
class Ellipse(DXFGraphic):
    """ DXF ELLIPSE entity """
    DXFTYPE = 'ELLIPSE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_ellipse)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_ellipse_group_code, 2, recover=True)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_ellipse.name)

        assert is_valid_ratio(self.dxf.ratio)
        self.dxf.export_dxf_attribs(tagwriter, [
            'center', 'major_axis', 'extrusion', 'ratio', 'start_param',
            'end_param',
        ])

    @property
    def minor_axis(self) -> Vec3:
        dxf = self.dxf
        return ellipse.minor_axis(Vec3(dxf.major_axis), Vec3(dxf.extrusion),
                                  dxf.ratio)

    @property
    def start_point(self) -> 'Vec3':
        return list(self.vertices([self.dxf.start_param]))[0]

    @property
    def end_point(self) -> 'Vec3':
        return list(self.vertices([self.dxf.end_param]))[0]

    def construction_tool(self) -> ConstructionEllipse:
        """ Returns construction tool :class:`ezdxf.math.ConstructionEllipse`.
        """
        dxf = self.dxf
        return ConstructionEllipse(
            dxf.center,
            dxf.major_axis,
            dxf.extrusion,
            dxf.ratio,
            dxf.start_param,
            dxf.end_param,
        )

    def apply_construction_tool(self, e: ConstructionEllipse) -> 'Ellipse':
        """ Set ELLIPSE data from construction tool
        :class:`ezdxf.math.ConstructionEllipse`.

        """
        self.update_dxf_attribs(e.dxfattribs())
        return self  # floating interface

    def params(self, num: int) -> Iterable[float]:
        """ Returns `num` params from start- to end param in counter
        clockwise order.

        All params are normalized in the range from [0, 2pi).

        """
        start = self.dxf.start_param % math.tau
        end = self.dxf.end_param % math.tau
        yield from ellipse.get_params(start, end, num)

    def vertices(self, params: Iterable[float]) -> Iterable[Vec3]:
        """ Yields vertices on ellipse for iterable `params` in WCS.

        Args:
            params: param values in the range from ``0`` to ``2*pi`` in radians,
                param goes counter clockwise around the extrusion vector,
                major_axis = local x-axis = 0 rad.

        """
        yield from self.construction_tool().vertices(params)

    def flattening(self, distance: float, segments: int = 8) -> Iterable[Vec3]:
        """ Adaptive recursive flattening. The argument `segments` is the
        minimum count of approximation segments, if the distance from the center
        of the approximation segment to the curve is bigger than `distance` the
        segment will be subdivided. Returns a closed polygon for a full ellipse:
        start vertex == end vertex.

        Args:
            distance: maximum distance from the projected curve point onto the
                segment chord.
            segments: minimum segment count

        .. versionadded:: 0.15

        """
        return self.construction_tool().flattening(distance, segments)

    def swap_axis(self):
        """ Swap axis and adjust start- and end parameter. """
        e = self.construction_tool()
        e.swap_axis()
        self.update_dxf_attribs(e.dxfattribs())

    @classmethod
    def from_arc(cls, entity: 'DXFGraphic') -> 'Ellipse':
        """ Create a new ELLIPSE entity from ARC or CIRCLE entity.

        The new SPLINE entity has no owner, no handle, is not stored in
        the entity database nor assigned to any layout!

        """
        assert entity.dxftype() in {'ARC', 'CIRCLE'}
        attribs = entity.dxfattribs(drop={'owner', 'handle', 'thickness'})
        e = ellipse.ConstructionEllipse.from_arc(
            center=attribs.get('center', NULLVEC),
            extrusion=attribs.get('extrusion', Z_AXIS),
            # Remove all not ELLIPSE attributes:
            radius=attribs.pop('radius', 1.0),
            start_angle=attribs.pop('start_angle', 0),
            end_angle=attribs.pop('end_angle', 360),
        )
        attribs.update(e.dxfattribs())
        return Ellipse.new(dxfattribs=attribs, doc=entity.doc)

    def transform(self, m: Matrix44) -> 'Ellipse':
        """ Transform the ELLIPSE entity by transformation matrix `m` inplace.
        """
        e = self.construction_tool()
        e.transform(m)
        self.update_dxf_attribs(e.dxfattribs())
        return self

    def translate(self, dx: float, dy: float, dz: float) -> 'Ellipse':
        """ Optimized ELLIPSE translation about `dx` in x-axis, `dy` in y-axis
        and `dz` in z-axis, returns `self` (floating interface).

        """
        self.dxf.center = Vec3(dx, dy, dz) + self.dxf.center
        return self

    def to_spline(self, replace=True) -> 'Spline':
        """ Convert ELLIPSE to a :class:`~ezdxf.entities.Spline` entity.

        Adds the new SPLINE entity to the entity database and to the
        same layout as the source entity.

        Args:
            replace: replace (delete) source entity by SPLINE entity if ``True``

        """
        from ezdxf.entities import Spline
        spline = Spline.from_arc(self)
        layout = self.get_layout()

        if replace:
            replace_entity(self, spline, layout)
        else:
            add_entity(spline, layout)
        return spline

    def ocs(self) -> OCS:
        # WCS entity which supports the "extrusion" attribute in a
        # different way!
        return OCS()

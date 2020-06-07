# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Iterable
import math

from ezdxf.math import Vector, Matrix44, NULLVEC, Z_AXIS, ConstructionEllipse
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000
from ezdxf.math import ellipse
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['Ellipse']

acdb_ellipse = DefSubclass('AcDbEllipse', {
    'center': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),
    'major_axis': DXFAttr(11, xtype=XType.point3d, default=Vector(1, 0, 0)),  # relative to the center
    # extrusion does not establish an OCS, it is just the normal vector of the ellipse plane.
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=(0, 0, 1), optional=True),
    'ratio': DXFAttr(40, default=1),  # has to be in range 1e-6 to 1
    'start_param': DXFAttr(41, default=0),  # this value is 0.0 for a full ellipse
    'end_param': DXFAttr(42, default=math.tau),  # this value is 2*pi for a full ellipse
})

HALF_PI = math.pi / 2.0


@register_entity
class Ellipse(DXFGraphic):
    """ DXF ELLIPSE entity """
    DXFTYPE = 'ELLIPSE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_ellipse)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_ellipse)
            if len(tags):
                processor.log_unprocessed_tags(tags, subclass=acdb_ellipse.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_ellipse.name)

        # AutoCAD does not accept a ratio < 1e-6 -> invalid DXF file
        self.dxf.ratio = max(self.dxf.ratio, 1e-6)
        self.dxf.export_dxf_attribs(tagwriter, [
            'center', 'major_axis', 'extrusion', 'ratio', 'start_param', 'end_param',
        ])

    @property
    def minor_axis(self) -> Vector:
        dxf = self.dxf
        return ellipse.minor_axis(Vector(dxf.major_axis), Vector(dxf.extrusion), dxf.ratio)

    @property
    def start_point(self) -> 'Vector':
        return list(self.vertices([self.dxf.start_param]))[0]

    @property
    def end_point(self) -> 'Vector':
        return list(self.vertices([self.dxf.end_param]))[0]

    def construction_tool(self) -> ConstructionEllipse:
        """
        Returns construction tool :class:`ezdxf.math.ConstructionEllipse`.

        .. versionadded:: 0.13

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

    def apply_construction_tool(self, e: ConstructionEllipse) -> None:
        """
        Set ELLIPSE data from construction tool :class:`ezdxf.math.ConstructionEllipse`.

        .. versionadded:: 0.13

        """
        self.update_dxf_attribs(e.dxfattribs())

    def params(self, num: int) -> Iterable[float]:
        """ Returns `num` params from start- to end param in counter clockwise order.

        All params are normalized in the range from [0, 2pi).

        """
        start = self.dxf.start_param % math.tau
        end = self.dxf.end_param % math.tau
        yield from ellipse.get_params(start, end, num)

    def vertices(self, params: Iterable[float]) -> Iterable[Vector]:
        """
        Yields vertices on ellipse for iterable `params` in WCS.

        Args:
            params: param values in the range from ``0`` to ``2*pi`` in radians, param goes counter clockwise around the
                    extrusion vector, major_axis = local x-axis = 0 rad.

        .. versionadded:: 0.11

        """
        yield from self.construction_tool().vertices(params)

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

        .. versionadded:: 0.13

        """
        assert entity.dxftype() in {'ARC', 'CIRCLE'}
        attribs = entity.dxfattribs(drop={'owner', 'handle', 'thickness'})
        e = ellipse.ConstructionEllipse.from_arc(
            center=attribs.get('center', NULLVEC),
            radius=attribs.pop('radius', 1.0),  # not an ELLIPSE attribute
            extrusion=attribs.get('extrusion', Z_AXIS),
            start_angle=attribs.pop('start_angle', 0),  # not an ELLIPSE attribute
            end_angle=attribs.pop('end_angle', 360)  # not an ELLIPSE attribute
        )
        attribs.update(e.dxfattribs())
        return Ellipse.new(dxfattribs=attribs, doc=entity.doc)

    def transform(self, m: Matrix44) -> 'Ellipse':
        """ Transform ELLIPSE entity by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        e = self.construction_tool()
        e.transform(m)
        self.update_dxf_attribs(e.dxfattribs())
        return self

    def translate(self, dx: float, dy: float, dz: float) -> 'Ellipse':
        """ Optimized ELLIPSE translation about `dx` in x-axis, `dy` in y-axis and `dz` in z-axis,
        returns `self` (floating interface).

        .. versionadded:: 0.13

        """
        self.dxf.center = Vector(dx, dy, dz) + self.dxf.center
        return self

# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Iterable
import math
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, UCS

__all__ = ['Ellipse']


acdb_ellipse = DefSubclass('AcDbEllipse', {
    'center': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),
    'major_axis': DXFAttr(11, xtype=XType.point3d, default=Vector(1, 0, 0)),  # relative to the center
    # extrusion does not establish an OCS, it is just the normal vector of the ellipse plane.
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=(0, 0, 1), optional=True),
    'ratio': DXFAttr(40, default=1),
    'start_param': DXFAttr(41, default=0),  # this value is 0.0 for a full ellipse
    'end_param': DXFAttr(42, default=math.pi*2),  # this value is 2*pi for a full ellipse
})


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
        self.dxf.export_dxf_attribs(tagwriter, [
            'center', 'major_axis', 'extrusion', 'ratio', 'start_param', 'end_param',
        ])

    def vertices(self, params: Iterable[float]) -> Iterable[Vector]:
        """
        Yields vertices on ellipse for iterable `params` in WCS.

        Args:
            params: param values in the range from ``0`` to ``2*pi`` in radians, param goes counter clockwise around the
                    extrusion vector, major_axis = local x-axis = 0 rad.

        .. versionadded:: 0.11

        """
        # get main axis
        major_axis = Vector(self.dxf.major_axis)  # local x-axis, 0 rad
        extrusion = Vector(self.dxf.extrusion)  # local z-axis, normal vector of the ellipse plane
        minor_axis = extrusion.cross(major_axis)  # local y-axis, pi/2 rad, need only normalized direction

        # normal vectors for local x- and y-axis
        x_axis = major_axis.normalize()
        y_axis = minor_axis.normalize()

        # point on ellipse calculation
        radius_x = major_axis.magnitude
        radius_y = radius_x * self.dxf.ratio
        center = Vector(self.dxf.center)
        for param in params:
            # Ellipse params in radians by definition (DXF Reference)
            x = math.cos(param) * radius_x
            y = math.sin(param) * radius_y

            # construct WCS coordinates, do not convert from OCS to WCS, extrusion defines only the normal vector of
            # the ellipse plane.
            yield center + (x_axis * x) + (y_axis * y)

    @property
    def start_point(self) -> 'Vector':
        v = list(self.vertices([self.dxf.start_param]))
        return v[0]

    @property
    def end_point(self) -> 'Vector':
        v = list(self.vertices([self.dxf.end_param]))
        return v[0]

    def transform_to_wcs(self, ucs: 'UCS') -> None:
        """ Transform ELLIPSE entity from local :class:`~ezdxf.math.UCS` coordinates to
        :ref:`WCS` coordinates.

        .. versionadded:: 0.11

        """
        # Ellipse is an real 3d entity without OCS
        self.dxf.center = ucs.to_wcs(self.dxf.center)
        self.dxf.major_axis = ucs.to_wcs(self.dxf.major_axis)
        self.dxf.extrusion = ucs.to_wcs(self.dxf.extrusion)

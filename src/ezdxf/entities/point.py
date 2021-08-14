# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List
from ezdxf.lldxf import validator
from ezdxf.lldxf.attributes import (
    DXFAttr,
    DXFAttributes,
    DefSubclass,
    XType,
    RETURN_DEFAULT,
    group_code_mapping,
)
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from ezdxf.math import Vec3, Matrix44, NULLVEC, Z_AXIS, OCS
from ezdxf.math.transformtools import (
    transform_thickness_and_extrusion_without_ocs,
)
from ezdxf.render import point
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ["Point"]

# Point styling is a global setting, stored in the HEADER section as:
# $PDMODE: https://knowledge.autodesk.com/support/autocad/learn-explore/caas/CloudHelp/cloudhelp/2019/ENU/AutoCAD-Core/files/GUID-82F9BB52-D026-4D6A-ABA6-BF29641F459B-htm.html
# One of these values
#   0 = center dot (.)
#   1 = none ( )
#   2 = cross (+)
#   3 = x-cross (x)
#   4 = tick (')
# Combined with these bit values
#  32 = circle
#  64 = Square
#
# e.g. circle + square+center dot = 32 + 64 + 0 = 96
#
# $PDSIZE: https://knowledge.autodesk.com/support/autocad/learn-explore/caas/CloudHelp/cloudhelp/2021/ENU/AutoCAD-Core/files/GUID-826CA91D-704B-400B-B784-7FCC9619AFB9-htm.html?st=$PDSIZE
#  0 = 5% of draw area height
# <0 = Specifies a percentage of the viewport size
# >0 = Specifies an absolute size

acdb_point = DefSubclass(
    "AcDbPoint",
    {
        # Point location:
        "location": DXFAttr(10, xtype=XType.point3d, default=NULLVEC),
        # Thickness could be negative:
        "thickness": DXFAttr(39, default=0, optional=True),
        "extrusion": DXFAttr(
            210,
            xtype=XType.point3d,
            default=Z_AXIS,
            optional=True,
            validator=validator.is_not_null_vector,
            fixer=RETURN_DEFAULT,
        ),
        # angle of the x-axis for the UCS in effect when the point was drawn;
        # used when PDMODE is nonzero:
        "angle": DXFAttr(50, default=0, optional=True),
    },
)
acdb_point_group_codes = group_code_mapping(acdb_point)


@register_entity
class Point(DXFGraphic):
    """DXF POINT entity"""

    DXFTYPE = "POINT"
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_point)

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        """Loading interface. (internal API)"""
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_point_group_codes, 2, recover=True
            )
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags. (internal API)"""
        super().export_entity(tagwriter)
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_point.name)
        self.dxf.export_dxf_attribs(
            tagwriter, ["location", "thickness", "extrusion", "angle"]
        )

    def transform(self, m: Matrix44) -> "Point":
        """Transform the POINT entity by transformation matrix `m` inplace."""
        self.dxf.location = m.transform(self.dxf.location)
        transform_thickness_and_extrusion_without_ocs(self, m)
        # ignore dxf.angle!
        return self

    def translate(self, dx: float, dy: float, dz: float) -> "Point":
        """Optimized POINT translation about `dx` in x-axis, `dy` in y-axis and
        `dz` in z-axis.
        """
        self.dxf.location = Vec3(dx, dy, dz) + self.dxf.location
        return self

    def virtual_entities(
        self, pdsize: float = 1, pdmode: int = 0
    ) -> List["DXFGraphic"]:
        """Yields point graphic as DXF primitives LINE and CIRCLE entities.
        The dimensionless point is rendered as zero-length line!

        Check for this condition::

            e.dxftype() == 'LINE' and e.dxf.start.isclose(e.dxf.end)

        if the rendering engine can't handle zero-length lines.

        Args:
            pdsize: point size in drawing units
            pdmode: point styling mode

        .. versionadded:: 0.15

        """
        return point.virtual_entities(self, pdsize, pdmode)

    def ocs(self) -> OCS:
        # WCS entity which supports the "extrusion" attribute in a
        # different way!
        return OCS()

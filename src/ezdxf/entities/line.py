# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
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
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ["Line"]

acdb_line = DefSubclass(
    "AcDbLine",
    {
        "start": DXFAttr(10, xtype=XType.point3d, default=NULLVEC),
        "end": DXFAttr(11, xtype=XType.point3d, default=NULLVEC),
        "thickness": DXFAttr(39, default=0, optional=True),
        "extrusion": DXFAttr(
            210,
            xtype=XType.point3d,
            default=Z_AXIS,
            optional=True,
            validator=validator.is_not_null_vector,
            fixer=RETURN_DEFAULT,
        ),
    },
)

acdb_line_group_codes = group_code_mapping(acdb_line)


@register_entity
class Line(DXFGraphic):
    """The LINE entity represents a 3D line from `start` to `end`"""

    DXFTYPE = "LINE"
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_line)

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        """Adds subclass processing for 'AcDbLine', requires previous base
        class and 'AcDbEntity' processing by parent class. (internal API)

        """
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_line_group_codes, subclass=2, recover=True
            )
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags. (internal API)"""
        super().export_entity(tagwriter)
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_line.name)
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "start",
                "end",
                "thickness",
                "extrusion",
            ],
        )

    def ocs(self) -> OCS:
        # WCS entity which supports the "extrusion" attribute in a
        # different way!
        return OCS()

    def transform(self, m: Matrix44) -> "Line":
        """Transform the LINE entity by transformation matrix `m` inplace."""
        start, end = m.transform_vertices([self.dxf.start, self.dxf.end])
        self.dxf.start = start
        self.dxf.end = end
        transform_thickness_and_extrusion_without_ocs(self, m)
        self.post_transform(m)
        return self

    def translate(self, dx: float, dy: float, dz: float) -> "Line":
        """Optimized LINE translation about `dx` in x-axis, `dy` in y-axis and
        `dz` in z-axis.

        """
        vec = Vec3(dx, dy, dz)
        self.dxf.start = vec + self.dxf.start
        self.dxf.end = vec + self.dxf.end
        # Avoid Matrix44 instantiation if not required:
        if self.is_post_transform_required:
            self.post_transform(Matrix44.translate(dx, dy, dz))
        return self

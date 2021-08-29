# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List, Union
from ezdxf.lldxf.attributes import (
    DXFAttr,
    DXFAttributes,
    DefSubclass,
    XType,
    group_code_mapping,
)
from ezdxf.lldxf.const import (
    SUBCLASS_MARKER,
    DXF2000,
    DXFTypeError,
    DXF2013,
    DXFStructureError,
)
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.math import Matrix44
from ezdxf.tools import crypt
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = [
    "Body",
    "Solid3d",
    "Region",
    "Surface",
    "ExtrudedSurface",
    "LoftedSurface",
    "RevolvedSurface",
    "SweptSurface",
]

acdb_modeler_geometry = DefSubclass(
    "AcDbModelerGeometry",
    {
        "version": DXFAttr(70, default=1),
        "flags": DXFAttr(290, dxfversion=DXF2013),
        "uid": DXFAttr(2, dxfversion=DXF2013),
    },
)
acdb_modeler_geometry_group_codes = group_code_mapping(acdb_modeler_geometry)

# with R2013/AC1027 Modeler Geometry of ACIS data is stored in the ACDSDATA
# section as binary encoded information detection:
# group code 70, 1, 3 is missing
# group code 290, 2 present
#
#   0
# ACDSRECORD
#  90
# 1
#   2
# AcDbDs::ID
# 280
# 10
# 320
# 19B   <<< handle of associated 3DSOLID entity in model space
#   2
# ASM_Data
# 280
# 15
#  94
# 7197  <<< size in bytes ???
# 310
# 414349532042696E61727946696C6...

ACIS_DATA = Union[List[str], List[bytes]]


@register_entity
class Body(DXFGraphic):
    """DXF BODY entity - container entity for embedded ACIS data."""

    DXFTYPE = "BODY"
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_modeler_geometry)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self):
        super().__init__()
        self._acis_data: ACIS_DATA = []

    @property
    def acis_data(self) -> ACIS_DATA:
        """Get ACIS text data as list of strings for DXF R2000 to DXF R2010 and
        binary encoded ACIS data for DXF R2013 and later as list of bytes.

        """
        if self.doc is not None and self.has_binary_data:
            return self.doc.acdsdata.get_acis_data(self.dxf.handle)
        else:
            return self._acis_data

    @acis_data.setter
    def acis_data(self, lines: Iterable[str]):
        """Set ACIS data as list of strings for DXF R2000 to DXF R2010. In case
        of DXF R2013 and later, setting ACIS data as binary data is not
        supported.

        """
        if self.has_binary_data:
            raise DXFTypeError(
                "Setting ACIS data not supported for DXF R2013 and later."
            )
        else:
            self._acis_data = list(lines)

    @property
    def has_binary_data(self):
        """Returns ``True`` if ACIS data is of type ``List[bytes]``, ``False``
        if data is of type ``List[str]``.
        """
        if self.doc:
            return self.doc.dxfversion >= DXF2013
        else:
            return False

    def copy(self):
        """Prevent copying. (internal interface)"""
        raise DXFTypeError("Copying of ACIS data not supported.")

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        """Loading interface. (internal API)"""
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_modeler_geometry_group_codes, 2, log=False
            )
            if not self.has_binary_data:
                self.load_acis_data(processor.subclasses[2])
        return dxf

    def load_acis_data(self, tags: Tags):
        """Loading interface. (internal API)"""
        text_lines = tags2textlines(tag for tag in tags if tag.code in (1, 3))
        self.acis_data = crypt.decode(text_lines)  # type: ignore

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags. (internal API)"""
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_modeler_geometry.name)
        if tagwriter.dxfversion >= DXF2013:
            # ACIS data stored in the ACDSDATA section as binary encoded
            # information.
            if self.dxf.hasattr("version"):
                tagwriter.write_tag2(70, self.dxf.version)
            self.dxf.export_dxf_attribs(tagwriter, ["flags", "uid"])
        else:
            # DXF R2000 - R2013 stores ACIS data as text in entity
            self.dxf.export_dxf_attribs(tagwriter, "version")
            self.export_acis_data(tagwriter)

    def export_acis_data(self, tagwriter: "TagWriter") -> None:
        """Export ACIS data as DXF tags. (internal API)"""

        def cleanup(lines):
            for line in lines:
                yield line.rstrip().replace("\n", "")

        tags = Tags(textlines2tags(crypt.encode(cleanup(self.acis_data))))
        tagwriter.write_tags(tags)

    def set_text(self, text: str, sep: str = "\n") -> None:
        """Set ACIS data from one string."""
        self.acis_data = text.split(sep)

    def tostring(self) -> str:
        """Returns ACIS data as one string for DXF R2000 to R2010."""
        if self.has_binary_data:
            return ""
        else:
            return "\n".join(self.acis_data)  # type: ignore

    def tobytes(self) -> bytes:
        """Returns ACIS data as joined bytes for DXF R2013 and later."""
        if self.has_binary_data:
            return b"".join(self.acis_data)  # type: ignore
        else:
            return b""


def tags2textlines(tags: Iterable) -> Iterable[str]:
    """Yields text lines from code 1 and 3 tags, code 1 starts a line following
    code 3 tags are appended to the line.
    """
    line = None
    for code, value in tags:
        if code == 1:
            if line is not None:
                yield line
            line = value
        elif code == 3:
            line += value
    if line is not None:
        yield line


def textlines2tags(lines: Iterable[str]) -> Iterable[DXFTag]:
    """Yields text lines as DXFTags, splitting long lines (>255) int code 1
    and code 3 tags.
    """
    for line in lines:
        text = line[:255]
        tail = line[255:]
        yield DXFTag(1, text)
        while len(tail):
            text = tail[:255]
            tail = tail[255:]
            yield DXFTag(3, text)


@register_entity
class Region(Body):
    """DXF REGION entity - container entity for embedded ACIS data."""

    DXFTYPE = "REGION"


acdb_3dsolid = DefSubclass(
    "AcDb3dSolid",
    {
        "history_handle": DXFAttr(350, default="0"),
    },
)
acdb_3dsolid_group_codes = group_code_mapping(acdb_3dsolid)


@register_entity
class Solid3d(Body):
    """DXF 3DSOLID entity - container entity for embedded ACIS data."""

    DXFTYPE = "3DSOLID"
    DXFATTRIBS = DXFAttributes(
        base_class, acdb_entity, acdb_modeler_geometry, acdb_3dsolid
    )

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(dxf, acdb_3dsolid_group_codes, 3)
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        # AcDbModelerGeometry export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_3dsolid.name)
        self.dxf.export_dxf_attribs(tagwriter, "history_handle")


def load_matrix(subclass: "Tags", code: int) -> Matrix44:
    values = [tag.value for tag in subclass.find_all(code)]
    if len(values) != 16:
        raise DXFStructureError("Invalid transformation matrix.")
    return Matrix44(values)


def export_matrix(tagwriter: "TagWriter", code: int, matrix: Matrix44) -> None:
    for value in list(matrix):
        tagwriter.write_tag2(code, value)


acdb_surface = DefSubclass(
    "AcDbSurface",
    {
        "u_count": DXFAttr(71),
        "v_count": DXFAttr(72),
    },
)
acdb_surface_group_codes = group_code_mapping(acdb_surface)


@register_entity
class Surface(Body):
    """DXF SURFACE entity - container entity for embedded ACIS data."""

    DXFTYPE = "SURFACE"
    DXFATTRIBS = DXFAttributes(
        base_class, acdb_entity, acdb_modeler_geometry, acdb_surface
    )

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(dxf, acdb_surface_group_codes, 3)
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        # AcDbModelerGeometry export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_surface.name)
        self.dxf.export_dxf_attribs(tagwriter, ["u_count", "v_count"])


acdb_extruded_surface = DefSubclass(
    "AcDbExtrudedSurface",
    {
        "class_id": DXFAttr(90),
        "sweep_vector": DXFAttr(10, xtype=XType.point3d),
        # 16x group code 40: Transform matrix of extruded entity (16 floats;
        # row major format; default = identity matrix)
        "draft_angle": DXFAttr(42, default=0.0),  # in radians
        "draft_start_distance": DXFAttr(43, default=0.0),
        "draft_end_distance": DXFAttr(44, default=0.0),
        "twist_angle": DXFAttr(45, default=0.0),  # in radians?
        "scale_factor": DXFAttr(48, default=0.0),
        "align_angle": DXFAttr(49, default=0.0),  # in radians
        # 16x group code 46: Transform matrix of sweep entity (16 floats;
        # row major format; default = identity matrix)
        # 16x group code 47: Transform matrix of path entity (16 floats;
        # row major format; default = identity matrix)
        "solid": DXFAttr(290, default=0),  # bool
        # 0=No alignment; 1=Align sweep entity to path:
        "sweep_alignment_flags": DXFAttr(70, default=0),
        "unknown1": DXFAttr(71, default=0),
        # 2=Translate sweep entity to path; 3=Translate path to sweep entity:
        "align_start": DXFAttr(292, default=0),  # bool
        "bank": DXFAttr(293, default=0),  # bool
        "base_point_set": DXFAttr(294, default=0),  # bool
        "sweep_entity_transform_computed": DXFAttr(295, default=0),  # bool
        "path_entity_transform_computed": DXFAttr(296, default=0),  # bool
        "reference_vector_for_controlling_twist": DXFAttr(
            11, xtype=XType.point3d
        ),
    },
)
acdb_extruded_surface_group_codes = group_code_mapping(acdb_extruded_surface)


@register_entity
class ExtrudedSurface(Surface):
    """DXF EXTRUDEDSURFACE entity - container entity for embedded ACIS data."""

    DXFTYPE = "EXTRUDEDSURFACE"
    DXFATTRIBS = DXFAttributes(
        base_class,
        acdb_entity,
        acdb_modeler_geometry,
        acdb_surface,
        acdb_extruded_surface,
    )

    def __init__(self):
        super().__init__()
        self.transformation_matrix_extruded_entity = Matrix44()
        self.sweep_entity_transformation_matrix = Matrix44()
        self.path_entity_transformation_matrix = Matrix44()

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_extruded_surface_group_codes, 4, log=False
            )
            self.load_matrices(processor.subclasses[4])
        return dxf

    def load_matrices(self, tags: Tags):
        self.transformation_matrix_extruded_entity = load_matrix(tags, code=40)
        self.sweep_entity_transformation_matrix = load_matrix(tags, code=46)
        self.path_entity_transformation_matrix = load_matrix(tags, code=47)

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        # AcDbModelerGeometry export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_extruded_surface.name)
        self.dxf.export_dxf_attribs(tagwriter, ["class_id", "sweep_vector"])
        export_matrix(
            tagwriter,
            code=40,
            matrix=self.transformation_matrix_extruded_entity,
        )
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "draft_angle",
                "draft_start_distance",
                "draft_end_distance",
                "twist_angle",
                "scale_factor",
                "align_angle",
            ],
        )
        export_matrix(
            tagwriter, code=46, matrix=self.sweep_entity_transformation_matrix
        )
        export_matrix(
            tagwriter, code=47, matrix=self.path_entity_transformation_matrix
        )
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "solid",
                "sweep_alignment_flags",
                "unknown1",
                "align_start",
                "bank",
                "base_point_set",
                "sweep_entity_transform_computed",
                "path_entity_transform_computed",
                "reference_vector_for_controlling_twist",
            ],
        )


acdb_lofted_surface = DefSubclass(
    "AcDbLoftedSurface",
    {
        # 16x group code 40: Transform matrix of loft entity (16 floats;
        # row major format; default = identity matrix)
        "plane_normal_lofting_type": DXFAttr(70),
        "start_draft_angle": DXFAttr(41, default=0.0),  # in radians
        "end_draft_angle": DXFAttr(42, default=0.0),  # in radians
        "start_draft_magnitude": DXFAttr(43, default=0.0),
        "end_draft_magnitude": DXFAttr(44, default=0.0),
        "arc_length_parameterization": DXFAttr(290, default=0),  # bool
        "no_twist": DXFAttr(291, default=1),  # true/false
        "align_direction": DXFAttr(292, default=1),  # bool
        "simple_surfaces": DXFAttr(293, default=1),  # bool
        "closed_surfaces": DXFAttr(294, default=0),  # bool
        "solid": DXFAttr(295, default=0),  # true/false
        "ruled_surface": DXFAttr(296, default=0),  # bool
        "virtual_guide": DXFAttr(297, default=0),  # bool
    },
)
acdb_lofted_surface_group_codes = group_code_mapping(acdb_lofted_surface)


@register_entity
class LoftedSurface(Surface):
    """DXF LOFTEDSURFACE entity - container entity for embedded ACIS data."""

    DXFTYPE = "LOFTEDSURFACE"
    DXFATTRIBS = DXFAttributes(
        base_class,
        acdb_entity,
        acdb_modeler_geometry,
        acdb_surface,
        acdb_lofted_surface,
    )

    def __init__(self):
        super().__init__()
        self.transformation_matrix_lofted_entity = Matrix44()

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_lofted_surface_group_codes, 4, log=False
            )
            self.load_matrices(processor.subclasses[4])
        return dxf

    def load_matrices(self, tags: Tags):
        self.transformation_matrix_lofted_entity = load_matrix(tags, code=40)

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        # AcDbModelerGeometry export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_lofted_surface.name)
        export_matrix(
            tagwriter, code=40, matrix=self.transformation_matrix_lofted_entity
        )
        self.dxf.export_dxf_attribs(
            tagwriter, acdb_lofted_surface.attribs.keys()
        )


acdb_revolved_surface = DefSubclass(
    "AcDbRevolvedSurface",
    {
        "class_id": DXFAttr(90, default=0.0),
        "axis_point": DXFAttr(10, xtype=XType.point3d),
        "axis_vector": DXFAttr(11, xtype=XType.point3d),
        "revolve_angle": DXFAttr(40),  # in radians
        "start_angle": DXFAttr(41),  # in radians
        # 16x group code 42: Transform matrix of revolved entity (16 floats;
        # row major format; default = identity matrix)
        "draft_angle": DXFAttr(43),  # in radians
        "start_draft_distance": DXFAttr(44, default=0),
        "end_draft_distance": DXFAttr(45, default=0),
        "twist_angle": DXFAttr(46, default=0),  # in radians
        "solid": DXFAttr(290, default=0),  # bool
        "close_to_axis": DXFAttr(291, default=0),  # bool
    },
)
acdb_revolved_surface_group_codes = group_code_mapping(acdb_revolved_surface)


@register_entity
class RevolvedSurface(Surface):
    """DXF REVOLVEDSURFACE entity - container entity for embedded ACIS data."""

    DXFTYPE = "REVOLVEDSURFACE"
    DXFATTRIBS = DXFAttributes(
        base_class,
        acdb_entity,
        acdb_modeler_geometry,
        acdb_surface,
        acdb_revolved_surface,
    )

    def __init__(self):
        super().__init__()
        self.transformation_matrix_revolved_entity = Matrix44()

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_revolved_surface_group_codes, 4, log=False
            )
            self.load_matrices(processor.subclasses[4])
        return dxf

    def load_matrices(self, tags: Tags):
        self.transformation_matrix_revolved_entity = load_matrix(tags, code=42)

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        # AcDbModelerGeometry export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_revolved_surface.name)
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "class_id",
                "axis_point",
                "axis_vector",
                "revolve_angle",
                "start_angle",
            ],
        )
        export_matrix(
            tagwriter,
            code=42,
            matrix=self.transformation_matrix_revolved_entity,
        )
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "draft_angle",
                "start_draft_distance",
                "end_draft_distance",
                "twist_angle",
                "solid",
                "close_to_axis",
            ],
        )


acdb_swept_surface = DefSubclass(
    "AcDbSweptSurface",
    {
        "swept_entity_id": DXFAttr(90),
        # 90: size of binary data (lost on saving)
        # 310: binary data  (lost on saving)
        "path_entity_id": DXFAttr(91),
        # 90: size of binary data  (lost on saving)
        # 310: binary data  (lost on saving)
        # 16x group code 40: Transform matrix of sweep entity (16 floats;
        # row major format; default = identity matrix)
        # 16x group code 41: Transform matrix of path entity (16 floats;
        # row major format; default = identity matrix)
        "draft_angle": DXFAttr(42),  # in radians
        "draft_start_distance": DXFAttr(43, default=0),
        "draft_end_distance": DXFAttr(44, default=0),
        "twist_angle": DXFAttr(45, default=0),  # in radians
        "scale_factor": DXFAttr(48, default=1),
        "align_angle": DXFAttr(49, default=0),  # in radians
        # don't know the meaning of this matrices
        # 16x group code 46: Transform matrix of sweep entity (16 floats;
        # row major format; default = identity matrix)
        # 16x group code 47: Transform matrix of path entity (16 floats;
        # row major format; default = identity matrix)
        "solid": DXFAttr(290, default=0),  # in radians
        # 0=No alignment; 1= align sweep entity to path:
        "sweep_alignment": DXFAttr(70, default=0),
        "unknown1": DXFAttr(71, default=0),
        # 2=Translate sweep entity to path; 3=Translate path to sweep entity:
        "align_start": DXFAttr(292, default=0),  # bool
        "bank": DXFAttr(293, default=0),  # bool
        "base_point_set": DXFAttr(294, default=0),  # bool
        "sweep_entity_transform_computed": DXFAttr(295, default=0),  # bool
        "path_entity_transform_computed": DXFAttr(296, default=0),  # bool
        "reference_vector_for_controlling_twist": DXFAttr(
            11, xtype=XType.point3d
        ),
    },
)
acdb_swept_surface_group_codes = group_code_mapping(acdb_swept_surface)


@register_entity
class SweptSurface(Surface):
    """DXF SWEPTSURFACE entity - container entity for embedded ACIS data."""

    DXFTYPE = "SWEPTSURFACE"
    DXFATTRIBS = DXFAttributes(
        base_class,
        acdb_entity,
        acdb_modeler_geometry,
        acdb_surface,
        acdb_swept_surface,
    )

    def __init__(self):
        super().__init__()
        self.transformation_matrix_sweep_entity = Matrix44()
        self.transformation_matrix_path_entity = Matrix44()
        self.sweep_entity_transformation_matrix = Matrix44()
        self.path_entity_transformation_matrix = Matrix44()

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_swept_surface_group_codes, 4, log=False
            )
            self.load_matrices(processor.subclasses[4])
        return dxf

    def load_matrices(self, tags: Tags):
        self.transformation_matrix_sweep_entity = load_matrix(tags, code=40)
        self.transformation_matrix_path_entity = load_matrix(tags, code=41)
        self.sweep_entity_transformation_matrix = load_matrix(tags, code=46)
        self.path_entity_transformation_matrix = load_matrix(tags, code=47)

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        # AcDbModelerGeometry export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_swept_surface.name)
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "swept_entity_id",
                "path_entity_id",
            ],
        )
        export_matrix(
            tagwriter, code=40, matrix=self.transformation_matrix_sweep_entity
        )
        export_matrix(
            tagwriter, code=41, matrix=self.transformation_matrix_path_entity
        )
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "draft_angle",
                "draft_start_distance",
                "draft_end_distance",
                "twist_angle",
                "scale_factor",
                "align_angle",
            ],
        )

        export_matrix(
            tagwriter, code=46, matrix=self.sweep_entity_transformation_matrix
        )
        export_matrix(
            tagwriter, code=47, matrix=self.path_entity_transformation_matrix
        )
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "solid",
                "sweep_alignment",
                "unknown1",
                "align_start",
                "bank",
                "base_point_set",
                "sweep_entity_transform_computed",
                "path_entity_transform_computed",
                "reference_vector_for_controlling_twist",
            ],
        )

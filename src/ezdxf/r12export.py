#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
"""
Module to export any DXF document as DXF version R12 without modifying the source
document.

---------------------------------------------------------
WARNING: THIS MODULE IS IN PLANNING STATE, DO NOT USE IT!
---------------------------------------------------------

"""

from __future__ import annotations
from typing import TYPE_CHECKING, TextIO, Callable
import os

from ezdxf import const
from ezdxf.document import Drawing
from ezdxf.entities import (
    BlockRecord,
    Insert,
    DXFEntity,
    DXFGraphic,
    LWPolyline,
    Polyline,
    Polyface,
    Mesh,
    Spline,
    Ellipse,
)
from ezdxf.layouts import VirtualLayout
from ezdxf.lldxf.tagwriter import TagWriter, AbstractTagWriter
from ezdxf.math import NULLVEC, Z_AXIS, Vec3
from ezdxf.render import MeshBuilder

if TYPE_CHECKING:
    from ezdxf.entitydb import EntitySpace

__all__ = ["R12Exporter"]


def spline_to_polyline(
    spline: Spline, max_sagitta: float, min_segments: int
) -> Polyline:
    polyline = Polyline.new(dxfattribs={"flags": const.POLYLINE_3D_POLYLINE})
    polyline.append_vertices(points=spline.flattening(max_sagitta, min_segments))
    return polyline


def ellipse_to_polyline(
    ellipse: Ellipse, max_sagitta: float, min_segments: int
) -> Polyline:
    polyline = Polyline.new(dxfattribs={"flags": const.POLYLINE_3D_POLYLINE})
    polyline.append_vertices(points=ellipse.flattening(max_sagitta, min_segments))
    return polyline


def lwpolyline_to_polyline(lwpolyline: LWPolyline) -> Polyline:
    polyline = Polyline.new(
        dxfattribs={
            "layer": lwpolyline.dxf.layer,
            "linetype": lwpolyline.dxf.linetype,
            "color": lwpolyline.dxf.color,
        }
    )
    polyline.append_formatted_vertices(lwpolyline.points(), format="xyseb")  # type: ignore
    if lwpolyline.is_closed:
        polyline.close()
    if lwpolyline.dxf.hasattr("const_width"):
        width = lwpolyline.dxf.const_width
        polyline.dxf.start_width = width
        polyline.dxf.end_width = width
    extrusion = Vec3(lwpolyline.dxf.extrusion)
    if not extrusion.isclose(Z_AXIS):
        polyline.dxf.extrusion = extrusion
        elevation = lwpolyline.dxf.elevation
        polyline.dxf.elevation = Vec3(0, 0, elevation)
        # Set z-axis of VERTEX.location to elevation?
    return polyline


def mesh_to_polyface_mesh(mesh: Mesh) -> Polyface:
    builder = MeshBuilder.from_mesh(mesh)
    return builder.render_polyface(
        VirtualLayout(),
        dxfattribs={
            "layer": mesh.dxf.layer,
            "linetype": mesh.dxf.linetype,
            "color": mesh.dxf.color,
        },
    )


def get_replacement_block_name(entity: DXFEntity) -> str:
    return f"EZDXF_{entity.dxf.handle}_REPLACEMENT"


def default_entity_exporter(exporter: R12Exporter, entity: DXFEntity):
    entity.export_dxf(exporter.tagwriter)


def export_lwpolyline(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity, LWPolyline)
    polyline = lwpolyline_to_polyline(entity)
    if len(polyline.vertices):
        polyline.export_dxf(exporter.tagwriter)


def export_mesh(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity, Mesh)
    polyface_mesh = mesh_to_polyface_mesh(entity)
    if len(polyface_mesh.vertices):
        polyface_mesh.export_dxf(exporter.tagwriter)


def export_spline(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity, Spline)
    polyline = spline_to_polyline(
        entity, exporter.max_sagitta, exporter.min_spline_segments
    )
    if len(polyline.vertices):
        polyline.export_dxf(exporter.tagwriter)


def export_ellipse(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity, Ellipse)
    polyline = ellipse_to_polyline(
        entity, exporter.max_sagitta, exporter.min_ellipse_segments
    )
    if len(polyline.vertices):
        polyline.export_dxf(exporter.tagwriter)


def export_replacement_insert(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity, DXFGraphic)
    block_name = get_replacement_block_name(entity)
    insert = Insert.new(
        dxfattribs={
            "name": block_name,
            "insert": NULLVEC,
            "layer": entity.dxf.layer,
            "linetype": entity.dxf.linetype,
            "color": entity.dxf.color,
        }
    )
    insert.export_dxf(exporter.tagwriter)


# Exporters are required to convert newer entity types into DXF R12 types.
# All newer entity types without an exporter will be ignored.
EXPORTERS: dict[str, Callable[[R12Exporter, DXFEntity], None]] = {
    "LWPOLYLINE": export_lwpolyline,
    "MESH": export_mesh,
    "SPLINE": export_spline,
    "ELLIPSE": export_ellipse,
}


# Planned feature: explode complex newer entity types into DXF primitives:
#
# MTextExplode creates new text styles and cannot use a virtual layout.
# A temporary document will be required or a special MTextExplode class has to be
# implemented.
# current state: MTEXT is ignored
#
# ACAD_TABLE: original anonymous block "*T..." should not be exported
# current state: ACAD_TABLE is ignored


class R12Exporter:
    def __init__(self, doc: Drawing, max_sagitta: float = 0.01):
        assert isinstance(doc, Drawing)
        self._doc = doc
        self._tagwriter: AbstractTagWriter = None  # type: ignore
        self.max_sagitta = float(max_sagitta)  # flattening SPLINE, ELLIPSE
        self.min_spline_segments: int = 4  # flattening SPLINE
        self.min_ellipse_segments: int = 8  # flattening ELLIPSE

    @property
    def doc(self) -> Drawing:
        return self._doc

    @property
    def tagwriter(self) -> AbstractTagWriter:
        return self._tagwriter

    def reset(self, tagwriter: AbstractTagWriter) -> None:
        self._tagwriter = tagwriter

    def write(self, stream: TextIO) -> None:
        self.reset(TagWriter(stream, write_handles=False, dxfversion=const.DXF12))
        self.preprocess()
        self.export_sections()

    def saveas(self, filepath: str | os.PathLike) -> None:
        with open(filepath, mode="wt", encoding=self.doc.encoding) as fp:
            self.write(fp)

    def preprocess(self) -> None:
        # e.g. explode HATCH entities into extra blocks
        pass

    def export_sections(self) -> None:
        assert isinstance(self._tagwriter, AbstractTagWriter)
        self.export_header()
        self.export_tables()
        self.export_blocks()
        self.export_layouts()

    def export_header(self) -> None:
        self.doc.header.export_dxf(self._tagwriter)

    def export_tables(self) -> None:
        self.doc.tables.export_dxf(self._tagwriter)

    def export_blocks(self) -> None:
        self._write_section_header("BLOCKS")
        for block_record in self.doc.block_records:
            if block_record.is_any_layout and not block_record.is_active_paperspace:
                continue
            self._export_block_record(block_record)
        self._write_endsec()

    def export_layouts(self) -> None:
        self._write_section_header("ENTITIES")
        self._export_entity_space(self.doc.modelspace().entity_space)
        self._export_entity_space(self.doc.paperspace().entity_space)
        self._write_endsec()

    def _export_block_record(self, block_record: BlockRecord):
        tagwriter = self._tagwriter
        assert block_record.block is not None
        block_record.block.export_dxf(tagwriter)
        if not block_record.is_any_layout:
            self._export_entity_space(block_record.entity_space)
        assert block_record.endblk is not None
        block_record.endblk.export_dxf(tagwriter)

    def _export_entity_space(self, space: EntitySpace):
        for entity in space:
            exporter = EXPORTERS.get(entity.dxftype(), default_entity_exporter)
            exporter(self, entity)

    def _write_section_header(self, name: str) -> None:
        self._tagwriter.write_str(f"  0\nSECTION\n  2\n{name}\n")

    def _write_endsec(self) -> None:
        self._tagwriter.write_tag2(0, "ENDSEC")

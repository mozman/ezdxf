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
from io import StringIO
import logging
import string

import ezdxf
from ezdxf import const
from ezdxf.document import Drawing
from ezdxf.entities import (
    BlockRecord,
    DXFEntity,
    LWPolyline,
    Polyline,
    Polyface,
    Mesh,
    Spline,
    Ellipse,
)
from ezdxf.layouts import VirtualLayout
from ezdxf.lldxf.types import DXFTag, TAG_STRING_FORMAT
from ezdxf.lldxf.tagwriter import TagWriter, AbstractTagWriter
from ezdxf.math import Z_AXIS, Vec3
from ezdxf.render import MeshBuilder

if TYPE_CHECKING:
    from ezdxf.entitydb import EntitySpace

__all__ = ["R12Exporter", "convert", "saveas", "write"]

MAX_SAGITTA = 0.01
logger = logging.getLogger("ezdxf")


def convert(doc: Drawing, *, max_sagitta: float = MAX_SAGITTA) -> Drawing:
    """Export and reload DXF document as DXF version R12."""
    stream = StringIO()
    exporter = R12Exporter(doc, max_sagitta=max_sagitta)
    exporter.write(stream)
    stream.seek(0)
    return ezdxf.read(stream)


def write(doc: Drawing, stream: TextIO, *, max_sagitta: float = MAX_SAGITTA) -> None:
    """Write a DXF document as DXF version R12 to a text stream."""
    exporter = R12Exporter(doc, max_sagitta=max_sagitta)
    exporter.write(stream)


def saveas(
    doc: Drawing, filepath: str | os.PathLike, *, max_sagitta: float = MAX_SAGITTA
) -> None:
    """Write a DXF document as DXF version R12 to a file."""
    with open(filepath, "wt", encoding=doc.encoding, errors="dxfreplace") as stream:
        write(
            doc,
            stream,
            max_sagitta=max_sagitta,
        )


def spline_to_polyline(
    spline: Spline, max_sagitta: float, min_segments: int
) -> Polyline:
    polyline = Polyline.new(
        dxfattribs={
            "layer": spline.dxf.layer,
            "linetype": spline.dxf.linetype,
            "color": spline.dxf.color,
            "flags": const.POLYLINE_3D_POLYLINE,
        }
    )

    polyline.append_vertices(points=spline.flattening(max_sagitta, min_segments))
    polyline.new_seqend()
    return polyline


def ellipse_to_polyline(
    ellipse: Ellipse, max_sagitta: float, min_segments: int
) -> Polyline:
    polyline = Polyline.new(
        dxfattribs={
            "layer": ellipse.dxf.layer,
            "linetype": ellipse.dxf.linetype,
            "color": ellipse.dxf.color,
            "flags": const.POLYLINE_3D_POLYLINE,
        }
    )
    polyline.append_vertices(points=ellipse.flattening(max_sagitta, min_segments))
    polyline.new_seqend()
    return polyline


def lwpolyline_to_polyline(lwpolyline: LWPolyline) -> Polyline:
    polyline = Polyline.new(
        dxfattribs={
            "layer": lwpolyline.dxf.layer,
            "linetype": lwpolyline.dxf.linetype,
            "color": lwpolyline.dxf.color,
        }
    )
    polyline.new_seqend()
    polyline.append_formatted_vertices(lwpolyline.get_points(), format="xyseb")  # type: ignore
    if lwpolyline.is_closed:
        polyline.close()
    if lwpolyline.dxf.hasattr("const_width"):
        width = lwpolyline.dxf.const_width
        polyline.dxf.default_start_width = width
        polyline.dxf.default_end_width = width
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


def get_xpl_block_name(entity: DXFEntity) -> str:
    assert entity.dxf.handle is not None
    return f"EZDXF_XPL_{entity.dxftype()}_{entity.dxf.handle}"


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

# ACAD Releases upto 14: limit names to 31 characters in length.
# Names can include the letters A to Z, the numerals 0 to 9, and the special characters,
# dollar sign ($), underscore (_), and hyphen (-).

VALID_CHARS_CODE_2 = set(string.ascii_letters + string.digits + "_-*$")
VALID_CHARS_CODE_3 = set(string.ascii_letters + string.digits + "_-*$.")


# Truncating names from the end to avoid duplicate table names: name[-31:]
def sanitize_name(code, name):
    if code in (3, 4):  # only for the '.' in font definitions
        return "".join(
            (char if char in VALID_CHARS_CODE_3 else "_") for char in name[-31:]
        )
    else:
        return "".join(
            (char if char in VALID_CHARS_CODE_2 else "_") for char in name[-31:]
        )


# 1 The primary text value for an entity
# 2 A name: Attribute tag, Block name, and so on. Also used to identify a DXF section or
#   table name
# 3 Other textual or name values: Textstyle.font
# 4 Other textual or name values: Textstyle.bigfont
# 5 Entity handle expressed as a hexadecimal string (fixed)
# 6 Line type name (fixed)
# 7 Text style name (fixed)
# 8 Layer name (fixed)
NAME_TAG_CODES = {2, 3, 4, 6, 7, 8, 1001, 1003}


class R12TagWriter(TagWriter):
    def __init__(self, stream: TextIO, dxfversion: str, write_handles: bool):
        super().__init__(stream, dxfversion, write_handles)
        self.skip_xdata = False

    def write_tag(self, tag: DXFTag) -> None:
        code, value = tag
        if self.skip_xdata and tag.code > 999:
            return
        if code in NAME_TAG_CODES:
            self._stream.write(TAG_STRING_FORMAT % (code, sanitize_name(code, value)))
        else:
            self._stream.write(tag.dxfstr())

    def write_tag2(self, code: int, value) -> None:
        if self.skip_xdata and code > 999:
            return
        if code in NAME_TAG_CODES:
            value = sanitize_name(code, value)
        self._stream.write(TAG_STRING_FORMAT % (code, value))


class R12Exporter:
    def __init__(self, doc: Drawing, max_sagitta: float = 0.01):
        assert isinstance(doc, Drawing)
        self._doc = doc
        self._tagwriter: R12TagWriter = None  # type: ignore
        self.max_sagitta = float(max_sagitta)  # flattening SPLINE, ELLIPSE
        self.min_spline_segments: int = 4  # flattening SPLINE
        self.min_ellipse_segments: int = 8  # flattening ELLIPSE
        self.log: list[str] = []

    @property
    def doc(self) -> Drawing:
        return self._doc

    @property
    def tagwriter(self) -> R12TagWriter:
        return self._tagwriter

    def log_msg(self, msg: str) -> None:
        logger.debug(msg)
        self.log.append(msg)

    def reset(self, tagwriter: R12TagWriter) -> None:
        self._tagwriter = tagwriter
        self.log.clear()

    def write(self, stream: TextIO) -> None:
        self.reset(R12TagWriter(stream, write_handles=False, dxfversion=const.DXF12))
        self.preprocess()
        self.export_sections()

    def preprocess(self) -> None:
        # e.g. explode HATCH entities into blocks
        pass

    def export_sections(self) -> None:
        assert isinstance(self._tagwriter, AbstractTagWriter)
        self.export_header()
        self.export_tables()
        self.export_blocks()
        self.export_layouts()
        self._write_end_of_file()

    def export_header(self) -> None:
        self.doc.header.export_dxf(self._tagwriter)

    def export_tables(self) -> None:
        # DXF R12 does not support XDATA in tables according Autodesk DWG TrueView
        tagwriter = self.tagwriter
        tagwriter.skip_xdata = True
        self.doc.tables.export_dxf(tagwriter)
        tagwriter.skip_xdata = False

    def export_blocks(self) -> None:
        self._write_section_header("BLOCKS")
        for block_record in self.doc.block_records:
            if block_record.is_any_paperspace and not block_record.is_active_paperspace:
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
        tagwriter = self._tagwriter
        for entity in space:
            if entity.MIN_DXF_VERSION_FOR_EXPORT > const.DXF12:
                exporter = EXPORTERS.get(entity.dxftype())
                if exporter:
                    exporter(self, entity)
                else:
                    self.log_msg(f"Entity {str(entity)} not exported.")
            else:
                entity.export_dxf(tagwriter)

    def _write_section_header(self, name: str) -> None:
        self._tagwriter.write_str(f"  0\nSECTION\n  2\n{name}\n")

    def _write_endsec(self) -> None:
        self._tagwriter.write_tag2(0, "ENDSEC")

    def _write_end_of_file(self):
        self._tagwriter.write_tag2(0, "EOF")

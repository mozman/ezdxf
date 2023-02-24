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
from typing import TYPE_CHECKING, TextIO, Callable, Optional
import os
from io import StringIO
import logging

import ezdxf
from ezdxf import const, proxygraphic
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
    Insert,
    MText,
    Textstyle,
)
from ezdxf.addons import MTextExplode
from ezdxf.entitydb import EntitySpace
from ezdxf.layouts import BlockLayout, VirtualLayout
from ezdxf.lldxf.tagwriter import TagWriter, AbstractTagWriter
from ezdxf.lldxf.types import DXFTag, TAG_STRING_FORMAT
from ezdxf.math import Z_AXIS, Vec3, NULLVEC
from ezdxf.r12strict import R12NameTranslator
from ezdxf.render import MeshBuilder
from ezdxf.sections.table import TextstyleTable

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType

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
        polyline.export_dxf(exporter.tagwriter())


def export_mesh(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity, Mesh)
    polyface_mesh = mesh_to_polyface_mesh(entity)
    if len(polyface_mesh.vertices):
        polyface_mesh.export_dxf(exporter.tagwriter())


def export_spline(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity, Spline)
    polyline = spline_to_polyline(
        entity, exporter.max_sagitta, exporter.min_spline_segments
    )
    if len(polyline.vertices):
        polyline.export_dxf(exporter.tagwriter())


def export_ellipse(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity, Ellipse)
    polyline = ellipse_to_polyline(
        entity, exporter.max_sagitta, exporter.min_ellipse_segments
    )
    if len(polyline.vertices):
        polyline.export_dxf(exporter.tagwriter())


def make_insert(name: str, entity: DXFEntity, location=NULLVEC) -> Insert:
    return Insert.new(
        dxfattribs={
            "name": name,
            "layer": entity.dxf.layer,
            "linetype": entity.dxf.linetype,
            "color": entity.dxf.color,
            "insert": location,
        }
    )


def export_proxy_graphic(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity.proxy_graphic, bytes)
    pg = proxygraphic.ProxyGraphic(entity.proxy_graphic)
    try:
        entities = EntitySpace(pg.virtual_entities())
    except proxygraphic.ProxyGraphicError:
        return
    exporter.export_entity_space(entities)


def export_mtext(exporter: R12Exporter, entity: DXFEntity):
    assert isinstance(entity, MText)
    layout = VirtualLayout()
    exporter.explode_mtext(entity, layout)
    exporter.export_entity_space(layout.entity_space)


# Exporters are required to convert newer entity types into DXF R12 types.
# All newer entity types without an exporter will be ignored.
EXPORTERS: dict[str, Callable[[R12Exporter, DXFEntity], None]] = {
    "LWPOLYLINE": export_lwpolyline,
    "MESH": export_mesh,
    "SPLINE": export_spline,
    "ELLIPSE": export_ellipse,
    "MTEXT": export_mtext,
}


# Planned features: explode complex newer entity types into DXF primitives.
# currently skipped entity types:
# - MTEXT: exploding into DXF primitives is possible
# - LEADER: exploding into DXF primitives is possible
# - MLEADER: exploding into DXF primitives is possible
# - MLINE: exploding into DXF primitives is possible
# - HATCH & MPOLYGON: exploding pattern filling as LINE entities and solid filling as
#   SOLID entities is possible
# - ACAD_TABLE: graphic as geometry block is available
# --------------------------------------------------------------------------------------
# - all ACIS based entities: tessellated meshes could be exported, but very much work
#   and beyond my current knowledge
# - IMAGE and UNDERLAY: no support possible
# - XRAY and XLINE: no support possible (infinite lines)

# Possible name tags to translate:
# 1 The primary text value for an entity
# 2 A name: Attribute tag, Block name, and so on. Also used to identify a DXF section or
#   table name
# 3 Other textual or name values: Textstyle.font
# 4 Other textual or name values: Textstyle.bigfont
# 5 Entity handle expressed as a hexadecimal string (fixed)
# 6 Line type name (fixed)
# 7 Text style name (fixed)
# 8 Layer name (fixed)
NAME_TAG_CODES = {2, 3, 6, 7, 8, 1001, 1003}


class R12TagWriter(TagWriter):
    def __init__(self, stream: TextIO):
        super().__init__(stream, dxfversion=const.DXF12, write_handles=False)
        self.skip_xdata = False
        self.current_entity = ""
        self.translator = R12NameTranslator()

    def set_stream(self, stream: TextIO) -> None:
        self._stream = stream

    def write_tag(self, tag: DXFTag) -> None:
        code, value = tag
        if code == 0:
            self.current_entity = str(value)
        if self.skip_xdata and tag.code > 999:
            return
        if code in NAME_TAG_CODES:
            self._stream.write(
                TAG_STRING_FORMAT % (code, self.sanitize_name(code, value))
            )
        else:
            self._stream.write(tag.dxfstr())

    def write_tag2(self, code: int, value) -> None:
        if self.skip_xdata and code > 999:
            return
        if code == 0:
            self.current_entity = str(value)
        if code in NAME_TAG_CODES:
            value = self.sanitize_name(code, value)
        self._stream.write(TAG_STRING_FORMAT % (code, value))

    def sanitize_name(self, code: int, name: str):
        # sanitize group code 3 + 4
        # LTYPE - <description> has group code (3) NO
        # STYLE - <font> has group code (3) NO
        # STYLE - <bigfont> has group code (4) NO
        # DIMSTYLE - <dimpost> has group code e.g. "<> mm" (3) NO
        # DIMSTYLE - <dimapost> has group code (4) NO
        # ATTDEF - <prompt> has group code (3) NO
        # DIMENSION - <dimstyle> has group code (3) YES
        if code == 3 and self.current_entity != "DIMENSION":
            return name
        return self.translator.translate(name)


class SpecialStyleTable:
    def __init__(self, styles: TextstyleTable, extra_styles: TextstyleTable):
        self.styles = styles
        self.extra_styles = extra_styles

    def get_text_styles(self) -> list[Textstyle]:
        entries = list(self.styles.entries.values())
        for name, extra_style in self.extra_styles.entries.items():
            if not self.styles.has_entry(name):
                entries.append(extra_style)
        return entries

    def export_dxf(self, tagwriter: AbstractTagWriter) -> None:
        text_styles = self.get_text_styles()
        tagwriter.write_tag2(0, "TABLE")
        tagwriter.write_tag2(2, "STYLE")
        tagwriter.write_tag2(70, len(text_styles))
        for style in text_styles:
            style.export_dxf(tagwriter)
        tagwriter.write_tag2(0, "ENDTAB")


EOF_STR = "0\nEOF\n"


def detect_max_block_number(names: list[str]) -> int:
    max_number = 0
    for name in names:
        name = name.upper()
        if not name.startswith("*"):
            continue
        try:  # *U10
            number = int(name[2:])
        except ValueError:
            continue
        max_number = max(max_number, number)
    return max_number + 1


class R12Exporter:
    def __init__(self, doc: Drawing, max_sagitta: float = 0.01):
        assert isinstance(doc, Drawing)
        self._doc = doc
        self._tagwriter = R12TagWriter(StringIO())
        self.max_sagitta = float(max_sagitta)  # flattening SPLINE, ELLIPSE
        self.min_spline_segments: int = 4  # flattening SPLINE
        self.min_ellipse_segments: int = 8  # flattening ELLIPSE
        self._extra_doc = ezdxf.new("R12")
        self._next_block_number = detect_max_block_number(
            [br.dxf.name for br in doc.block_records]
        )

    @property
    def doc(self) -> Drawing:
        return self._doc

    def tagwriter(self, stream: Optional[TextIO] = None) -> R12TagWriter:
        if stream is not None:
            self._tagwriter.set_stream(stream)
        return self._tagwriter

    def write(self, stream: TextIO) -> None:
        """Write DXF document to text stream."""
        stream.write(self.to_string())

    def to_string(self) -> str:
        """Export DXF document as string."""
        # export layouts before blocks: may create new anonymous blocks
        entities = self.export_layouts_to_string()
        # export blocks before HEADER and TABLES sections: may create new text styles
        blocks = self.export_blocks_to_string()

        return "".join(
            (
                self.export_header_to_string(),
                self.export_tables_to_string(),
                blocks,
                entities,
                EOF_STR,
            )
        )

    def next_block_name(self) -> str:
        name = f"*U{self._next_block_number}"
        self._next_block_number += 1
        return name

    def new_block(self, entity: DXFEntity) -> BlockLayout:
        name = self.next_block_name()
        return self._extra_doc.blocks.new(
            name,
            dxfattribs={
                "layer": entity.dxf.get("layer", "0"),
                "flags": const.BLK_ANONYMOUS,
            },
        )

    def export_header_to_string(self) -> str:
        in_memory_stream = StringIO()
        self.doc.header.export_dxf(self.tagwriter(in_memory_stream))
        return in_memory_stream.getvalue()

    def export_tables_to_string(self) -> str:
        # DXF R12 does not support XDATA in tables according Autodesk DWG TrueView
        in_memory_stream = StringIO()
        tables = self.doc.tables
        preserve_table = tables.styles
        tables.styles = SpecialStyleTable(self.doc.styles, self._extra_doc.styles)  # type: ignore

        tagwriter = self.tagwriter(in_memory_stream)
        tagwriter.skip_xdata = True
        tables.export_dxf(tagwriter)
        tables.styles = preserve_table
        tagwriter.skip_xdata = False
        return in_memory_stream.getvalue()

    def export_blocks_to_string(self) -> str:
        in_memory_stream = StringIO()
        self._tagwriter.set_stream(in_memory_stream)

        self._write_section_header("BLOCKS")
        for block_record in self.doc.block_records:
            if block_record.is_any_paperspace and not block_record.is_active_paperspace:
                continue
            name = block_record.dxf.name.lower()
            if name in ("$model_space", "$paper_space"):
                # These block names collide with the translated names of the *Model_Space
                # and the *Paper_Space blocks.
                continue
            self._export_block_record(block_record)

        extra_blocks = self.get_extra_blocks()
        while len(extra_blocks):
            for block_record in extra_blocks:
                self._export_block_record(block_record)
                self.discard_extra_block(block_record.dxf.name)
            # block record export can create further blocks
            extra_blocks = self.get_extra_blocks()

        self._write_endsec()
        return in_memory_stream.getvalue()

    def discard_extra_block(self, name: str) -> None:
        self._extra_doc.block_records.discard(name)

    def get_extra_blocks(self) -> list[BlockRecord]:
        return [
            br for br in self._extra_doc.block_records if br.dxf.name.startswith("*U")
        ]

    def explode_mtext(self, mtext: MText, layout: GenericLayoutType):
        with MTextExplode(layout, self._extra_doc) as xpl:
            xpl.explode(mtext, destroy=False)

    def export_layouts_to_string(self) -> str:
        in_memory_stream = StringIO()
        self._tagwriter.set_stream(in_memory_stream)

        self._write_section_header("ENTITIES")
        self.export_entity_space(self.doc.modelspace().entity_space)
        self.export_entity_space(self.doc.paperspace().entity_space)
        self._write_endsec()
        return in_memory_stream.getvalue()

    def _export_block_record(self, block_record: BlockRecord):
        tagwriter = self._tagwriter
        assert block_record.block is not None
        block_record.block.export_dxf(tagwriter)
        if not block_record.is_any_layout:
            self.export_entity_space(block_record.entity_space)
        assert block_record.endblk is not None
        block_record.endblk.export_dxf(tagwriter)

    def export_entity_space(self, space: EntitySpace):
        tagwriter = self._tagwriter
        for entity in space:
            if entity.MIN_DXF_VERSION_FOR_EXPORT > const.DXF12:
                exporter = EXPORTERS.get(entity.dxftype())
                if exporter:
                    exporter(self, entity)
                    continue
                if entity.proxy_graphic:
                    export_proxy_graphic(self, entity)
            else:
                entity.export_dxf(tagwriter)

    def _write_section_header(self, name: str) -> None:
        self._tagwriter.write_str(f"  0\nSECTION\n  2\n{name}\n")

    def _write_endsec(self) -> None:
        self._tagwriter.write_tag2(0, "ENDSEC")

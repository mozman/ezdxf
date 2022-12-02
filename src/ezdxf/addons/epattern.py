#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import TextIO
import os
import io

import ezdxf
from ezdxf.document import Drawing
from ezdxf.lldxf.tagwriter import TagWriter, AbstractTagWriter

__all__ = ["export_file", "export_stream"]


def export_file(doc: Drawing, filename: str | os.PathLike) -> None:
    """Exports ASTM/AAMA compliant DXF R12 files (ASTM-DXF/D6673).
    The input document must correspond to the DXF R12 format.

    Args:
        doc: DXF document of type :class:`ezdxf.document.Drawing`
        filename: filename as string or a path-like object

    Raises:
        DXFVersionError: invalid DXF version of the input document

    """
    fp = io.open(filename, mode="wt", encoding="ascii", errors="dxfreplace")
    export_stream(doc, fp)


def export_stream(doc: Drawing, stream: TextIO) -> None:
    """Exports ASTM/AAMA compliant DXF R12 files (ASTM-DXF/D6673) to the given `stream`
    instance. The input document must correspond to the DXF R12 format.

    Args:
        doc: DXF document of type :class:`ezdxf.document.Drawing`
        stream: text stream with "ascii" encoding

    Raises:
        DXFVersionError: invalid DXF version of the input document

    """
    if doc.dxfversion != ezdxf.const.DXF12:
        raise ezdxf.DXFVersionError("only DXF R12 format is supported")
    tagwriter = TagWriter(stream, write_handles=False, dxfversion=ezdxf.const.DXF12)
    _export_sections(doc, tagwriter)


def _export_sections(doc: Drawing, tagwriter: AbstractTagWriter) -> None:
    """DXF export sections. (internal API)"""
    # export empty header section
    tagwriter.write_str("  0\nSECTION\n  2\nHEADER\n")
    tagwriter.write_tag2(0, "ENDSEC")
    # export block definitions
    _export_blocks(doc, tagwriter)
    # export modelspace content
    tagwriter.write_str("  0\nSECTION\n  2\nENTITIES\n")
    doc.modelspace().entity_space.export_dxf(tagwriter)
    tagwriter.write_tag2(0, "ENDSEC")
    tagwriter.write_tag2(0, "EOF")


def _export_blocks(doc: Drawing, tagwriter: AbstractTagWriter) -> None:
    tagwriter.write_str("  0\nSECTION\n  2\nBLOCKS\n")
    for block_record in doc.block_records:
        if block_record.is_block_layout:
            block_record.export_block_definition(tagwriter)
    tagwriter.write_tag2(0, "ENDSEC")


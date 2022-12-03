# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
# This add-on was created to solve this problem: https://github.com/mozman/ezdxf/discussions/789
"""
This add-on creates special DXF files for use by Gerber Technology applications which
have a broken DXF loader.
"""
from __future__ import annotations
from typing import TextIO
import os
import io

import ezdxf
from ezdxf.document import Drawing
from ezdxf.lldxf.tagwriter import TagWriter, AbstractTagWriter

__all__ = ["export_file", "export_stream"]


def export_file(doc: Drawing, filename: str | os.PathLike) -> None:
    """Exports the specified DXF R12 document, intended to contain content conforming to
    the ASTM-D6673-10 standard, in a special way so that Gerber Technology applications
    can parse it by their low-quality DXF parser.
    """
    fp = io.open(filename, mode="wt", encoding="ascii", errors="dxfreplace")
    export_stream(doc, fp)


def export_stream(doc: Drawing, stream: TextIO) -> None:
    if doc.dxfversion != ezdxf.const.DXF12:
        raise ezdxf.DXFVersionError("only DXF R12 format is supported")
    tagwriter = TagWriter(stream, write_handles=False, dxfversion=ezdxf.const.DXF12)
    _export_sections(doc, tagwriter)


def _export_sections(doc: Drawing, tagwriter: AbstractTagWriter) -> None:
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
    # This is the important part:
    #
    # Gerber Technology applications have a low-quality parser which do not accept DXF
    # files that contain blocks without ASTM-D6673-10 content, such as the *MODEL_SPACE
    # and *PAPER_SPACE blocks.
    #
    # This is annoying but the presence of these blocks is NOT mandatory for
    # the DXF Standard.
    #
    tagwriter.write_str("  0\nSECTION\n  2\nBLOCKS\n")
    for block_record in doc.block_records:
        if block_record.is_block_layout:
            block_record.export_block_definition(tagwriter)
    tagwriter.write_tag2(0, "ENDSEC")

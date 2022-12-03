# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
# This add-on was created to solve this problem: https://github.com/mozman/ezdxf/discussions/789
"""
This add-on creates invalid DXF files to accommodate Gerber Technology's software,
because the software of Gerber Technology do not follow fully the ASTM-D6673-10
standard which requires DXF compliant DXF files.

Citation from the ASTM-D6673-10 Standard:

    1.2  The file format for the pattern data exchange file defined
    by this standard (Practice D6673) complies with the Drawing
    Interchange File (DXF) format. Autodesk, Inc. developed the
    DXF format for transferring data between their AutoCAD(r)
    product and other software applications. This standard documents
    the manner in which pattern data should be represented within
    the DXF format.  Users of this standard should have
    Autodesk, Inc.’s documentation on Drawing Interchange Files,
    found in the AutoCAD Reference Manual, in order to assure
    compatibility to all DXF format specifications. The AutoCAD
    Version 13 DXF specification is to be used. The file format for
    the grade rule table exchange file is an ASCII text file.

I hate creating invalid DXF files, but I also want to help those users who need to use
Gerber Technology software (e.g. Gerber Accumark).

I don't know Gerber Technology's motivation to cripple the file format to a point that
these files can no longer be opened by Autodesk applications, so these files are
definitely no longer following the DXF standard, but if that's a try locking users into
their software-ecosystem, this add-on may help those users to get some freedom back.

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
    """Export the given DXF R12 document which should contain content according to the
    ASTM-D6673-10 Standard, so that Gerber Technology applications can read it.
    The exported file is an invalid DXF file which Autodesk applications cannot open!
    """
    fp = io.open(filename, mode="wt", encoding="ascii", errors="dxfreplace")
    export_stream(doc, fp)


def export_stream(doc: Drawing, stream: TextIO) -> None:
    if doc.dxfversion != ezdxf.const.DXF12:
        raise ezdxf.DXFVersionError("only DXF R12 format is supported")
    tagwriter = TagWriter(stream, write_handles=False, dxfversion=ezdxf.const.DXF12)
    _export_sections(doc, tagwriter)


def _export_sections(doc: Drawing, tagwriter: AbstractTagWriter) -> None:
    tagwriter.write_tag2(
        999,
        "This is an invalid DXF file created by ezdxf for use by Gerber Technology applications",
    )
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

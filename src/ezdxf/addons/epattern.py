#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Union, Optional, TextIO, BinaryIO
import os
import io

import ezdxf
from ezdxf.document import Drawing
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.filemanagement import dxf_file_info


def readfile(
    filename: Union[str, os.PathLike],
) -> Drawing:
    filename = str(filename)
    info = dxf_file_info(filename)
    with open(filename, mode="rt", encoding=info.encoding, errors="ignore") as fp:  # type: ignore
        doc = D6673.read(fp)  # type: ignore
    doc.filename = filename
    return doc


class D6673(Drawing):
    def saveas(
        self,
        filename: Union[os.PathLike, str],
        encoding: Optional[str] = None,
        fmt: str = "asc",
    ) -> None:
        self.filename = str(filename)
        self.save(encoding=encoding, fmt=fmt)

    def save(self, encoding: Optional[str] = None, fmt: str = "asc") -> None:
        if encoding is None:
            enc = self.output_encoding
        else:
            enc = encoding

        if fmt.startswith("asc"):
            fp = io.open(
                self.filename, mode="wt", encoding=enc, errors="dxfreplace"  # type: ignore
            )
        else:
            raise ValueError(f"only ASCII format supported.")
        try:
            self.write(fp, fmt=fmt)  # type: ignore
        finally:
            fp.close()

    def write(self, stream: Union[TextIO, BinaryIO], fmt: str = "asc") -> None:
        if self.dxfversion != ezdxf.const.DXF12:
            raise ezdxf.DXFVersionError("only DXF R12 format is supported")
        # no handles required
        self.header["$HANDLING"] = 0
        handles = False
        tagwriter = TagWriter(
            stream,  # type: ignore
            write_handles=handles,
            dxfversion=ezdxf.const.DXF12,
        )
        self.export_sections(tagwriter)

    def export_sections(self, tagwriter: TagWriter) -> None:
        """DXF export sections. (internal API)"""
        # export empty header section
        tagwriter.write_str("  0\nSECTION\n  2\nHEADER\n")
        tagwriter.write_tag2(0, "ENDSEC")
        # export block definitions
        self.export_blocks(tagwriter)
        # export modelspace content
        tagwriter.write_str("  0\nSECTION\n  2\nENTITIES\n")
        self.modelspace().entity_space.export_dxf(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")
        tagwriter.write_tag2(0, "EOF")

    def export_blocks(self, tagwriter: TagWriter) -> None:
        tagwriter.write_str("  0\nSECTION\n  2\nBLOCKS\n")
        for block_record in self.block_records:
            if block_record.dxf.name.startswith("*"):  # ignore layout blocks
                continue
            block_record.export_block_definition(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

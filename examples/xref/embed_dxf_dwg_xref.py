#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import odafc
from ezdxf.document import Drawing
from ezdxf import xref, units

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to attach DXF and DWG files as external references to a
# host document.
# ------------------------------------------------------------------------------


def make_dxf_xref_document(name: str, dxfversion="R2013") -> Drawing:
    # AutoCAD does not accept DXF R12 files as XREF :(
    ref_doc = ezdxf.new(dxfversion, units=units.M)
    ref_doc.modelspace().add_circle(
        center=(5, 5), radius=2.5, dxfattribs={"layer": "CIRCLE"}
    )
    ref_doc.header["$INSBASE"] = (5, 5, 0)  # set XREF base point for insertion
    ref_doc.saveas(CWD / name)
    return ref_doc


# AutoCAD accepts DXF files (>DXF12) as XREFs, but is unwilling to resolve the
# DXF files created by ezdxf, which opened for itself is a total valid DXF
# document.
#
# It seems that AutoCAD does not resolve any DXF file as an XREF file, no matter what
# CAD application created the DXF file!
# The much more friendly BricsCAD has no problem to resolve the DXF files as XREFs.
#
# Export the DXF document as DWG file by the odafc addon, for more information
# see the docs: https://ezdxf.mozman.at/docs/addons/odafc.html
# At least the DWG file is accepted by AutoCAD.


def export_dwg_xref_document(name: str, doc: Drawing) -> None:
    dwg = CWD / name
    try:
        odafc.export_dwg(doc, str(dwg), replace=True)
    except odafc.ODAFCError as e:
        print(str(e))


def create_xrefs(dxf_name, dwg_name, dxfversion):
    xref_doc = make_dxf_xref_document(dxf_name, dxfversion=dxfversion)
    export_dwg_xref_document(dwg_name, xref_doc)


def embed_dxf_xref(dxf_name: str, dxfversion: str) -> None:
    host_doc = ezdxf.new(dxfversion, units=units.M)
    host_doc.filename = str(CWD / "host_embedded_dxf.dxf")

    xref.attach(host_doc, block_name="dxf_xref", filename=dxf_name)
    block = host_doc.blocks.get("dxf_xref")
    xref.embed(block)
    host_doc.save()


def embed_dwg_xref(dwg_name: str, dxfversion: str) -> None:
    host_doc = ezdxf.new(dxfversion, units=units.M)
    host_doc.filename = str(CWD / "host_embedded_dwg.dxf")

    xref.attach(host_doc, block_name="dwg_xref", filename=dwg_name)
    block = host_doc.blocks.get("dwg_xref")
    xref.embed(block, load_fn=odafc.readfile)
    host_doc.save()


def main():
    dxfversion = "R2013"
    dxf_name = "xref.dxf"
    dwg_name = "xref.dwg"
    create_xrefs(dxf_name, dwg_name, dxfversion)

    embed_dxf_xref(dxf_name, dxfversion)
    embed_dwg_xref(dwg_name, dxfversion)


if __name__ == "__main__":
    main()

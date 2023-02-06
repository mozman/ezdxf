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


def use_add_xref_def(dxf_name: str, dwg_name: str, dxfversion: str) -> None:
    # The method before ezdxf v1.1 which will continue to work in the future:
    host_doc = ezdxf.new(dxfversion, units=units.M)
    msp = host_doc.modelspace()

    # create external reference definitions
    host_doc.add_xref_def(filename=dxf_name, name="dxf_xref")
    host_doc.add_xref_def(filename=dwg_name, name="dwg_xref")

    # add external references as block references:
    msp.add_blockref(name="dxf_xref", insert=(0, 0))
    msp.add_blockref(name="dwg_xref", insert=(10, 0))

    # save host document
    host_doc.set_modelspace_vport(height=10, center=(5, 0))
    host_doc.saveas(CWD / "host_add_xref.dxf")


def use_xref_attach(dxf_name: str, dwg_name: str, dxfversion: str) -> None:
    # The new ezdxf.xref module in v1.1 bundles all XREF relates tasks into a single
    # module.
    host_doc = ezdxf.new(dxfversion, units=units.M)

    # create the external reference definition and a default block reference for it:
    xref.attach(host_doc, block_name="dxf_xref", filename=dxf_name)
    xref.attach(host_doc, block_name="dwg_xref", filename=dwg_name, insert=(10, 0))

    # save host document
    host_doc.set_modelspace_vport(height=10, center=(5, 0))
    host_doc.saveas(CWD / "host_xref_attach.dxf")


def main():
    dxfversion = "R2013"
    dxf_name = "xref.dxf"
    dwg_name = "xref.dwg"
    create_xrefs(dxf_name, dwg_name, dxfversion)

    # both function do the same:
    # 1. uses the method before ezdxf v1.1
    use_add_xref_def(dxf_name, dwg_name, dxfversion)
    # 2. uses the new xref module in ezdxf v1.1
    use_xref_attach(dxf_name, dwg_name, dxfversion)


if __name__ == "__main__":
    main()

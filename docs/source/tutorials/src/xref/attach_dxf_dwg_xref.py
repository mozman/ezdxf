#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import ezdxf
from ezdxf.addons import odafc
from ezdxf.document import Drawing
from ezdxf import xref, units, colors
from ezdxf.render import forms

DXFVERSION = "R2013"
DXF_NAME = "xref.dxf"
DWG_NAME = "xref.dwg"


def make_dxf_xref_document(name: str) -> Drawing:
    ref_doc = ezdxf.new(DXFVERSION, units=units.M)
    ref_doc.layers.add("GEAR", color=colors.YELLOW)
    msp = ref_doc.modelspace()
    gear = forms.gear(
        16, top_width=0.25, bottom_width=0.75, height=0.5, outside_radius=2.5
    )
    msp.add_lwpolyline(
        forms.translate(gear, (5, 5)), close=True, dxfattribs={"layer": "GEAR"}
    )
    ref_doc.header["$INSBASE"] = (5, 5, 0)
    ref_doc.saveas(name)
    return ref_doc


def export_dwg_xref_document(name: str, doc: Drawing) -> None:
    try:
        odafc.export_dwg(doc, str(name), replace=True)
    except odafc.ODAFCError as e:
        print(str(e))


def create_xrefs():
    xref_doc = make_dxf_xref_document(DXF_NAME)
    export_dwg_xref_document(DWG_NAME, xref_doc)


def attach_dxf() -> None:
    host_doc = ezdxf.new(DXFVERSION, units=units.M)
    xref.attach(host_doc, block_name="dxf_xref", insert=(0, 0), filename=DXF_NAME)
    host_doc.set_modelspace_vport(height=10, center=(0, 0))
    host_doc.saveas("attached_dxf.dxf")


def attach_dwg() -> None:
    host_doc = ezdxf.new(DXFVERSION, units=units.M)
    xref.attach(host_doc, block_name="dwg_xref", filename=DWG_NAME, insert=(0, 0))
    host_doc.set_modelspace_vport(height=10, center=(0, 0))
    host_doc.saveas("attached_dwg.dxf")


def main():
    create_xrefs()
    attach_dxf()
    attach_dwg()


if __name__ == "__main__":
    main()

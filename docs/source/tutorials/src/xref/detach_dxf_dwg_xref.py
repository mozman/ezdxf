#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import ezdxf
from ezdxf.addons import odafc
from ezdxf.document import Drawing
from ezdxf import xref, colors
from ezdxf.render import forms


def make_block(doc: Drawing, name: str) -> None:
    blk = doc.blocks.new(name, base_point=(5, 5, 0))
    doc.layers.add("GEAR", color=colors.YELLOW)
    gear = forms.gear(
        16, top_width=0.25, bottom_width=0.75, height=0.5, outside_radius=2.5
    )
    blk.add_lwpolyline(
        forms.translate(gear, (5, 5)), close=True, dxfattribs={"layer": "GEAR"}
    )
    doc.modelspace().add_blockref(name, (0, 0))


def detach_dxf() -> None:
    host_doc = ezdxf.new()
    make_block(host_doc, "GEAR")
    block_layout = host_doc.blocks.get("GEAR")
    detached_block_doc = xref.detach(block_layout, xref_filename="detached_gear.dxf")
    detached_block_doc.saveas("detached_gear.dxf")
    host_doc.set_modelspace_vport(height=10, center=(0, 0))
    host_doc.saveas("detach_host_dxf_xref.dxf")


def detach_dwg() -> None:
    host_doc = ezdxf.new()
    make_block(host_doc, "GEAR")
    block_layout = host_doc.blocks.get("GEAR")
    detached_block_doc = xref.detach(block_layout, xref_filename="detached_gear.dwg")
    try:
        odafc.export_dwg(detached_block_doc, "detached_gear.dwg", replace=True)
    except odafc.ODAFCError as e:
        print(str(e))
    host_doc.set_modelspace_vport(height=10, center=(0, 0))
    host_doc.saveas("detach_host_dwg_xref.dxf")


if __name__ == "__main__":
    detach_dxf()
    detach_dwg()

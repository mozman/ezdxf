#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import ezdxf
from ezdxf import colors, transform, xref
from ezdxf.math import Matrix44
from ezdxf.render import forms


def make_gear(name: str) -> None:
    doc = ezdxf.new()
    doc.layers.add("GEAR", color=colors.YELLOW)
    msp = doc.modelspace()
    gear = forms.gear(
        16, top_width=0.25, bottom_width=0.75, height=0.5, outside_radius=2.5
    )
    msp.add_lwpolyline(gear, close=True, dxfattribs={"layer": "GEAR"})
    doc.saveas(name)


make_gear("gear.dxf")
merged_doc = ezdxf.new()
for index in range(3):
    sdoc = ezdxf.readfile("gear.dxf")  # this could be different DXF files
    transform.inplace(sdoc.modelspace(), Matrix44.translate(index * 10, 0, 0))
    xref.load_modelspace(sdoc, merged_doc)
merged_doc.saveas("merged.dxf")

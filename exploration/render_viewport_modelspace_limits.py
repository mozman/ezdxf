#  Copyright (c) 2024, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import cast, TYPE_CHECKING
from pathlib import Path
import ezdxf
from ezdxf import colors
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.math import Vec2
from ezdxf.entities import Viewport

if TYPE_CHECKING:
    from ezdxf.layouts import Modelspace

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")


def render_viewport_modelspace_limits(vp: Viewport, msp: Modelspace, dxfattribs):
    print(f"  {str(vp)}")
    x0, y0, x1, y1 = vp.get_modelspace_limits()
    vertices = Vec2(x0, y0), Vec2(x1, y0), Vec2(x1, y1), Vec2(x0, y1)
    msp.add_lwpolyline(vertices, close=True, dxfattribs=dxfattribs)


def main(filename: str) -> None:
    print(f"loading DXF: {filename}")
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()

    for num, name in enumerate(doc.layout_names_in_taborder()):
        if name == "Model":
            continue
        print(f"processing layout: {name}")
        layer_name = f"EZDXF_VP_BORDER_{num}"
        doc.layers.add(layer_name, color=colors.MAGENTA)
        dxfattribs = GfxAttribs(layer=layer_name)
        psp = doc.layout(name)
        for viewport in psp.query("VIEWPORT")[1:]:
            # skip the first viewport - defines the paperspace representation in
            # the CAD application
            render_viewport_modelspace_limits(
                cast(Viewport, viewport), msp, dxfattribs=dxfattribs
            )

    filename = CWD / "vp_limits.dxf"
    print(f"saving DXF: {filename}")
    doc.saveas(filename)
    print("finish.")


if __name__ == "__main__":
    main(r"C:\Users\mozman\Desktop\Now\ezdxf\1298\problematic_viewports.dxf")

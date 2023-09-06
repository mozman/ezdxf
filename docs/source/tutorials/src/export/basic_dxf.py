#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, dxf


def example_doc():
    doc = ezdxf.new()
    msp = doc.modelspace()
    x0, y0, x1, y1 = 0, 0, 10, 10
    start = (x0, y0)
    end = (x0 + 1, y0)
    for color in range(1, 6):
        msp.add_lwpolyline(
            [start, (x0, y1), (x1, y1), (x1, y0), end], dxfattribs={"color": color}
        )
        x0 += 1
        x1 -= 1
        y0 += 1
        y1 -= 1
        start = end
        end = (x0 + 1, y0)
    msp.add_line((0, -2), (10, -2), dxfattribs={"color": 7})
    return doc


def export(doc):
    export_doc = ezdxf.new()
    msp = doc.modelspace()
    # 1. create the render context
    context = RenderContext(doc)
    # 2. create the backend
    backend = dxf.DXFBackend(export_doc.modelspace())
    # 3. create the frontend
    frontend = Frontend(context, backend)
    # 4. draw the modelspace
    frontend.draw_layout(msp)
    # 5. save or return DXF document
    export_doc.saveas("output_01.dxf")


if __name__ == "__main__":
    export(example_doc())

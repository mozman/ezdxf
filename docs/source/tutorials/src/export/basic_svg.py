#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout


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
    return doc


def export(doc):
    msp = doc.modelspace()
    # 1. create the render context
    context = RenderContext(doc)
    # 2. create the backend
    backend = svg.SVGBackend()
    # 3. create the frontend
    frontend = Frontend(context, backend)
    # 4. draw the modelspace
    frontend.draw_layout(msp)
    # 5. create an A4 page layout, not required for all backends
    page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
    # 6. get the SVG rendering as string - this step is backend dependent
    svg_string = backend.get_string(page)
    with open("output.svg", "wt", encoding="utf8") as fp:
        fp.write(svg_string)


if __name__ == "__main__":
    export(example_doc())

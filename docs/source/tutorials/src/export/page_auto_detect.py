#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout, config


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


def make_backend(doc):
    msp = doc.modelspace()
    context = RenderContext(doc)
    backend = svg.SVGBackend()
    frontend = Frontend(
        context,
        backend,
        config=config.Configuration(
            background_policy=config.BackgroundPolicy.WHITE,
        ),
    )
    frontend.draw_layout(msp)
    return backend


def export_1(doc):
    backend = make_backend(doc)
    # auto-detect page size and 2mm margins on all sides
    page = layout.Page(0, 0, layout.Units.mm, margins=layout.Margins.all(2))
    # scale content by 1, do not fit content to page
    svg_string = backend.get_string(
        page, settings=layout.Settings(scale=1, fit_page=False)
    )
    with open("output_1.svg", "wt", encoding="utf8") as fp:
        fp.write(svg_string)


def export_2(doc):
    backend = make_backend(doc)
    # auto-detect page size and 2mm margins on all sides
    page = layout.Page(0, 0, layout.Units.mm, margins=layout.Margins.all(2))
    # scale content by 10, do not fit content to page
    svg_string = backend.get_string(
        page, settings=layout.Settings(scale=10, fit_page=False)
    )
    with open("output_2.svg", "wt", encoding="utf8") as fp:
        fp.write(svg_string)


if __name__ == "__main__":
    doc1 = example_doc()
    export_1(doc1)
    export_2(doc1)

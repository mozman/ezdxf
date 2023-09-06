#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, pymupdf, layout, config


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


def export_dark_bg(doc):
    msp = doc.modelspace()
    # 1. create the render context
    context = RenderContext(doc)
    # 2. create the backend
    backend = pymupdf.PyMuPdfBackend()
    # 3. create the frontend
    frontend = Frontend(context, backend)
    # 4. draw the modelspace
    frontend.draw_layout(msp)
    # 5. create an A4 page layout
    page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
    # 6. get the PNG rendering as bytes
    png_bytes = backend.get_pixmap_bytes(page, fmt="png", dpi=96)
    with open("png_dark_bg.png", "wb") as fp:
        fp.write(png_bytes)


def export_white_bg(doc):
    msp = doc.modelspace()
    # 1. create the render context
    context = RenderContext(doc)
    # 2. create the backend
    backend = pymupdf.PyMuPdfBackend()
    # 3. create and configure the frontend
    cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE)
    frontend = Frontend(context, backend, config=cfg)
    # 4. draw the modelspace
    frontend.draw_layout(msp)
    # 5. create an A4 page layout
    page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
    # 6. get the PNG rendering as bytes
    png_bytes = backend.get_pixmap_bytes(page, fmt="png", dpi=96)
    with open("png_white_bg.png", "wb") as fp:
        fp.write(png_bytes)


if __name__ == "__main__":
    doc = example_doc()
    export_dark_bg(doc)
    export_white_bg(doc)

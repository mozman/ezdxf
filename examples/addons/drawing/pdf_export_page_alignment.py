# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import pathlib

import ezdxf
from ezdxf.render import forms
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing import layout, pymupdf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")
EXAMPLE_DXF = pathlib.Path(__file__).parent.parent.parent.parent / "examples_dxf"

# ------------------------------------------------------------------------------
# This example shows how to use the page alignment, when exporting the modelspace by the
# drawing add-on and the PyMuPDF backend.
#
# docs: https://ezdxf.mozman.at/docs/addons/drawing.html
# ------------------------------------------------------------------------------


def export_aligned(page_alignment: layout.PageAlignment, filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_lwpolyline(
        forms.gear(16, top_width=5, bottom_width=10, height=5, outside_radius=30),
        close=True,
    )
    backend = pymupdf.PyMuPdfBackend()
    height, width, _ = layout.PAGE_SIZES["ISO A4"]

    Frontend(RenderContext(doc), backend).draw_layout(msp)
    page = layout.Page(width, height, margins=layout.Margins.all(15))
    pdf_bytes = backend.get_pdf_bytes(page, settings=layout.Settings(
        fit_page=False,
        page_alignment=page_alignment,
    ))
    (CWD / filename).write_bytes(pdf_bytes)


if __name__ == "__main__":
    for page_alignment, filename in [
        (layout.PageAlignment.TOP_LEFT, "gear_top_left.pdf"),
        (layout.PageAlignment.TOP_CENTER, "gear_top_center.pdf"),
        (layout.PageAlignment.TOP_RIGHT, "gear_top_right.pdf"),
        (layout.PageAlignment.MIDDLE_LEFT, "gear_middle_left.pdf"),
        (layout.PageAlignment.MIDDLE_CENTER, "gear_middle_center.pdf"),
        (layout.PageAlignment.MIDDLE_RIGHT, "gear_middle_right.pdf"),
        (layout.PageAlignment.BOTTOM_LEFT, "gear_bottom_left.pdf"),
        (layout.PageAlignment.BOTTOM_CENTER, "gear_bottom_center.pdf"),
        (layout.PageAlignment.BOTTOM_RIGHT, "gear_bottom_right.pdf"),

    ]:
        export_aligned(page_alignment, filename)

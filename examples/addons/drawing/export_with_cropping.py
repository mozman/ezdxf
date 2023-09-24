# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import pathlib

import ezdxf
from ezdxf.document import Drawing
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import (
    Configuration,
    BackgroundPolicy,
    ColorPolicy,
)
from ezdxf.addons.drawing import svg, layout, pymupdf, hpgl2

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to export the modelspace by the drawing add-on and the
# native SVG backend with cropping at the page margins
#
# docs: https://ezdxf.mozman.at/docs/addons/drawing.html
# ------------------------------------------------------------------------------

CADKIT = "CADKitSamples"
CADKIT_FILES = [
    "BIKE.DXF",
    "gekko.DXF",
    "Tamiya TT-01.DXF",
    "Tyrannosaurus.DXF",
]


def export_svg(doc: Drawing, alignment: layout.PageAlignment, outname: pathlib.Path):
    msp = doc.modelspace()
    # A4 landscape, 1 drawing unit = 1mm, 10mm margin on all sides of the page
    page = layout.Page(297, 210, layout.Units.mm, layout.Margins.all(10))
    settings = layout.Settings(
        page_alignment=alignment, crop_at_margins=True, fit_page=False, scale=0.25
    )
    backend = svg.SVGBackend()
    Frontend(
        RenderContext(doc),
        backend,
        config=Configuration(
            background_policy=BackgroundPolicy.WHITE,
            color_policy=ColorPolicy.BLACK,
        ),
    ).draw_layout(msp)

    svg_string = backend.get_string(page, settings)
    (CWD / outname).write_text(svg_string)
    print(f"exported: {outname}")


def export_pdf(doc: Drawing, alignment: layout.PageAlignment, outname: pathlib.Path):
    msp = doc.modelspace()
    # A4 landscape, 1 drawing unit = 1mm, 10mm margin on all sides of the page
    page = layout.Page(297, 210, layout.Units.mm, layout.Margins.all(10))
    settings = layout.Settings(
        page_alignment=alignment, crop_at_margins=True, fit_page=False, scale=0.25
    )
    backend = pymupdf.PyMuPdfBackend()
    Frontend(
        RenderContext(doc),
        backend,
        config=Configuration(
            background_policy=BackgroundPolicy.WHITE,
            color_policy=ColorPolicy.BLACK,
        ),
    ).draw_layout(msp)

    pdf_bytes = backend.get_pdf_bytes(page, settings=settings)
    (CWD / outname).write_bytes(pdf_bytes)
    print(f"exported: {outname}")


def export_plt(doc: Drawing, alignment: layout.PageAlignment, outname: pathlib.Path):
    msp = doc.modelspace()
    # A4 landscape, 1 drawing unit = 1mm, 10mm margin on all sides of the page
    page = layout.Page(297, 210, layout.Units.mm, layout.Margins.all(10))
    settings = layout.Settings(
        page_alignment=alignment, crop_at_margins=True, fit_page=False, scale=0.25
    )
    backend = hpgl2.PlotterBackend()
    Frontend(
        RenderContext(doc),
        backend,
        # background is always white for the plotter Backend
        config=Configuration(color_policy=ColorPolicy.BLACK),
    ).draw_layout(msp)

    plt_bytes = backend.get_bytes(page, settings=settings)
    (CWD / outname).write_bytes(plt_bytes)
    print(f"exported: {outname}")


def export_cadkit_samples():
    for name in CADKIT_FILES[:]:
        filename = ezdxf.options.test_files_path / CADKIT / name
        doc = ezdxf.readfile(filename)
        export_svg(doc, layout.PageAlignment.TOP_LEFT, filename.stem + ".svg")
        export_pdf(doc, layout.PageAlignment.MIDDLE_CENTER, filename.stem + ".pdf")
        export_plt(doc, layout.PageAlignment.BOTTOM_RIGHT, filename.stem + ".plt")


if __name__ == "__main__":
    export_cadkit_samples()

# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import pathlib
import time

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import (
    Configuration,
    BackgroundPolicy,
    ColorPolicy,
    LineweightPolicy,
)
from ezdxf.addons.drawing import pymupdf, layout
from ezdxf.math import global_bspline_interpolation

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")
EXAMPLE_DXF = pathlib.Path(__file__).parent.parent.parent.parent / "examples_dxf"

# ------------------------------------------------------------------------------
# This example shows how to export the modelspace by the drawing add-on and the
# native SVG backend.
#
# docs: https://ezdxf.mozman.at/docs/addons/drawing.html
# ------------------------------------------------------------------------------

CADKIT = "CADKitSamples"
CADKIT_FILES = [
    "A_000217.dxf",
    "AEC Plan Elev Sample.dxf",
    "backhoe.dxf",
    "BIKE.DXF",
    "Controller-M128-top.dxf",
    "drilling_machine.dxf",
    "fanuc-430-arm.dxf",
    "Floor plan.dxf",
    "gekko.DXF",
    "house design for two family with comman staircasedwg.dxf",
    "house design.dxf",
    "kit-dev-coldfire-xilinx_5213.dxf",
    "Lock-Off.dxf",
    "Mc Cormik-D3262.DXF",
    "Mechanical Sample.dxf",
    "Nikon_D90_Camera.DXF",
    "pic_programmer.dxf",
    "Proposed Townhouse.dxf",
    "Shapefont.dxf",
    "SMA-Controller.dxf",
    "Tamiya TT-01.DXF",
    "Tyrannosaurus.DXF",
    "WOOD DETAILS.dxf",
]

wave = [
    (0.0, 0.0),
    (0.897597901, 0.78183148),
    (1.79519580, 0.97492791),
    (2.69279370, 0.433883739),
    (3.59039160, -0.43388373),
    (4.48798950, -0.97492791),
    (5.38558740, -0.78183148),
    (6.28318530, 0.0),
]


def export(filepath: pathlib.Path, layout_names=("Model",), scale=1, fmt="png", dpi=72):
    print(f"\nprocessing: {filepath.name}")
    t0 = time.perf_counter()
    doc = ezdxf.readfile(filepath)
    t1 = time.perf_counter()
    print(f"loading time: {t1 - t0: .3f} seconds")
    for layout_name in layout_names:
        outname = filepath.stem + f"-[{layout_name}]" + f".{fmt}"
        print(outname)
        t1 = time.perf_counter()
        if layout_name == "Model":
            dxf_layout = doc.modelspace()
            page = layout.Page(
                0,  # auto-detect
                0,  # auto-detect
                layout.Units.mm,  # 1 drawing unit = 1mm
                layout.Margins.all(0),
                max_width=1189,  # limit page width to 1189mm
                max_height=841,  # limit page height to 841mm
            )
            settings = layout.Settings(scale=scale, fit_page=True)
        else:
            try:
                dxf_layout = doc.paperspace(layout_name)
            except KeyError:
                print(f"Layout '{layout_name}' not found")
                continue
            page = layout.Page.from_dxf_layout(dxf_layout)
            settings = layout.Settings(
                fit_page=False,
                scale=dxf_layout.get_plot_unit_scale_factor() * scale,
            )

        backend = pymupdf.PyMuPdfBackend()
        # You can get the content bounding box in DXF drawing units, before you create the
        # PNG output to calculate page size, margins, scaling factor and so on ...
        # content_extents = backend.bbox()
        config = Configuration(
            # blueprint schema:
            # background_policy=BackgroundPolicy.CUSTOM,
            # custom_bg_color="#002082",
            # color_policy=ColorPolicy.CUSTOM,
            # custom_fg_color="#ced8f7",
            # lineweight_policy=LineweightPolicy.RELATIVE,
            # lineweight_scaling=0.5,
        )

        Frontend(RenderContext(doc), backend, config=config).draw_layout(dxf_layout)
        pixmap_bytes = backend.get_pixmap_bytes(
            page, fmt=fmt, settings=settings, dpi=dpi
        )
        t2 = time.perf_counter()
        print(f"render time: {t2 - t1: .3f} seconds")
        (CWD / outname).write_bytes(pixmap_bytes)


def export_cadkit_samples(fmt="png", dpi=72):
    # supported formats: png, ppm
    for name in CADKIT_FILES[:]:
        filename = ezdxf.options.test_files_path / CADKIT / name
        export(filename, fmt=fmt, dpi=dpi)


def transparency():
    doc = ezdxf.readfile(EXAMPLE_DXF / "transparency_checker.dxf")
    msp = doc.modelspace()
    backend = pymupdf.PyMuPdfBackend()
    Frontend(RenderContext(doc), backend).draw_layout(msp)
    pdf_bytes = backend.get_pixmap_bytes(
        layout.Page(0, 0, layout.Units.mm),
        fmt="png",
        settings=layout.Settings(scale=10),
        dpi=72,
        alpha=True,
    )
    (CWD / "transparency.pdf").write_bytes(pdf_bytes)


if __name__ == "__main__":
    # export(pathlib.Path(r"C:\Source\dxftest\CADKitSamples\A_000217.dxf"), dpi=72)
    export_cadkit_samples(fmt="png")
    # simple()
    # transparency()

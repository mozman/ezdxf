# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import pathlib
import time

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
from ezdxf.addons.drawing import svg, layout
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


def export(filepath: pathlib.Path, layout_names=("Model",)):
    print(f"\nprocessing: {filepath.name}")
    t0 = time.perf_counter()
    doc = ezdxf.readfile(filepath)
    t1 = time.perf_counter()
    print(f"loading time: {t1 - t0: .3f} seconds")
    for layout_name in layout_names:
        outname = filepath.stem + f"-[{layout_name}]" + ".svg"
        print(outname)
        t1 = time.perf_counter()
        if layout_name == "Model":
            dxf_layout = doc.modelspace()
            page = layout.Page(0, 0, layout.Units.mm, layout.Margins.all(10))
            settings = layout.Settings(
                stroke_width_policy=layout.StrokeWidthPolicy.RELATIVE,
            )
        else:
            try:
                dxf_layout = doc.paperspace(layout_name)
            except KeyError:
                print(f"Layout '{layout_name}' not found")
                continue
            page = layout.Page.from_dxf_layout(dxf_layout)
            settings = layout.Settings(
                fit_page=False,
                stroke_width_policy=layout.StrokeWidthPolicy.RELATIVE,
                scale=dxf_layout.get_plot_unit_scale_factor(),
            )

        backend = svg.SVGBackend()
        # You can get the content bounding box in DXF drawing units, before you create the
        # SVG output to calculate page size, margins, scaling factor and so on ...
        # content_extents = backend.bbox()

        Frontend(RenderContext(doc), backend, config=Configuration()).draw_layout(
            dxf_layout
        )

        svg_string = backend.get_string(page, settings)
        t2 = time.perf_counter()
        print(f"render time: {t2 - t1: .3f} seconds")
        (CWD / outname).write_text(svg_string)


def export_cadkit_samples():
    for name in CADKIT_FILES[:]:
        filename = ezdxf.options.test_files_path / CADKIT / name
        export(filename)


def simple():
    doc = ezdxf.new()
    msp = doc.modelspace()
    s = global_bspline_interpolation(wave)
    msp.add_spline(dxfattribs={"color": 2}).apply_construction_tool(s)
    msp.add_lwpolyline(wave, dxfattribs={"color": 3})

    backend = svg.SVGBackend()
    Frontend(RenderContext(doc), backend).draw_layout(msp)
    svg_string = backend.get_string(layout.Page(100, 40, layout.Units.mm))
    (CWD / "wave.svg").write_text(svg_string)


def transparency():
    doc = ezdxf.readfile(EXAMPLE_DXF / "transparency_checker.dxf")
    msp = doc.modelspace()
    backend = svg.SVGBackend()
    Frontend(RenderContext(doc), backend).draw_layout(msp)
    svg_string = backend.get_string(
        layout.Page(0, 0, layout.Units.mm), settings=layout.Settings(scale=10)
    )
    (CWD / "transparency.svg").write_text(svg_string)


if __name__ == "__main__":
    export(
        pathlib.Path(r"C:\Source\dxftest\CADKitSamples\AEC Plan Elev Sample.dxf"),
        ["Model", "PLAN", "SECTION"],
    )
    # export_cadkit_samples()
    # simple()
    # transparency()

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
from ezdxf.addons.drawing import hpgl2, layout
from ezdxf.math import global_bspline_interpolation

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")
EXAMPLE_DXF = pathlib.Path(__file__).parent.parent.parent.parent / "examples_dxf"

# ------------------------------------------------------------------------------
# This example shows how to export the modelspace by the drawing add-on and the
# native HPGL2 backend.
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
        outname = filepath.stem + f"-[{layout_name}]" + ".plt"
        print(outname)
        t1 = time.perf_counter()
        if layout_name == "Model":
            dxf_layout = doc.modelspace()
            page = layout.Page(
                0,  # auto-detect
                0,  # auto-detect
                layout.Units.mm,  # 1 drawing unit = 1mm
                layout.Margins.all(10),  # 10mm margin on all sides of the page
                max_width=1189,  # limit page width to 1189mm
                max_height=841,  # limit page height to 841mm
            )
            settings = layout.Settings()
        else:
            try:
                dxf_layout = doc.paperspace(layout_name)
            except KeyError:
                print(f"Layout '{layout_name}' not found")
                continue
            page = layout.Page.from_dxf_layout(dxf_layout)
            settings = layout.Settings(
                fit_page=False,
                scale=dxf_layout.get_plot_unit_scale_factor(),
            )

        backend = hpgl2.PlotterBackend()
        Frontend(
            RenderContext(doc),
            backend,
            config=Configuration(
                color_policy=ColorPolicy.BLACK,
                lineweight_policy=LineweightPolicy.ABSOLUTE,
            ),
        ).draw_layout(dxf_layout)

        data = backend.get_bytes(page, settings=settings, curves=True, decimal_places=0)
        t2 = time.perf_counter()
        print(f"render time: {t2 - t1: .3f} seconds")
        (CWD / outname).write_bytes(data)


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

    backend = hpgl2.PlotterBackend()
    Frontend(RenderContext(doc), backend).draw_layout(msp)
    data = backend.get_bytes(layout.Page(100, 40, layout.Units.mm))
    (CWD / "wave.plt").write_bytes(data)


def triangle():
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_line((0, 100), (500, 100))
    msp.add_solid([(0, 0), (500, 0), (250, 500)], dxfattribs={"color": 1})

    backend = hpgl2.PlotterBackend()
    Frontend(RenderContext(doc), backend).draw_layout(msp)
    data = backend.get_bytes(layout.Page(0, 0))
    (CWD / "triangle.plt").write_bytes(data)


def text():
    doc = ezdxf.new()
    doc.styles.add("ARIAL", font="Arial.ttf")
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (1000, 0), (1000, 800), (0, 800)], close=True)
    msp.add_text("0123456789", height=2.5, dxfattribs={"style": "ARIAL"}).set_placement(
        (100, 400)
    )
    backend = hpgl2.PlotterBackend()
    Frontend(RenderContext(doc), backend).draw_layout(msp)
    data = backend.low_quality(layout.Page(0, 0))
    (CWD / "text.plt").write_bytes(data)


def transparency():
    doc = ezdxf.readfile(EXAMPLE_DXF / "transparency_checker.dxf")
    msp = doc.modelspace()
    backend = hpgl2.PlotterBackend()
    Frontend(RenderContext(doc), backend).draw_layout(msp)
    data = backend.get_bytes(
        layout.Page(0, 0, layout.Units.mm), settings=layout.Settings(scale=10)
    )
    (CWD / "transparency.plt").write_bytes(data)


if __name__ == "__main__":
    text()
    # export(
    #     pathlib.Path(r"C:\Source\dxftest\CADKitSamples\A_000217.dxf"),
    #     ["Model"]  #, "PLAN", "SECTION"],
    # )
    export_cadkit_samples()
    # simple()
    # transparency()
    # triangle()

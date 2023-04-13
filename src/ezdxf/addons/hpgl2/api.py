#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import ezdxf
from ezdxf.document import Drawing
from ezdxf import zoom, transform
from ezdxf.math import Matrix44, BoundingBox

from .tokenizer import hpgl2_commands
from .plotter import Plotter
from .interpreter import Interpreter
from .backend import Recorder
from .dxf_backend import DXFBackend, ColorMode
from .svg_backend import SVGBackend
from .compiler import build


def to_dxf(
    b: bytes,
    scale: float = 1.0,
    *,
    rotation: int=0,
    flip_horizontal=False,
    flip_vertical=False,
    color_mode=ColorMode.RGB,
    map_black_rgb_to_white_rgb=False,
) -> Drawing:
    if rotation not in (0, 90, 180, 270):
        raise ValueError("invalid rotation angle: should be 0, 90, 180, or 270")
    doc = ezdxf.new()
    msp = doc.modelspace()
    plotter = Plotter(
        DXFBackend(
            msp,
            color_mode=color_mode,
            map_black_rgb_to_white_rgb=map_black_rgb_to_white_rgb,
        )
    )
    plotter.set_page_rotation(rotation)
    interpreter = Interpreter(plotter)
    if flip_vertical or flip_horizontal:
        plotter.set_page_flip(vertical=flip_vertical, horizontal=flip_horizontal)
        # disable embedded scaling commands
        interpreter.disable_commands(["SC", "IP", "IR"])
    interpreter.run(hpgl2_commands(b))
    if plotter.bbox.has_data:  # non-empty page
        bbox = _scale_and_zoom(msp, scale, plotter.bbox)
        _reset_doc(doc, bbox)
    return doc


def _scale_and_zoom(layout, scale, bbox):
    extmin = bbox.extmin
    extmax = bbox.extmax
    if scale != 1.0 and scale > 1e-9:
        m = Matrix44.scale(scale, scale, scale)
        transform.inplace(layout, m)
        extmin = m.transform(extmin)
        extmax = m.transform(extmax)
    zoom.window(layout, extmin, extmax)
    return BoundingBox([extmin, extmax])

def _reset_doc(doc, bbox):
    doc.header["$EXTMIN"] = bbox.extmin
    doc.header["$EXTMAX"] = bbox.extmax

    psp_size = bbox.size / 40.0  # plu to mm
    psp_center = psp_size * 0.5
    psp = doc.paperspace()
    psp.page_setup(size=(psp_size.x, psp_size.y), margins=(0, 0, 0, 0), units="mm")
    psp.add_viewport(
        center=psp_center,
        size=(psp_size.x, psp_size.y),
        view_center_point=bbox.center,
        view_height=bbox.size.y,
    )


def to_svg(b: bytes, *, rotation: int=0, flip_horizontal=False, flip_vertical=False) -> str:
    # 1st pass records the plotting commands and detects the bounding box
    recorder = Recorder()
    plotter = Plotter(recorder)
    plotter.set_page_rotation(rotation)
    interpreter = Interpreter(plotter)
    if flip_vertical or flip_horizontal:
        plotter.set_page_flip(vertical=flip_vertical, horizontal=flip_horizontal)
        # disable embedded scaling commands
        interpreter.disable_commands(["SC", "IP", "IR"])
    interpreter.run(hpgl2_commands(b))
    if not plotter.bbox.has_data:
        return ""

    # 2nd pass replays the plotting commands to plot the SVG
    svg_backend = SVGBackend(plotter.bbox)
    recorder.replay(svg_backend)
    return svg_backend.get_string()

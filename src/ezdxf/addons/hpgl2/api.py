#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import ezdxf
from ezdxf.document import Drawing
from ezdxf import zoom, transform
from ezdxf.math import Matrix44
from .tokenizer import parse
from .plotter import Plotter
from .interpreter import Interpreter
from .backend import BoundingBoxDetector
from .dxf_backend import DXFBackend, ColorMode
from .svg_backend import SVGBackend
from .compiler import build


def plot_to_dxf(
    b: bytes,
    scale: float = 1.0,
    *,
    color_mode=ColorMode.RGB,
    map_black_rgb_to_white_rgb=False,
) -> Drawing:
    doc = ezdxf.new()
    msp = doc.modelspace()
    commands = parse(b)
    plotter = Plotter(
        DXFBackend(
            msp,
            color_mode=color_mode,
            map_black_rgb_to_white_rgb=map_black_rgb_to_white_rgb,
        )
    )
    interpreter = Interpreter(plotter)
    interpreter.run(commands)
    if interpreter.not_implemented_commands:
        print(
            f"not implemented commands: {sorted(interpreter.not_implemented_commands)}"
        )
    if plotter.bbox.has_data:  # non-empty page
        _scale_and_zoom(msp, scale, plotter.bbox)
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


PROLOG = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
)


def plot_to_svg(b: bytes) -> str:
    # 1st pass detect extents
    detector = BoundingBoxDetector()
    plotter = Plotter(detector)
    commands = parse(b)
    interpreter = Interpreter(plotter)
    interpreter.run(commands)
    if not detector.bbox.has_data:
        return ""
    # 2nd pass plot SVG
    svg_backend = SVGBackend(detector.bbox)
    plotter = Plotter(svg_backend)
    interpreter = Interpreter(plotter)
    interpreter.run(commands)
    return PROLOG + svg_backend.get_string()

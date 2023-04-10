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
from .dxf_backend import DXFBackend, ColorMode
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

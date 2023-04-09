#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import ezdxf
from ezdxf.document import Drawing
from .tokenizer import parse
from .plotter import Plotter
from .interpreter import Interpreter
from .dxf_backend import DXFBackend
from .compiler import build


def plot_dxf(b: bytes) -> Drawing:
    doc = ezdxf.new()
    commands = parse(b)
    plotter = Plotter(DXFBackend(doc.modelspace()))
    interpreter = Interpreter(plotter)
    interpreter.run(commands)
    print(f"unsupported commands: {interpreter.unsupported_commands}")
    return doc

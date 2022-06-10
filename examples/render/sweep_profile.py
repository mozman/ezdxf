#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib

import ezdxf
from ezdxf.render import forms
from ezdxf import path


DIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = pathlib.Path(".")

doc = ezdxf.new()
msp = doc.modelspace()

circle = list(forms.circle(8))
p0 = path.Path()
p0.curve4_to((3, 0, 5), (0, 0, 2), (1.5, 0, 4))
p0.curve4_to((6, 0, 10), (4.5, 0, 6), (6, 0, 8))
sweeping_path = list(p0.flattening(distance=0.1))
mesh = forms.sweep(circle, sweeping_path, close=True, caps=True)
mesh.render_mesh(msp, dxfattribs={"color": ezdxf.colors.MAGENTA})

square = forms.square()
sweeping_path = [(0, 0, 0), (0, 0, 5), (5, 0, 5), (5, 5, 5), (10, 5, 5)]
mesh = forms.sweep(square, sweeping_path, close=True, caps=True)
offset = 10, 0, 0
mesh.translate(*offset)
mesh.render_mesh(msp, dxfattribs={"color": ezdxf.colors.MAGENTA})

sweeping_path = [(0, 0, 5), (5, 0, 5), (5, 5, 5), (5, 5, 10)]
mesh = forms.sweep(square, sweeping_path, close=True, caps=True)
offset = 10, 10, 0
mesh.translate(*offset)
mesh.render_mesh(msp, dxfattribs={"color": ezdxf.colors.YELLOW})

doc.saveas(DIR / "sweep_profile.dxf")

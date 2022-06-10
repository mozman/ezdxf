#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib

import ezdxf
from ezdxf.render import forms
from ezdxf import path


DIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = pathlib.Path(".")

circle = list(forms.circle(8))
p0 = path.Path()
p0.curve4_to((3, 0, 5), (0, 0, 2), (1.5, 0, 4))
sweeping_path = list(p0.flattening(distance=0.1))

doc = ezdxf.new()
msp = doc.modelspace()

profiles = forms.sweep_profile(circle, sweeping_path)
mesh = forms.from_profiles_linear(profiles, close=True, caps=True)
mesh.render_mesh(msp, dxfattribs={"color": ezdxf.colors.MAGENTA})

square = list(forms.translate(forms.square(), (-.5, -.5)))
sweeping_path = [(0, 0, 0), (0, 0, 5), (5, 0, 5), (5, 5, 5)]
profiles = forms.sweep_profile(square, sweeping_path)
mesh = forms.from_profiles_linear(profiles, close=True, caps=True)
offset = 10, 0, 0
mesh.translate(*offset)
mesh.render_mesh(msp, dxfattribs={"color": ezdxf.colors.MAGENTA})

doc.saveas(DIR / "sweep_profile.dxf")

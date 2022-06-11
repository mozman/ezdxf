#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib

import ezdxf
from ezdxf.render import forms
from ezdxf import path


DIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = pathlib.Path(".")
DEBUG_COLOR = ezdxf.colors.CYAN

doc = ezdxf.new()
doc.layers.add("DEBUG", color=DEBUG_COLOR)
msp = doc.modelspace()


def add_debug_profiles(profiles, sweeping_path):
    attribs = {"layer": "DEBUG"}
    msp.add_polyline3d(
        sweeping_path,
        dxfattribs={"layer": "DEBUG", "color": ezdxf.colors.MAGENTA},
    )
    msp.add_polyline3d(profiles[0], dxfattribs=attribs)
    count = 0
    for p0, p1 in zip(profiles, profiles[1:]):
        msp.add_polyline3d(p1, dxfattribs=attribs)
        count += 1
        if count % 2:
            for s, e in zip(p0, p1):
                msp.add_line(s, e, dxfattribs=attribs)


circle = list(forms.circle(8))
p0 = path.Path()
p0.curve4_to((3, 0, 5), (0, 0, 2), (1.5, 0, 4))
p0.curve4_to((6, 0, 10), (4.5, 0, 6), (6, 0, 8))
sweeping_path = list(p0.flattening(distance=0.1))
mesh = forms.sweep(circle, sweeping_path, close=True, caps=True)
mesh.render_mesh(msp, dxfattribs={"color": ezdxf.colors.MAGENTA})

square = list(forms.translate(forms.square(), (-0.5, -0.5)))
sweeping_path = [(0, 0, 0), (0, 0, 5), (5, 0, 5), (5, 5, 5), (10, 5, 5)]
mesh = forms.sweep(square, sweeping_path, close=True, caps=True)
offset = 10, 0, 0
mesh.translate(*offset)
mesh.render_mesh(msp, dxfattribs={"color": ezdxf.colors.MAGENTA})

# The next example shows the limitations of the sweeping algorithm,
# the intersection of the sweeping volumes is degenerated for the last bending:
sweeping_path = [(0, 0, 5), (5, 0, 5), (5, 5, 5), (6, 5, 10)]
mesh = forms.sweep(square, sweeping_path, close=True, caps=True)
offset = 10, 10, 0
add_debug_profiles(
    [
        list(forms.translate(p, offset))
        for p in forms.debug_sweep_profiles(square, sweeping_path, close=True)
    ],
    list(forms.translate(sweeping_path, offset)),
)


mesh.translate(*offset)
mesh.render_mesh(msp, dxfattribs={"color": ezdxf.colors.YELLOW})

doc.saveas(DIR / "sweep_profile.dxf")

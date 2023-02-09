# Copyright (c) 2020-2022 Manfred Moitzi
# License: MIT License
import pathlib
from time import perf_counter
import math
from ezdxf.addons import MengerSponge
from ezdxf.addons import r12writer
from ezdxf.render.forms import sphere, circle, translate

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use the fast DXF R12 writer add-on.
#
# docs: https://ezdxf.mozman.at/docs/addons/r12writer.html
# ------------------------------------------------------------------------------


def menger_sponge(filename, level=1, kind=0):
    t0 = perf_counter()
    sponge = MengerSponge(level=level, kind=kind).mesh()
    t1 = perf_counter()
    print(f"Build menger sponge <{kind}> in {t1 - t0:.5f}s.")

    with r12writer(filename) as r12:
        r12.add_polyface(sponge.vertices, sponge.faces, color=1)
    print(f'saved as "{filename}".')


def polymesh(filename, size=(10, 10)):
    m, n = size  # rows, cols
    dx = math.pi / m * 2
    dy = math.pi / n * 2
    vertices = []
    for x in range(m):  # rows second
        z1 = math.sin(dx * x)
        for y in range(n):  # cols first
            z2 = math.sin(dy * y)
            z = z1 * z2
            vertices.append((x, y, z))
    with r12writer(filename) as r12:
        r12.add_polymesh(vertices, size=size, color=1)
    print(f'saved as "{filename}".')


def polyface_sphere(filename):
    mesh = sphere(16, 8, quads=True)
    with r12writer(filename) as r12:
        r12.add_polyface(mesh.vertices, mesh.faces, color=1)
    print(f'saved as "{filename}".')


def polylines(filename):
    with r12writer(filename) as r12:
        r12.add_polyline_2d(circle(8), color=1, closed=False)
        r12.add_polyline_2d(
            translate(circle(8), vec=(3, 0)), color=3, closed=True
        )
        r12.add_polyline_2d(
            [(0, 4), (4, 4, 1), (8, 4, 0, 0.2, 0.000001), (12, 4)],
            format="xybse",
            start_width=0.1,
            end_width=0.1,
            color=5,
        )
    print(f'saved as "{filename}".')


if __name__ == "__main__":
    menger_sponge(CWD / "menger_sponge_r12.dxf", level=2)
    polymesh(CWD / "polymesh.dxf", size=(20, 10))
    polyface_sphere(CWD / "sphere.dxf")
    polylines(CWD / "polylines.dxf")

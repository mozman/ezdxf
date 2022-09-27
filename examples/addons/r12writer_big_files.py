# Copyright (c) 2020-2022 Manfred Moitzi
# License: MIT License
import pathlib
from time import perf_counter
import math
from ezdxf.addons import MengerSponge
from ezdxf.addons import r12writer
from ezdxf.math.perlin import snoise2
from ezdxf.render.forms import sphere

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


def polymesh(filename, size=(10, 10), height=1):
    m, n = size  # rows, cols
    dx = math.pi / m * 2
    dy = math.pi / n * 2
    vertices = []
    for x in range(m):  # rows second
        z1 = math.sin(dx * x)
        for y in range(n):  # cols first
            z2 = math.sin(dy * y)
            z = z1 * z2 * height
            vertices.append((x, y, z))
    with r12writer(filename) as r12:
        r12.add_polymesh(vertices, size=size, color=1)
    print(f'saved as "{filename}".')


def perlin_mesh(filename, size=(10, 10), height=1, scale=1):
    m, n = size  # rows, cols
    vertices = []
    dx = 1.0 / m * scale
    dy = 1.0 / n * scale
    for x in range(m):  # rows second
        for y in range(n):  # cols first
            vertices.append((x, y, snoise2(x * dx, y * dy) * height))
    with r12writer(filename) as r12:
        r12.add_polymesh(vertices, size=size, color=1)
    print(f'saved as "{filename}".')


def polyface_sphere(filename):
    mesh = sphere(128, 64, quads=True)
    with r12writer(filename) as r12:
        r12.add_polyface(mesh.vertices, mesh.faces, color=1)
    print(f'saved as "{filename}".')


if __name__ == "__main__":
    menger_sponge(CWD / "menger_sponge_r12.dxf", level=3)
    polymesh(CWD / "polymesh.dxf", size=(256, 256), height=20)
    perlin_mesh(CWD / "perlin_mesh.dxf", size=(256, 256), height=20, scale=3)
    polyface_sphere(CWD / "sphere.dxf")

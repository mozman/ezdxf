# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from pathlib import Path
from time import perf_counter
import math
from ezdxf.addons import MengerSponge
from ezdxf.render.forms import sphere
from ezdxf.r12writer import r12writer

DIR = Path('~/Desktop/Outbox').expanduser()


def menger_sponge(filename, level=1, kind=0):
    t0 = perf_counter()
    sponge = MengerSponge(level=level, kind=kind).mesh()
    t1 = perf_counter()
    print(f'Build menger sponge <{kind}> in {t1 - t0:.5f}s.')

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
            z = z1*z2
            vertices.append((x, y, z))
    with r12writer(filename) as r12:
        r12.add_polymesh(vertices, size=size, color=1)
    print(f'saved as "{filename}".')


def polyface_sphere(filename):
    mesh = sphere(16, 8, quads=True)
    with r12writer(filename) as r12:
        r12.add_polyface(mesh.vertices, mesh.faces, color=1)
    print(f'saved as "{filename}".')


if __name__ == '__main__':
    menger_sponge(DIR / "menger_sponge_r12.dxf", level=2)
    polymesh(DIR / "polymesh.dxf", size=(20, 10))
    polyface_sphere(DIR / "sphere.dxf")

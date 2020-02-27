# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from typing import cast
from pathlib import Path
from time import perf_counter
import ezdxf
from ezdxf.addons import r12writer
from ezdxf.math.perlin import SimplexNoise
from ezdxf.addons.iterdxf import single_pass_modelspace, opendxf, modelspace
from ezdxf.render import MeshVertexMerger

DIR = Path('~/Desktop/Outbox').expanduser()
noise = SimplexNoise()
STACK_SIZE = 16
GRID_SIZE = 256
TYPE = '3DFACE'
# TYPE = 'POLYLINE'
PRINT_STATUS = False

FILENAME_R12 = DIR / f"perlin_{TYPE}_{STACK_SIZE}_stacks_{GRID_SIZE}_x_{GRID_SIZE}_r12.dxf"
FILENAME_R2010 = DIR / f"perlin_{TYPE}_{STACK_SIZE}_stacks_{GRID_SIZE}_x_{GRID_SIZE}_r2010.dxf"
COMPARE_WITH_READFILE = False


def perlin_mesh(writer, size=(10, 10), heigth: float = 1, scale: float = 1, offset: float = 0, color: int = 1):
    m, n = size  # rows, cols
    vertices = []
    dx = 1. / m * scale
    dy = 1. / n * scale
    for x in range(m):
        for y in range(n):
            vertices.append((x, y, offset + noise.noise2(x * dx, y * dy) * heigth))
    writer.add_polymesh(vertices, size=size, color=color)


def perlin_3dfaces(writer, size=(10, 10), heigth: float = 1, scale: float = 1, offset: float = 0, color: int = 1):
    def vertex(x_, y_):
        return x_, y_, offset + noise.noise2(x_ * dx, y_ * dy) * heigth

    m, n = size  # rows, cols
    dx = 1. / m * scale
    dy = 1. / n * scale
    for x in range(m - 1):
        for y in range(n - 1):
            writer.add_3dface([
                vertex(x, y),
                vertex(x + 1, y),
                vertex(x + 1, y + 1),
                vertex(x, y + 1),
            ], color=color)


def create_r12(filename: str):
    height = 20
    with r12writer(filename) as r12:
        for i in range(STACK_SIZE):
            noise.randomize()
            print(f'Writing mesh #{i} as {TYPE}')
            generator = perlin_3dfaces if TYPE == '3DFACE' else perlin_mesh
            generator(r12, size=(GRID_SIZE, GRID_SIZE), heigth=height, offset=height * i * 1.5, color=(i % 254) + 1)


def entities1(filename):
    print('using single_pass_modelspace()')
    return single_pass_modelspace(open(filename, 'rb'))


def entities2(filename):
    print('using modelspace()')
    return modelspace(filename)


def entities3(filename):
    print('using opendxf()')
    doc = opendxf(filename)
    yield from doc.modelspace()
    doc.close()


def save_as_r2010_mesh(source: str, target: str):
    count = 0
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    converting_time = 0.
    t0 = perf_counter()
    for e in entities2(source):
        if e.dxftype() == TYPE:
            count += 1
            if TYPE == 'POLYLINE':
                if PRINT_STATUS:
                    print(f'Found {count}. POLYMESH')
                e = cast('Polyline', e)
                t1 = perf_counter()
                mesh = MeshVertexMerger.from_polyface(e)
                # render as MESH entity into modelspace of doc
                mesh.render(msp, dxfattribs={'color': e.dxf.color})
                converting_time += perf_counter() - t1
            else:
                if PRINT_STATUS and not (count % 10000):
                    print(f'Found {count}. 3DFACE')
                e = cast('Face3d', e)
                t1 = perf_counter()
                msp.add_3dface(list(e), dxfattribs={'color': e.dxf.color})
                converting_time += perf_counter() - t1

    loading_time = perf_counter() - t0 - converting_time

    t0 = perf_counter()
    doc.saveas(target)
    t1 = perf_counter()
    print(f'Loading time from disk: {loading_time:.2f}s')
    print(f'Converting time : {converting_time:.2f}s')
    print(f'Time to save R2010: {t1 - t0:.2f}s')


def just_loading_time(loader):
    count = 0
    for e in loader:
        if not PRINT_STATUS:
            continue
        if e.dxftype() == TYPE:
            count += 1
            if TYPE == 'POLYLINE':
                print(f'Found {count}. POLYMESH')
            elif not (count % 10000):
                print(f'Found {count}. 3DFACE')


if __name__ == '__main__':
    print(f'Creating DXF R12 "{FILENAME_R12}"')
    print(f'Stack size {STACK_SIZE}; Grid size: {GRID_SIZE};')
    if not Path(FILENAME_R12).exists():
        t0 = perf_counter()
        create_r12(FILENAME_R12)
        t1 = perf_counter()
        print(f'Runtime {t1 - t0:.2f}s\n')

    print(f'Loading {TYPE} entities from R12 file.')

    t0 = perf_counter()
    just_loading_time(entities1(FILENAME_R12))
    t1 = perf_counter()
    print(f'Runtime {t1 - t0:.2f}s\n')

    t0 = perf_counter()
    just_loading_time(entities2(FILENAME_R12))
    t1 = perf_counter()
    print(f'Runtime {t1 - t0:.2f}s\n')

    t0 = perf_counter()
    just_loading_time(entities3(FILENAME_R12))
    t1 = perf_counter()
    print(f'Runtime {t1 - t0:.2f}s\n')

    if COMPARE_WITH_READFILE:
        print(f'Loading {TYPE} entities from R12 by ezdxf.readfile().')
        t0 = perf_counter()
        doc = ezdxf.readfile(FILENAME_R12)
        t1 = perf_counter()
        print(f'Runtime {t1 - t0:.2f}s\n')

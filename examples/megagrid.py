# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from pathlib import Path
from time import perf_counter
from ezdxf.addons import r12writer
from ezdxf.math.perlin import SimplexNoise
from ezdxf.addons.iterdxf import single_pass_modelspace, opendxf, modelspace

DIR = Path('~/Desktop/Outbox').expanduser()
noise = SimplexNoise()
PRINT_STATUS = True


def print_progress(count, max_count, start_time, msg=''):
    if not PRINT_STATUS:
        return
    status = count / max_count
    if status == 0:
        return
    time = perf_counter() - start_time
    estimated_time = time / status
    print(f'{msg}{count} of {max_count}, time: {time:.0f}s of {estimated_time:.0f}s ')


def megagrid(writer, size=(10, 10), heigth: float = 1, scale: float = 1, color: int = 1):
    def vertex(x_, y_):
        return x_, y_, noise.noise2(x_ * dx, y_ * dy) * heigth

    t0 = perf_counter()
    m, n = size  # rows, cols
    max_count = m * n
    dx = 1. / m * scale
    dy = 1. / n * scale
    count = 0
    for x in range(m - 1):
        for y in range(n - 1):
            writer.add_3dface([
                vertex(x, y),
                vertex(x + 1, y),
                vertex(x + 1, y + 1),
                vertex(x, y + 1),
            ], color=color)
            count += 1
            if not (count % 10000):
                print_progress(count, max_count, t0, msg='written ')


def create_r12(filename: str, gridsize: int):
    with r12writer(filename) as r12:
        megagrid(r12, size=(gridsize, gridsize), heigth=20, scale=3, color=1)


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


def load(loader, start_time, max_count):
    count = 0
    for _ in loader:
        if not PRINT_STATUS:
            continue
        count += 1
        if not (count % 10000):
            print_progress(count, max_count, start_time, msg='loaded ')


def main(gridsize=1024):
    filename = Path(DIR / f"mega_grid_{gridsize}_x_{gridsize}_r12.dxf")
    max_count = gridsize * gridsize
    print(f'Creating DXF R12 "{filename}"')
    print(f'Grid size: {gridsize}\nEntities: {max_count} 3DFACE')

    if not filename.exists():
        t0 = perf_counter()
        create_r12(filename, gridsize)
        t1 = perf_counter()
        print(f'Runtime {t1 - t0:.2f}s\n')
    size = round(filename.stat().st_size / 1024)
    print(f'File size: {size} KB')
    print(f'Loading 3DFACE entities from R12 file.')

    t0 = perf_counter()
    load(entities2(filename), t0, max_count)
    t1 = perf_counter()
    print(f'Runtime {t1 - t0:.2f}s\n')

    t0 = perf_counter()
    load(entities1(filename), t0, max_count)
    t1 = perf_counter()
    print(f'Runtime {t1 - t0:.2f}s\n')

    t0 = perf_counter()
    load(entities3(filename), t0, max_count)
    t1 = perf_counter()
    print(f'Runtime {t1 - t0:.2f}s\n')


if __name__ == '__main__':
    main(2048)

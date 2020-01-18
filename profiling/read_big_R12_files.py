# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import time
from pathlib import Path

DIR = Path(r'D:\Source\dxftest\CADKitSamples')
_3D_MODEL = DIR / 'fanuc-430-arm.dxf'
_2D_PLAN = DIR / 'AEC Plan Elev Sample.dxf'

def load_3D_model():
    import ezdxf
    ezdxf.readfile(filename=_3D_MODEL)


def iter_3D_model():
    import ezdxf
    doc = ezdxf.readfile(filename=_3D_MODEL)
    msp = doc.modelspace()
    count = 0
    for e in msp:
        e.dxftype()
        count += 1
    print(f'Iterated {count} entities in modelspace (fanuc-430-arm.dxf).')
    del doc


def load_2D_plan():
    import ezdxf
    ezdxf.readfile(_2D_PLAN)


def iter_2D_plan():
    import ezdxf
    doc = ezdxf.readfile(_2D_PLAN)
    msp = doc.modelspace()
    count = 0
    for e in msp:
        e.dxftype()
        count += 1
    print(f'Iterated {count} entities in modelspace (AEC Plan Elev Sample.dxf).')
    del doc


def print_result(time, text):
    print(f'Operation: {text} takes {time:.2f} seconds')


def run(func):
    start = time.perf_counter()
    func()
    end = time.perf_counter()
    return end - start


if __name__ == '__main__':
    print_result(run(load_3D_model), 'load "faunc-430-arm.dxf"')
    print_result(run(iter_3D_model), 'iter "faunc-430-arm.dxf"')
    print_result(run(load_2D_plan), 'load "AEC Plan Elev Sample.dxf"')
    print_result(run(iter_2D_plan), 'iter "AEC Plan Elev Sample.dxf"')

# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import time
from pathlib import Path

DIR = Path(r"D:\Source\dxftest\CADKitSamples")
_3D_MODEL = DIR / "fanuc-430-arm.dxf"
_2D_PLAN = DIR / "AEC Plan Elev Sample.dxf"


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
    print(f"Iterated {count} entities in modelspace (fanuc-430-arm.dxf).")
    del doc


def single_pass_iter_3D_model():
    from ezdxf.addons.iterdxf import single_pass_modelspace

    count = 0
    for e in single_pass_modelspace(open(_3D_MODEL, "rb")):
        e.dxftype()
        count += 1
    print(f"Iterated  {count} entities in modelspace (fanuc-430-arm.dxf).")


def from_disk_iter_3D_model():
    from ezdxf.addons.iterdxf import opendxf

    count = 0
    doc = opendxf(_3D_MODEL)
    for e in doc.modelspace():
        e.dxftype()
        count += 1
    doc.close()
    print(f"Iterated  {count} entities in modelspace (fanuc-430-arm.dxf).")


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
    print(
        f"Iterated {count} entities in modelspace (AEC Plan Elev Sample.dxf)."
    )
    del doc


def print_result(time, text):
    print(f"Operation: {text} takes {time:.2f} s\n")


def run(func):
    start = time.perf_counter()
    func()
    end = time.perf_counter()
    return end - start


if __name__ == "__main__":
    print_result(
        run(load_3D_model), 'ezdxf.readfile() - load "faunc-430-arm.dxf"'
    )
    print_result(
        run(iter_3D_model), 'ezdxf.readfile() - iteration "faunc-430-arm.dxf"'
    )
    print_result(
        run(single_pass_iter_3D_model),
        'iterdxf.single_pass_modelspace() - single pass iteration from disk "faunc-430-arm.dxf"',
    )
    print_result(
        run(from_disk_iter_3D_model),
        'iterdxf.opendxf() - seekable file iteration from disk "faunc-430-arm.dxf"',
    )
    print_result(
        run(load_2D_plan), 'ezdxf.readfile() - load "AEC Plan Elev Sample.dxf"'
    )
    print_result(
        run(iter_2D_plan), 'ezdxf.readfile() - iter "AEC Plan Elev Sample.dxf"'
    )

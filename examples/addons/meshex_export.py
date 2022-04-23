#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.addons import meshex
from ezdxf.render.forms import cylinder

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

SIDES = 32


def make_mesh(sides: int):
    return cylinder(count=sides)


def export_scad(filename):
    with open(filename, "wt") as fp:
        mesh = make_mesh(SIDES)
        mesh.flip_normals()
        fp.write(meshex.scad_dumps(mesh))


def export_stl_asc(filename):
    with open(filename, "wt") as fp:
        mesh = make_mesh(SIDES)
        fp.write(meshex.stl_dumps(mesh))


def export_stl_bin(filename):
    with open(filename, "wb") as fp:
        mesh = make_mesh(SIDES)
        fp.write(meshex.stl_dumpb(mesh))


def export_off(filename):
    with open(filename, "wt") as fp:
        mesh = make_mesh(SIDES)
        fp.write(meshex.off_dumps(mesh))


def export_obj(filename):
    with open(filename, "wt") as fp:
        mesh = make_mesh(SIDES)
        fp.write(meshex.obj_dumps(mesh))


def export_ply(filename):
    with open(filename, "wb") as fp:
        mesh = make_mesh(SIDES)
        fp.write(meshex.ply_dumpb(mesh))


def export_dxf(filename):
    doc = ezdxf.new()
    mesh = make_mesh(SIDES)
    mesh.render_mesh(doc.modelspace())
    doc.saveas(filename)


def main():
    export_scad(DIR / "cylinder.scad")
    export_stl_asc(DIR / "cylinder_asc.stl")
    export_stl_bin(DIR / "cylinder_bin.stl")
    export_off(DIR / "cylinder.off")
    export_obj(DIR / "cylinder.obj")
    export_ply(DIR / "cylinder.ply")
    export_dxf(DIR / "cylinder.dxf")


if __name__ == "__main__":
    main()

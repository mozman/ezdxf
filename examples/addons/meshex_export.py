#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path

from ezdxf.addons import meshex
from ezdxf.render.forms import cylinder

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")


def export_scad(filename):
    with open(filename, "wt") as fp:
        mesh = cylinder()
        mesh.flip_normals()
        fp.write(meshex.scad_dumps(mesh))


def export_stl_asc(filename):
    with open(filename, "wt") as fp:
        mesh = cylinder()
        fp.write(meshex.stl_dumps(mesh))


def export_stl_bin(filename):
    with open(filename, "wb") as fp:
        mesh = cylinder()
        fp.write(meshex.stl_dumpb(mesh))


def export_off(filename):
    with open(filename, "wt") as fp:
        mesh = cylinder()
        fp.write(meshex.off_dumps(mesh))


def export_obj(filename):
    with open(filename, "wt") as fp:
        mesh = cylinder()
        fp.write(meshex.obj_dumps(mesh))


def export_ply(filename):
    with open(filename, "wb") as fp:
        mesh = cylinder()
        fp.write(meshex.ply_dumpb(mesh))


def main():
    export_scad(DIR / "cylinder.scad")
    export_stl_asc(DIR / "cylinder_asc.stl")
    export_stl_bin(DIR / "cylinder_bin.stl")
    export_off(DIR / "cylinder.off")
    export_obj(DIR / "cylinder.obj")
    export_ply(DIR / "cylinder.ply")


if __name__ == "__main__":
    main()

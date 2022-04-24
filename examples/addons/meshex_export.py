#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.addons import meshex
from ezdxf.render.forms import cylinder, sphere

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

SIDES = 16
NAME = "sphere"


def make_mesh(sides: int):
    if NAME == "sphere":
        return sphere(count=sides, stacks=sides // 2)
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


def export_ifc4(filename, kind):
    with open(filename, "wt") as fp:
        mesh = make_mesh(SIDES)
        fp.write(meshex.ifc4_dumps(mesh, kind, color=(1, .1, .1), layer="ezdxf-ifc4"))


def export_dxf(filename):
    doc = ezdxf.new()
    mesh = make_mesh(SIDES)
    mesh.render_mesh(doc.modelspace())
    doc.saveas(filename)


def main():
    export_scad(DIR / f"{NAME}.scad")
    export_stl_asc(DIR / f"{NAME}_asc.stl")
    export_stl_bin(DIR / f"{NAME}_bin.stl")
    export_off(DIR / f"{NAME}.off")
    export_obj(DIR / f"{NAME}.obj")
    export_ply(DIR / f"{NAME}.ply")
    export_dxf(DIR / f"{NAME}.dxf")
    export_ifc4(
        DIR / f"{NAME}_polygon_face_set.ifc",
        meshex.IfcEntityType.POLYGON_FACE_SET,
    )
    export_ifc4(
        DIR / f"{NAME}_closed_shell.ifc", meshex.IfcEntityType.CLOSED_SHELL
    )


if __name__ == "__main__":
    main()

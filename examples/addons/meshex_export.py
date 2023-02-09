#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import meshex
from ezdxf.render.forms import cylinder, sphere

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to export MeshBuilder instances as 3D file formats:
# STL, OBJ, PLY and IFC4
#
# docs: https://ezdxf.mozman.at/docs/addons/meshex.html
# ------------------------------------------------------------------------------

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
        fp.write(meshex.ifc4_dumps(mesh, kind, color=(1.0, 0.1, 0.1)))


def export_ifc4ZIP(filename, kind):
    mesh = make_mesh(SIDES)
    meshex.export_ifcZIP(filename, mesh, kind, color=(1.0, 0.1, 0.1))


def export_ifc4_open_cylinder(filename, kind):
    with open(filename, "wt") as fp:
        mesh = cylinder(count=SIDES, caps=False)
        fp.write(meshex.ifc4_dumps(mesh, kind, color=(0.1, 1.0, 0.1)))


def export_dxf(filename):
    doc = ezdxf.new()
    mesh = make_mesh(SIDES)
    mesh.render_mesh(doc.modelspace())
    doc.saveas(filename)


def main():
    export_scad(CWD / f"{NAME}.scad")
    export_stl_asc(CWD / f"{NAME}_asc.stl")
    export_stl_bin(CWD / f"{NAME}_bin.stl")
    export_off(CWD / f"{NAME}.off")
    export_obj(CWD / f"{NAME}.obj")
    export_ply(CWD / f"{NAME}.ply")
    export_dxf(CWD / f"{NAME}.dxf")
    export_ifc4(
        CWD / f"{NAME}_polygon_face_set.ifc",
        meshex.IfcEntityType.POLYGON_FACE_SET,
    )
    export_ifc4(
        CWD / f"{NAME}_closed_shell.ifc", meshex.IfcEntityType.CLOSED_SHELL
    )
    export_ifc4ZIP(
        CWD / f"{NAME}_closed_shell.ifcZIP", meshex.IfcEntityType.CLOSED_SHELL
    )
    export_ifc4_open_cylinder(
        CWD / f"open_cylinder_open_shell.ifc", meshex.IfcEntityType.OPEN_SHELL
    )
    export_ifc4_open_cylinder(
        CWD / f"open_cylinder_polygon_face_set.ifc", meshex.IfcEntityType.POLYGON_FACE_SET
    )


if __name__ == "__main__":
    main()

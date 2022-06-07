#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Sequence
from pathlib import Path
import ezdxf
from ezdxf.math import Vec3
from ezdxf.render import forms, MeshTransformer
from ezdxf.addons import meshex, openscad

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")


def make_rect_room(
    length: float, width: float, height: float, wall_thickness: float
):
    wall_thickness2 = 2 * wall_thickness
    outer_polygon = forms.box(length, width)
    inner_polygon = forms.box(
        length - wall_thickness2, width - wall_thickness2
    )
    outer_box = make_polyhedron(outer_polygon, height)
    inner_box = make_polyhedron(inner_polygon, height)
    inner_box.translate(wall_thickness, wall_thickness, 0)
    return outer_box, inner_box


def make_polyhedron(vertices: Sequence[Vec3], height: float) -> MeshTransformer:
    # create polyhedrons from contours like polylines
    height_vec = Vec3(0, 0, height)
    bottom_profile = list(vertices)
    top_profile = list(forms.translate(bottom_profile, height_vec))
    return forms.from_profiles_linear([bottom_profile, top_profile], caps=True)


def walls_by_openscad() -> MeshTransformer:
    # create 3 rectangular rooms from an outer box minus an inner box
    o1, i1 = make_rect_room(10, 5, 2.6, 0.3)
    o2, i2 = o1.copy().translate(15, 0, 0), i1.copy().translate(15, 0, 0)
    o3, i3 = o1.copy().translate(7.5, 2.5, 0), i1.copy().translate(7.5, 2.5, 0)

    # Flipping the normals for OpenSCAD is best practice, but this
    # example works also without that.
    for m in (o1, o2, o3, i1, i2, i3):
        m.flip_normals()
    """
    // https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/CSG_Modelling
    // create an OpenSCAD script like this:
    difference() {
        union() {  // add all outer boxes
            o1;
            o2;
            o3;
        }  // and subtract all inner boxes
        i1;
        i2;
        i3;
    }
    """
    script = openscad.Script()
    script.add("difference() { union() {")
    script.add_polyhedron(o1)
    script.add_polyhedron(o2)
    script.add_polyhedron(o3)
    script.add("}")
    script.add_polyhedron(i1)
    script.add_polyhedron(i2)
    script.add_polyhedron(i3)
    script.add("}")
    return openscad.run(script.get_string())


def main(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    wall_mesh = walls_by_openscad()
    wall_mesh.render_mesh(msp, dxfattribs={"layer": "WALL_MESH"})
    doc.saveas(DIR / (filename + ".dxf"))
    with open(DIR / (filename + ".obj"), "wt") as fp:
        fp.write(meshex.obj_dumps(wall_mesh))


if __name__ == "__main__":
    main("walls3d_openscad")

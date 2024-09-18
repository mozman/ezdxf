# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf import bbox, select

CWD = Path("~/Desktop/Now/ezdxf/select").expanduser()
if not CWD.exists():
    CWD = Path(".")

BASE = "base.dxf"


def select_inside_window():
    print("\nselect inside window:")
    doc = ezdxf.readfile(CWD / BASE)

    window = select.Window((150, 105), (280, 240))
    for entity in select.bbox_inside(window, doc.modelspace()):
        print(str(entity))


def select_outside_window():
    print("\nselect outside window:")
    doc = ezdxf.readfile(CWD / BASE)

    window = select.Window((185, 105), (245, 240))
    for entity in select.bbox_outside(window, doc.modelspace()):
        print(str(entity))


def select_overlap_window():
    print("\nselect overlap window:")
    doc = ezdxf.readfile(CWD / BASE)

    window = select.Window((150, 105), (280, 240))
    for entity in select.bbox_overlap(window, doc.modelspace()):
        print(str(entity))


def select_crosses_fence():
    print("\nselect crossing fence:")
    doc = ezdxf.readfile(CWD / BASE)
    msp = doc.modelspace()

    for entity in select.bbox_crosses_fence(
        [(83, 101), (186, 193), (300, 107)], msp.query("*").layer == "Entities"
    ):
        print(str(entity))


def select_chained():
    print("\nselect chained entities:")
    doc = ezdxf.readfile(CWD / "chained.dxf")
    msp = doc.modelspace()
    line = msp.query("LINE").first
    for entity in select.bbox_chained(line, msp.query("*").layer == "Entities"):
        print(str(entity))


def select_point():
    print("\nselect entities by point in bbox:")
    doc = ezdxf.readfile(CWD / "point.dxf")
    msp = doc.modelspace()
    for entity in select.point_in_bbox((264, 140), msp.query("*").layer == "Entities"):
        print(str(entity))


def select_by_circle():
    print("\nselect by circle:")
    doc = ezdxf.readfile(CWD / BASE)
    msp = doc.modelspace()
    entity = msp.query("CIRCLE").first
    circle = select.Circle(entity.dxf.center, radius=60)
    for entity in select.bbox_overlap(circle, msp.query("*").layer == "Entities"):
        print(str(entity))


def select_by_polygon():
    print("\nselect by polygon:")
    doc = ezdxf.readfile(CWD / BASE)
    msp = doc.modelspace()

    vertices = [(110, 168), (110, 107), (316, 107), (316, 243), (236, 243)]
    polygon = select.Polygon(vertices)
    for entity in select.bbox_inside(polygon, msp):
        print(str(entity))


def draw_bboxes(filename: str) -> None:
    doc = ezdxf.readfile(CWD / filename)
    msp = doc.modelspace()
    for entity in msp.query("*").layer == "Entities":
        box = bbox.extents((entity,))
        msp.add_lwpolyline(
            box.rect_vertices(), close=True, dxfattribs={"layer": "BoundingBox"}
        )
    doc.saveas(CWD / "bboxes.dxf")


if __name__ == "__main__":
    draw_bboxes(BASE)
    select_inside_window()
    select_outside_window()
    select_overlap_window()
    select_crosses_fence()
    select_chained()
    select_point()
    select_by_circle()
    select_by_polygon()

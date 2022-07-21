from pathlib import Path
import json
import ezdxf
from collections import deque
from ezdxf.render import forms
from ezdxf.math import BoundingBox2d
from ezdxf.math.triangulation import mapbox_earcut_2d

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")

TEST_DATA_DIR = Path(r"..\..\integration_tests\mapbox-test-data")


def hole_in_hole():
    shape = list(forms.square(4, center=True))
    hole0 = list(forms.square(3, center=True))
    hole1 = list(forms.square(2, center=True))
    holes = [hole0, hole1]
    return shape, holes


def hole_beyond_exterior_path():
    shape = list(forms.square(4, center=True))
    hole = list(forms.translate(shape, (2, 2)))
    return shape, [hole]


def render(func):
    doc = ezdxf.new()
    msp = doc.modelspace()
    colors = deque([1, 2, 3, 4, 5, 6])

    shape, holes = func()
    msp.add_lwpolyline(shape, close=True)
    for hole in holes:
        msp.add_lwpolyline(hole, close=True)
    for triangle in mapbox_earcut_2d(shape, holes=holes):
        msp.add_solid(triangle, dxfattribs={"color": colors[0]})
        colors.rotate()

    doc.set_modelspace_vport(10)
    doc.saveas(CWD / f"{func.__name__}.dxf")


def render_mapbox_test_cases():
    for sample in TEST_DATA_DIR.glob("*.json"):
        render_test_case(sample)


def render_test_case(filepath: Path):
    print(f"processing: {filepath.name}")
    doc = ezdxf.new()
    msp = doc.modelspace()
    colors = deque([1, 2, 3, 4, 5, 6])

    with filepath.open("rt") as fp:
        data = json.load(fp)
        shape = data[0]
        holes = data[1:]

    msp.add_lwpolyline(shape, close=True, dxfattribs={"layer": "SOURCE"})
    for hole in holes:
        msp.add_lwpolyline(hole, close=True, dxfattribs={"layer": "SOURCE"})
    for triangle in mapbox_earcut_2d(shape, holes=holes):
        msp.add_solid(
            triangle, dxfattribs={"color": colors[0], "layer": "TRIANGLES"}
        )
        colors.rotate()
    bbox = BoundingBox2d(shape)
    doc.set_modelspace_vport(bbox.size.y, bbox.center)
    doc.saveas(CWD / f"{filepath.stem}.dxf")


def render_polydata():
    for data in POLYGON_DATA0:
        filename = data.name.replace(" ", "_") + ".dxf"
        doc = ezdxf.new()
        msp = doc.modelspace()
        colors = deque([1, 2, 3, 4, 5, 6])
        for triangle in mapbox_earcut_2d(data.vertices):
            msp.add_solid(triangle, dxfattribs={"color": colors[0]})
            colors.rotate()
        msp.add_lwpolyline(data.vertices, close=True)
        bbox = BoundingBox2d(data.vertices)
        doc.set_modelspace_vport(bbox.size.y, bbox.center)
        doc.saveas(CWD / filename)


class PolyData:
    def __init__(self, name, vertices):
        self.name = name
        self.vertices = vertices


POLYGON_DATA0 = [
    PolyData(
        name="Star",
        vertices=[
            (350, 75),
            (379, 161),
            (469, 161),
            (397, 215),
            (423, 301),
            (350, 250),
            (277, 301),
            (303, 215),
            (231, 161),
            (321, 161),
        ],
    ),
    PolyData(
        name="Simple Diamond",
        vertices=[
            (0, 1),
            (-1, 0),
            (0, -1),
            (1, 0),
        ],
    ),
    PolyData(
        name="No Concave Vertex",
        vertices=[
            (-2.0, -17.0),
            (-2.0, -8.0),
            (-8.0, -2.0),
            (-17.0, -2.0),
            (-20.0, -8.0),
            (-18.0, -17.0),
            (-12.0, -24.0),
            (-7.0, -22.0),
        ],
    ),
    PolyData(
        name="Slanted Side",
        vertices=[
            (-10.0, -20.0),
            (-10.0, -30.0),
            (0.0, -20.0),
            (0.0, -10.0),
            (-20.0, -10.0),
            (-20.0, -20.0),
        ],
    ),
    PolyData(
        name="New Thing",
        vertices=[
            (-20.0, -20.0),
            (-10.0, -20.0),
            (-10.0, -30.0),
            (0.0, -20.0),
            (10.0, -20.0),
            (0.0, -10.0),
            (10.0, 0.0),
            (0.0, 0.0),
            (-10.0, -10.0),
            (-10.0, 0.0),
            (-20.0, -10.0),
            (-30.0, -10.0),
        ],
    ),
    PolyData(
        name="Edge Case 1",
        vertices=[
            (40.04332790675601, -30.70794551983977),
            (54.13, -30.70794551983977),
            (54.13, -28.03),
            (69.13, -28.03),
            (69.11, -52.53),
            (40.04332790675601, -52.53),
        ],
    ),
    PolyData(  # 6
        name="Edge Case 2",
        vertices=[
            (229.28340553, 78.91250014),
            (258.42948809, 17.98278109),
            (132.01956999, -22.96900817),
            (107.97774096, 23.39276058),
            (65.85573925, 28.63846858),
            (41.66373597, -92.78859248),
            (-5.59948763, -54.18987786),
            (-44.61508682, -69.7461117),
            (-28.41208894, -106.93810071),
            (-71.11899145, -125.56044277),
            (-100.84787818, -88.51853387),
            (-211.53564549, -160.76853269),
            (-244.22754588, -147.51172179),
            (-226.83717643, -42.0984372),
            (-230.65279618, -10.5455196),
            (-240.50239817, 70.87826746),
            (-12.48219264, 137.70176109),
            (4.65848369, 204.21077075),
            (176.5243417, 193.73497584),
            (171.13537712, 87.27009315),
            (229.28340553, 78.91250014),
        ],
    ),
    PolyData(  # 7
        name="Edge Case 3-A",
        vertices=[
            (229, 78),
            (66, 28.7),
            (-244.2, -147.5),
            (-226, -42),
            (229, 78),
        ],
    ),
    PolyData(  # 8
        name="Edge Case 3-B",
        vertices=[
            (229000, 78000),
            (66000, 28700),
            (-244200, -147500),
            (-226000, -42000),
            (229000, 78000),
        ],
    ),
    PolyData(  # 9
        name="Edge Case 4",
        vertices=[
            (-1179, -842),
            (-489, -1049),
            (101, -1226),
            (520, -558),
            (779, -175),
            (856, 257),
            (544, 806),
            (-72, 713),
            (-1004, 945),
            (-988, 62),
            (-1179, -842),
        ],
    ),
]


if __name__ == "__main__":
    render_mapbox_test_cases()
    render(hole_in_hole)
    render(hole_beyond_exterior_path)
    # render_polydata()

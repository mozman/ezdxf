import pathlib
import ezdxf
from ezdxf.upright import upright

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

POLYLINE_POINTS = [
    # x, y, s, e, b
    (0, 0, 0, 0, 0),
    (2, 2, 1, 2, -1),
    (4, 0, 2, 1, 1),
    (6, 0, 0, 0, 0),
]

doc = ezdxf.new()
doc.layers.new("original", dxfattribs={"color": 2})
doc.layers.new("upright", dxfattribs={"color": 6})

blk = doc.blocks.new("example")
blk.add_arc(
    center=(5, 0, 2),
    radius=3,
    start_angle=30,
    end_angle=150,
)
blk.add_lwpolyline(POLYLINE_POINTS)
blk.add_line((0, 0), (10, 0), dxfattribs={"color": 1})
blk.add_line((0, 0), (0, 10), dxfattribs={"color": 3})
blk.add_line((0, 0, 0), (0, 0, 10), dxfattribs={"color": 5})

msp = doc.modelspace()
blk_ref = msp.add_blockref(
    name="example",
    insert=(0, 0, 4),
    dxfattribs={"extrusion": (0, 0, -1), "layer": "original", "rotation": -37},
)

blk_ref_copy = blk_ref.copy()
blk_ref_copy.dxf.layer = "upright"

upright(blk_ref_copy)
msp.add_entity(blk_ref_copy)

doc.saveas(CWD / "upright_insert.dxf")

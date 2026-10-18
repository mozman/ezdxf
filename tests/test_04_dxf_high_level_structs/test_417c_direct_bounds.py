import pytest


import random


import ezdxf


from ezdxf.layouts import VirtualLayout


from ezdxf import bbox, disassemble


from ezdxf.math import BoundingBox


@pytest.mark.parametrize("fast", [False, True])
def test_direct_line_and_point_boxes_match_primitives(fast):
    rng = random.Random(417)
    layout = VirtualLayout()
    for _ in range(50):
        start = tuple(rng.uniform(-100, 100) for _ in range(3))
        end = tuple(rng.uniform(-100, 100) for _ in range(3))
        layout.add_line(start, end, dxfattribs={"thickness": 5, "extrusion": (1, 0, 0)})
        layout.add_point(start)
    layout.add_line((2, 3, 4), (2, 3, 4))
    expected = [p.bbox(fast=fast) for p in disassemble.to_primitives(layout)]
    cache = bbox.Cache(uuid=True)
    for _ in range(2):
        result = list(bbox.multi_flat(layout, fast=fast, cache=cache))
        assert len(result) == len(expected)
        for box, reference in zip(result, expected):
            assert box.extmin == reference.extmin
            assert box.extmax == reference.extmax


@pytest.mark.parametrize("thickness", [-5, 0, 5])
@pytest.mark.parametrize("extrusion", [(0, 0, 1), (0, 0, -1), (1, 2, 3)])
def test_direct_boxes_preserve_primitive_thickness_and_extrusion_behavior(
    thickness, extrusion
):
    layout = VirtualLayout()
    attribs = {"thickness": thickness, "extrusion": extrusion}
    layout.add_line((3, 2, 1), (-4, -5, -6), dxfattribs=attribs)
    layout.add_point((4, 5, 6), dxfattribs=attribs)
    # Existing primitives represent the stored WCS endpoints/location, ignoring
    # thickness. The fast path must preserve that established limitation.
    direct = list(bbox.multi_flat(layout))
    generic = list(bbox.multi_recursive(layout))
    for result, expected in zip(direct, generic):
        assert result.extmin == expected.extmin
        assert result.extmax == expected.extmax


def test_mixed_direct_and_decomposed_bounding_boxes():
    doc = ezdxf.new()
    block = doc.blocks.new("geometry")
    block.add_line((0, 0, 1), (2, 4, 3))
    block.add_point((-1, -2, -3))
    layout = doc.modelspace()
    layout.add_blockref("geometry", (20, 30, 40), dxfattribs={"rotation": 90})
    layout.add_point((-100, 200, 10))
    layout.add_line((2, 3, 7), (8, -5, 9))
    layout.add_ray((1000, 1000), (1, 0))  # unsupported
    reference = BoundingBox()
    for box in bbox.multi_recursive(layout):
        reference.extend(box)
    result = bbox.extents(layout)
    assert result.extmin.isclose(reference.extmin)
    assert result.extmax.isclose(reference.extmax)

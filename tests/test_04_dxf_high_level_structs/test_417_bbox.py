#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import pickle
import random
import ezdxf
from ezdxf.layouts import VirtualLayout
from ezdxf import bbox, disassemble
from ezdxf.render.forms import square, translate
from ezdxf.math import BoundingBox


@pytest.fixture(scope="module")
def points1():
    lay = VirtualLayout()
    lay.add_point((-1, -2, -3))
    lay.add_point((4, 5, 6))
    return lay


def test_extend(points1):
    box = bbox.extents(points1)
    assert box.extmin == (-1, -2, -3)
    assert box.extmax == (4, 5, 6)


def test_line():
    lay = VirtualLayout()
    lay.add_line((0, 0), (10, 0))
    lay.add_line((0, 1), (10, 1))
    box = bbox.extents(lay)
    assert box.extmin == (0, 0, 0)
    assert box.extmax == (10, 1, 0)


def solid_entities():
    lay = VirtualLayout()
    lay.add_solid(translate(square(1), (-10, -10)))
    lay.add_solid(translate(square(1), (10, 10)))
    return lay


def solid_blockrefs():
    doc = ezdxf.new()
    blk = doc.blocks.new("Solid")
    blk.add_solid(square(1))
    msp = doc.modelspace()
    msp.add_blockref("Solid", (-10, -10))
    msp.add_blockref("Solid", (10, 10))
    return msp


def test_empty_cache():
    assert bbox.Cache().has_data is False


@pytest.mark.parametrize(
    "solids",
    [solid_entities(), solid_blockrefs()],
    ids=["entities", "blockrefs"],
)
@pytest.mark.parametrize("func", [bbox.multi_flat, bbox.multi_recursive])
def test_multi_boxes(solids, func):
    box = list(func(solids))
    assert box[0].extmin == (-10, -10)
    assert box[0].extmax == (-9, -9)
    assert box[1].extmin == (10, 10)
    assert box[1].extmax == (11, 11)


def test_cache_usage_without_handles(points1):
    # Entities in VirtualLayouts have no handles:
    cache = bbox.Cache()
    for _ in range(10):
        bbox.extents(points1, cache=cache)
    assert cache.hits == 0


def test_cache_usage_with_uuids(points1):
    # Entities in VirtualLayouts have no handles:
    cache = bbox.Cache(uuid=True)
    for _ in range(10):
        bbox.extents(points1, cache=cache)
    assert cache.hits == 18


@pytest.fixture(scope="module")
def msp_solids():
    return solid_blockrefs()


@pytest.mark.parametrize("func", [bbox.multi_flat, bbox.extents])
def test_cache_usage_for_flat_multi_boxes(msp_solids, func):
    cache = bbox.Cache()
    for _ in range(10):
        list(func(msp_solids, cache=cache))

    # This works because flat processing has not to yield bounding boxes for
    # sub entities, caching top level bounding boxes works well.
    assert cache.misses == 2 + 2  # first 2xINSERT, 2xSOLID in INSERT
    assert cache.hits == 9 * 2  # 9 x 2xINSERT


def test_cache_usage_for_recreation_on_the_fly(msp_solids):
    cache = bbox.Cache(uuid=True)
    for _ in range(10):
        list(bbox.multi_recursive(msp_solids, cache=cache))

    # This does not work well, because recursive processing has to yield the
    # bounding boxes for all sub entities. These sub entities are created on the
    # fly for every call and do not have a handle and always gets a new UUID,
    # which is the meaning of an UUID.
    # The INSERT entity, which has a handle, gets no own bounding box and is
    # therefore not cached.
    assert cache.misses == 20
    assert cache.hits == 0


@pytest.mark.parametrize("func", [bbox.multi_flat, bbox.extents, bbox.multi_recursive])
def test_cache_usage_for_reused_virtual_entities(msp_solids, func):
    cache = bbox.Cache()
    # Create flat entity structure by yourself, so that virtual entities are
    # only created once:
    entities = list(disassemble.recursive_decompose(msp_solids))
    for _ in range(10):
        list(func(entities, cache=cache))

    # This does not work well by "handle only" usage, because 'entities' contains
    # virtual entities which have no handle and therefore are not cached:
    # multi_flat and extents, have a second access stage and triggers 2x20 cache
    # misses but this is just a cache access issue, this does not trigger 40
    # bounding box calculations!
    # multi_recursive is the lowest level and has only 20 cache misses.
    assert cache.misses in (20, 40)  # virtual entities do not have handles
    assert cache.hits == 0  # parent INSERT bbox is not calculated and cached


@pytest.mark.parametrize("func", [bbox.multi_flat, bbox.extents, bbox.multi_recursive])
def test_cache_usage_with_uuids_for_reused_virtual_entities(msp_solids, func):
    cache = bbox.Cache(uuid=True)
    # Create flat entity structure by yourself, so that virtual entities are
    # only created once:
    entities = list(disassemble.recursive_decompose(msp_solids))
    for _ in range(10):
        list(func(entities, cache=cache))

    # This works, because virtual entities are cached by UUID
    # multi_flat and extents, have a second access stage: 2x2 misses, but
    # triggers only 2 bounding box calculations.
    # multi_recursive is the lowest level and has only 2 cache misses.
    assert cache.misses in (2, 4)
    assert cache.hits == 18


@pytest.fixture
def circle():
    lay = VirtualLayout()
    lay.add_circle((0, 0), radius=100)
    return lay


def test_fast_bounding_box_calculation(circle):
    box = bbox.extents(circle, fast=True)
    assert box.extmin == (-100, -100)
    assert box.extmax == (+100, +100)


def test_precise_bounding_box_calculation(circle):
    box = bbox.extents(circle, fast=False)
    assert box.extmin == (-100, -100)
    assert box.extmax == (+100, +100)


@pytest.mark.parametrize("first_fast", [False, True])
@pytest.mark.parametrize("func", [bbox.extents, bbox.multi_flat, bbox.multi_recursive])
@pytest.mark.parametrize("in_block", [False, True])
def test_cache_separates_precise_and_fast_boxes(first_fast, func, in_block):
    doc = ezdxf.new()
    layout = doc.blocks.new("curve") if in_block else doc.modelspace()
    spline = layout.add_open_spline([(0, 0), (1, 30), (2, 30), (3, 0)], degree=3)
    entity = doc.modelspace().add_blockref("curve", (0, 0)) if in_block else spline
    cache = bbox.Cache(uuid=True)
    for fast in (first_fast, not first_fast, first_fast):
        result = func([entity], fast=fast, cache=cache)
        box = result if func is bbox.extents else next(iter(result))
        assert box.extmax.y == pytest.approx(30.0 if fast else 22.5)


@pytest.mark.parametrize("use_uuid", [False, True])
def test_cache_distinguishes_identical_handles_in_different_documents(use_uuid):
    point1 = ezdxf.new().modelspace().add_point((0, 0))
    point2 = ezdxf.new().modelspace().add_point((100, 100))
    assert point1.dxf.handle == point2.dxf.handle
    cache = bbox.Cache(uuid=use_uuid)
    assert bbox.extents([point1], cache=cache).extmin == (0, 0, 0)
    assert bbox.extents([point2], cache=cache).extmin == (100, 100, 0)


def test_cache_legacy_access_and_invalidation():
    point = ezdxf.new().modelspace().add_point((1, 2, 3))
    box = BoundingBox([point.dxf.location])
    cache = bbox.Cache()
    cache.store(point, box, fast=True)
    assert cache.get(point) is box
    assert cache.get(point, fast=False) is None
    precise = BoundingBox([point.dxf.location])
    cache.store(point, precise)
    assert cache.get(point) is precise
    assert cache.get(point, fast=True) is box
    cache.invalidate([point])
    cache.invalidate([point])  # already absent
    assert cache.get(point, fast=False) is None
    assert cache.get(point, fast=True) is None


@pytest.mark.parametrize("virtual", [False, True])
def test_cache_and_entities_survive_separate_pickle_roundtrips(virtual):
    doc = ezdxf.new()
    point = doc.modelspace().add_point((1, 2, 3))
    if virtual:
        point = point.copy()
    cache = bbox.Cache(uuid=virtual)
    bbox.extents([point], cache=cache, fast=False)
    bbox.extents([point], cache=cache, fast=True)
    restored_cache = pickle.loads(pickle.dumps(cache))
    restored_point = pickle.loads(pickle.dumps(point))
    for fast in (False, True):
        assert restored_cache.get(restored_point, fast=fast).extmin == (1, 2, 3)
    restored_cache.invalidate([restored_point])
    assert not restored_cache.has_data


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


if __name__ == "__main__":
    pytest.main([__file__])

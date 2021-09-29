#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.layouts import VirtualLayout
from ezdxf import bbox, disassemble
from ezdxf.render.forms import square, translate


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


@pytest.mark.parametrize(
    "func", [bbox.multi_flat, bbox.extents, bbox.multi_recursive]
)
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


@pytest.mark.parametrize(
    "func", [bbox.multi_flat, bbox.extents, bbox.multi_recursive]
)
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


def test_bbox_from_control_points(circle):
    box = bbox.extents(circle, flatten=0)
    assert box.extmin == (-100, -100)
    assert box.extmax == (+100, +100)


def test_bbox_from_rough_flattening(circle):
    box = bbox.extents(circle, flatten=5)
    assert box.extmin != (-100, -100), "did not expect a precise result"
    assert box.extmax != (+100, +100), "did not expect a precise result"


def test_bbox_from_precise_flattening(circle):
    box = bbox.extents(circle, flatten=0.0001)
    assert box.extmin.isclose(
        (-100, -100), abs_tol=0.0001
    ), "expected a very close result"
    assert box.extmax.isclose(
        (+100, +100), abs_tol=0.0001
    ), "expected a very_close result"


if __name__ == "__main__":
    pytest.main([__file__])

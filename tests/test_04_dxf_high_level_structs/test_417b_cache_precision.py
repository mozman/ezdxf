import pytest


import ezdxf


from ezdxf import bbox


from ezdxf.math import BoundingBox


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

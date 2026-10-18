import pytest


import pickle


import ezdxf


from ezdxf import bbox


@pytest.mark.parametrize("use_uuid", [False, True])
def test_cache_distinguishes_identical_handles_in_different_documents(use_uuid):
    point1 = ezdxf.new().modelspace().add_point((0, 0))
    point2 = ezdxf.new().modelspace().add_point((100, 100))
    assert point1.dxf.handle == point2.dxf.handle
    cache = bbox.Cache(uuid=use_uuid)
    assert bbox.extents([point1], cache=cache).extmin == (0, 0, 0)
    assert bbox.extents([point2], cache=cache).extmin == (100, 100, 0)


@pytest.mark.parametrize("virtual", [False, True])
def test_cache_and_entities_survive_separate_pickle_roundtrips(virtual):
    doc = ezdxf.new()
    point = doc.modelspace().add_point((1, 2, 3))
    if virtual:
        point = point.copy()
    cache = bbox.Cache(uuid=virtual)
    bbox.extents([point], cache=cache)
    restored_cache = pickle.loads(pickle.dumps(cache))
    restored_point = pickle.loads(pickle.dumps(point))
    assert restored_cache.get(restored_point).extmin == (1, 2, 3)
    restored_cache.invalidate([restored_point])
    assert not restored_cache.has_data

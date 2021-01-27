#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.layouts import VirtualLayout
from ezdxf import bbox
from ezdxf.render.forms import square, translate


@pytest.fixture(scope='module')
def points1():
    lay = VirtualLayout()
    lay.add_point((-1, -2, -3))
    lay.add_point((4, 5, 6))
    return lay


def test_extend(points1):
    box = bbox.extends(points1)
    assert box.extmin == (-1, -2, -3)
    assert box.extmax == (4, 5, 6)


def solid_entities():
    lay = VirtualLayout()
    lay.add_solid(translate(square(1), (-10, -10)))
    lay.add_solid(translate(square(1), (10, 10)))
    return lay


def solid_blockrefs():
    doc = ezdxf.new()
    blk = doc.blocks.new('Solid')
    blk.add_solid(square(1))
    msp = doc.modelspace()
    msp.add_blockref('Solid', (-10, -10))
    msp.add_blockref('Solid', (10, 10))
    return msp


@pytest.mark.parametrize('solids', [solid_entities(), solid_blockrefs()],
                         ids=['entities', 'blockrefs'])
@pytest.mark.parametrize('func', [bbox.multi_flat, bbox.multi_recursive])
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
        bbox.extends(points1, cache)
    assert cache.hits == 0


@pytest.fixture(scope='module')
def msp_solids():
    return solid_blockrefs()


@pytest.mark.parametrize('func', [bbox.multi_flat, bbox.extends])
def test_cache_usage_for_flat_multi_boxes(msp_solids, func):
    cache = bbox.Cache()
    for _ in range(10):
        list(func(msp_solids, cache))

    # This works because flat processing has not to yield bounding boxes for
    # sub entities, cached bounding box is good.
    # bbox.extends uses bbox.multi_flat, therefore same behavior
    assert cache.misses == 2 + 2  # first 2xINSERT, 2xSOLID in INSERT
    assert cache.hits == 2 * 9  # following 9 rounds


def test_cache_usage_for_recursive_multi_boxes(msp_solids):
    cache = bbox.Cache()
    for _ in range(10):
        list(bbox.multi_recursive(msp_solids, cache))

    # This does not work because recursive processing has to yield the
    # bounding boxes for all sub entities, the INSERT itself (which has a
    # handle) is not cached.
    assert cache.misses == 20  # virtual entities do not have handles
    assert cache.hits == 0  # parent INSERT bbox is not calculated and cached


if __name__ == '__main__':
    pytest.main([__file__])

from __future__ import annotations


import pytest


import ezdxf


from ezdxf import bbox, select


def test_selection_cache_does_not_change_precise_measurements():
    spline = (
        ezdxf.new()
        .modelspace()
        .add_open_spline([(0, 0), (1, 30), (2, 30), (3, 0)], degree=3)
    )
    cache = bbox.Cache()
    select.bbox_overlap(select.Window((-1, -1), (4, 31)), [spline], cache=cache)
    assert bbox.extents([spline], cache=cache).extmax.y == pytest.approx(22.5)

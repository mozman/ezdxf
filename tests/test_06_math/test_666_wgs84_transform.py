# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.math._construct import world_mercator_to_gps, gps_to_world_mercator
from ezdxf.math import Vec2
from ezdxf.acc import USE_C_EXT

if USE_C_EXT:
    try:
        from ezdxf.acc.construct import world_mercator_to_gps as cy_world_mercator_to_gps
        from ezdxf.acc.construct import gps_to_world_mercator as cy_gps_to_world_mercator
    except ImportError:
        USE_C_EXT = False

DATA = [
    [Vec2(15, 47), Vec2(1669792.36, 5910809.62)],
    [Vec2(-15, 47), Vec2(-1669792.36, 5910809.62)],
    [Vec2(15, -47), Vec2(1669792.36, -5910809.62)],
    [Vec2(-15, -47), Vec2(-1669792.36, -5910809.62)],
    [Vec2(0, 0), Vec2(0, 0)],
]


@pytest.mark.parametrize("deg, coords", DATA)
def test_common_WGS84_projection_cpython(deg: Vec2, coords: Vec2):
    projected = Vec2(gps_to_world_mercator(deg.x, deg.y))
    assert projected.round(2).isclose(coords)
    # inverse projection
    assert Vec2(world_mercator_to_gps(projected.x, projected.y)).isclose(deg)


@pytest.mark.skipif(USE_C_EXT is False, reason="Cython implementation not available")
@pytest.mark.parametrize("deg, coords", DATA)
def test_common_WGS84_projection_cython(deg: Vec2, coords: Vec2):
    projected = Vec2(cy_gps_to_world_mercator(deg.x, deg.y))
    assert projected.round(2).isclose(coords)
    # inverse projection
    assert Vec2(cy_world_mercator_to_gps(projected.x, projected.y)).isclose(deg)


if __name__ == "__main__":
    pytest.main([__file__])

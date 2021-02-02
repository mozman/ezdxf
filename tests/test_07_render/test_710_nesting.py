#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.render.forms import square, translate
from ezdxf.render import Path, nesting

EXTERIOR = list(translate(square(10), (-5, -5)))
EXT1_PATH = Path.from_vertices(EXTERIOR)
EXT2_PATH = Path.from_vertices(translate(EXTERIOR, (11, 0)))

CENTER_HOLE1 = list(translate(square(8), (-4, -4)))
CH1_PATH = Path.from_vertices(CENTER_HOLE1)

CENTER_HOLE2 = list(translate(square(6), (-3, -3)))
CH2_PATH = Path.from_vertices(CENTER_HOLE2)

LEFT_HOLE = list(translate(square(2.1), (-3, -1)))
LH_PATH = Path.from_vertices(LEFT_HOLE)

RIGHT_HOLE = list(translate(square(2.0), (3, -1)))
RH_PATH = Path.from_vertices(RIGHT_HOLE)

DETECTION_DATA = [
    pytest.param(
        # Each polygon is a list of paths
        [EXT1_PATH], [[EXT1_PATH]],
        id='1 path'),
    pytest.param(
        # returns the path sorted by area, and reversed if equal sized
        [EXT1_PATH, EXT2_PATH], [[EXT2_PATH], [EXT1_PATH]],
        id='2 separated paths'),
    pytest.param(
        [CH1_PATH, EXT1_PATH], [[EXT1_PATH, [CH1_PATH]]],
        id='1 nested sub-path'),
    pytest.param(
        [CH1_PATH, EXT1_PATH, CH2_PATH], [[EXT1_PATH, [CH1_PATH, [CH2_PATH]]]],
        id='2 nested sub-path'),
    pytest.param(
        [RH_PATH, LH_PATH, EXT1_PATH], [[EXT1_PATH, [LH_PATH], [RH_PATH]]],
        id='2 separated sub-paths'),
]


@pytest.mark.parametrize('paths,polygons', DETECTION_DATA)
def test_fast_bbox_detection(paths, polygons):
    assert nesting.fast_bbox_detection(paths) == polygons


@pytest.mark.parametrize('polygons,exp_ccw,exp_cw', [
    pytest.param(
        [[EXT1_PATH]],
        [EXT1_PATH],  # ccw paths
        [],  # cw paths
        id='1 polygon'),
    pytest.param(
        [[EXT1_PATH], [EXT1_PATH]],
        [EXT1_PATH, EXT1_PATH],  # ccw paths
        [],  # cw paths
        id='2 polygons'),
    pytest.param(
        [[EXT1_PATH, [CH1_PATH]]],
        [EXT1_PATH],  # ccw paths
        [CH1_PATH],  # cw paths
        id='1 polygon 1 nested sub-polygon'),
    pytest.param(
        [[EXT1_PATH, [CH1_PATH, [CH1_PATH]]]],
        [EXT1_PATH, CH1_PATH],  # ccw paths
        [CH1_PATH],  # cw paths
        id='1 polygon 2 nested sub-polygons'
    ),
    pytest.param(
        [[EXT1_PATH, [CH1_PATH], [CH1_PATH]]],
        [EXT1_PATH],  # ccw paths
        [CH1_PATH, CH1_PATH],  # cw paths
        id='1 polygon 2 separated sub-polygons'
    ),
])
def test_winding_deconstruction(polygons, exp_ccw, exp_cw):
    ccw, cw = nesting.winding_deconstruction(polygons)
    assert ccw == exp_ccw
    assert cw == exp_cw


@pytest.mark.parametrize('polygons,n', [
    pytest.param(
        [[EXT1_PATH]], 1,
        id='1 polygon'),
    pytest.param(
        [[EXT1_PATH], [EXT1_PATH]], 2,
        id='2 polygons'),
    pytest.param(
        [[EXT1_PATH, [CH1_PATH]]], 2,
        id='1 polygon 1 nested sub-polygon'),
    pytest.param(
        [[EXT1_PATH, [CH1_PATH, [CH1_PATH]]]], 3,
        id='1 polygon 2 nested sub-polygons'
    ),
    pytest.param(
        [[EXT1_PATH, [CH1_PATH], [CH1_PATH]]], 3,
        id='1 polygon 2 separated sub-polygons'
    ),
    pytest.param(
        [[EXT1_PATH, [CH1_PATH, [CH2_PATH]], [CH1_PATH, [CH2_PATH]]]], 5,
        id='1 polygon 2 separated nested sub-polygons'
    ),
])
def test_flatten_polygons(polygons, n):
    nlists = 0
    npaths = 0
    for path in list(nesting.flatten_polygons(polygons)):
        if isinstance(path, Path):
            npaths += 1
        elif isinstance(path, list):
            nlists += 1
        else:
            raise TypeError('?')

    assert nlists == 0
    assert npaths == n


if __name__ == '__main__':
    pytest.main([__file__])

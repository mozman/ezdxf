#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Sequence, Iterable, List
import os
import json
from pathlib import Path
from functools import partial
import pytest
from ezdxf.math import Vec2, UVec
from ezdxf.math._mapbox_earcut import earcut as _py_earcut

CYTHON = "Cython"
try:
    from ezdxf.acc.mapbox_earcut import earcut as _cy_earcut
except ImportError:
    CYTHON = "CPython"
    _cy_earcut = _py_earcut


def earcut_driver(
    exterior: Iterable[UVec],
    holes: Iterable[Iterable[UVec]] = None,
    func=_py_earcut,
) -> List[Sequence[Vec2]]:
    points: List[Vec2] = Vec2.list(exterior)
    if len(points) == 0:
        return []
    holes_: List[List[Vec2]] = []
    if holes:
        holes_ = [Vec2.list(hole) for hole in holes]
    return func(points, holes_)


py_earcut = partial(earcut_driver, func=_py_earcut)
cy_earcut = partial(earcut_driver, func=_cy_earcut)


BASEDIR = os.path.dirname(__file__)
DATADIR = "mapbox-test-data"

EXPECTED = {
    "bad-diagonals": 7,
    "bad-hole": 42,
    "boxy": 57,
    "building": 13,
    "collinear-diagonal": 14,
    "degenerate": 0,
    "dude": 106,
    "eberly-3": 73,
    "eberly-6": 1429,
    "empty-square": 0,
    "filtered-bridge-jhl": 25,
    "hilbert": 1024,
    "hole-touching-outer": 77,
    "hourglass": 2,
    "infinite-loop-jhl": 0,
    "issue107": 0,
    # "issue111": 19,  # error? - I don't see it!
    "issue119": 18,
    "issue131": 12,
    "issue142": 4,
    "issue149": 2,
    "issue16": 12,
    "issue17": 11,
    "issue29": 40,
    "issue34": 139,
    "issue35": 844,
    "issue45": 10,
    "issue52": 109,
    "issue83": 0,
    "outside-ring": 64,
    "rain": 2681,
    "self-touching": 124,
    "shared-points": 4,
    "simplified-us-border": 120,
    "steiner": 9,
    "touching-holes": 57,
    "touching2": 8,
    "touching3": 15,
    # "touching4": 20,  # error? - I don't see it!
    "water": 2482,
    # "water-huge": 5177,  # long running test
    # "water-huge2": 4462,  # long running test
    "water2": 1212,
    "water3": 197,
    "water3b": 25,
    "water4": 705,
}

FILEPATHS = list(
    p for p in (Path(BASEDIR) / DATADIR).glob("*.json") if p.stem in EXPECTED
)


@pytest.fixture(params=FILEPATHS, ids=[p.stem for p in FILEPATHS])
def filename(request):
    return request.param


@pytest.mark.parametrize(
    "earcut", [py_earcut, cy_earcut], ids=("CPython", CYTHON)
)
def test_mapbox_earcut(filename: Path, earcut):
    name = filename.stem
    with filename.open("rt") as fp:
        data = json.load(fp)
        shape = data[0]
        holes = data[1:]
        triangles = earcut(shape, holes)
        assert len(triangles) == EXPECTED[name], f"{name}.json failed"


if __name__ == "__main__":
    pytest.main([__file__])

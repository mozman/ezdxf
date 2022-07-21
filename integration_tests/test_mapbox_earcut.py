#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import os
import json
from pathlib import Path
import pytest

from ezdxf.math.triangulation import mapbox_earcut_2d


BASEDIR = os.path.dirname(__file__)
DATADIR = "mapbox-test-data"

EXPECTED = {
    "bad-diagonals": 7,
    # "bad-hole": 42,  # error
    # "boxy": 57,  # error
    "building": 13,
    "collinear-diagonal": 14,
    "degenerate": 0,
    "dude": 106,
    "eberly-3": 73,
    "eberly-6": 1429,
    "empty-square": 0,
    # "filtered-bridge-jhl": 25,  # error
    "hilbert": 1024,
    "hole-touching-outer": 77,
    "hourglass": 2,
    # "infinite-loop-jhl": 0,  # error
    "issue107": 0,
    # "issue111": 19,  # error
    "issue119": 18,
    "issue131": 12,
    "issue142": 4,
    # "issue149": 2,  # error
    "issue16": 12,
    "issue17": 11,
    "issue29": 40,
    "issue34": 139,
    "issue35": 844,
    "issue45": 10,
    "issue52": 109,
    "issue83": 0,
    # "outside-ring": 64,  # error
    # "rain": 2681,  # error
    "self-touching": 124,
    "shared-points": 4,
    # "simplified-us-border": 120,  # error
    "steiner": 9,
    "touching-holes": 57,
    "touching2": 8,
    "touching3": 15,
    # "touching4": 20,  # error
    # "water": 2482,  # error
    # "water-huge": 5177,  # error
    # "water-huge2": 4462,  # infinite loop
    # "water2": 1212,  # error
    # "water3": 197,  # error
    # "water3b": 25,  # error
    # "water4": 705,  # error
}

FILEPATHS = list(
    p for p in (Path(BASEDIR) / DATADIR).glob("*.json") if p.stem in EXPECTED
)


@pytest.fixture(params=FILEPATHS, ids=[p.stem for p in FILEPATHS])
def filename(request):
    return request.param


def test_mapbox_earcut(filename: Path):
    name = filename.stem
    with filename.open("rt") as fp:
        data = json.load(fp)
        shape = data[0]
        holes = data[1:]
        triangles = list(mapbox_earcut_2d(shape, holes))
        assert len(triangles) == EXPECTED[name], f"{name}.json failed"


if __name__ == "__main__":
    pytest.main([__file__])

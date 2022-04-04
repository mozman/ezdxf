#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.entities import Polyline
from ezdxf import path


@pytest.fixture
def polyline():
    e = Polyline.new(
        dxfattribs={
            "layer": "0",
            "elevation": (0.0, 0.0, 1.391912e19),
            "flags": 1,
        },
    )
    e.append_vertex(
        (25.03050985682449, 458.1099322425544, 1.391912e19), dxfattribs={}
    )
    e.append_vertex(
        (25.03050985682461, 443.1838806339785, 1.391912e19),
        dxfattribs={"bulge": -0.1622776601683793},
    )
    return e


def test_flattening_raises_recursion_error(polyline):
    p = path.make_path(polyline)
    with pytest.raises(RecursionError):
         list(p.flattening(0.001))


if __name__ == "__main__":
    pytest.main([__file__])

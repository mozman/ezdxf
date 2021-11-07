#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import BoundingBox
from ezdxf.render.trace import LinearTrace


@pytest.mark.xfail(reason="Error in LinearTrace.faces()")
def test_linear_trace_builder():
    width = 30
    trace = LinearTrace()
    trace.add_station((100, 0), width, width)
    trace.add_station((100_000, 0), width, width)
    trace.add_station((0, 0.001), width, width)
    bbox = BoundingBox()
    for face in trace.faces():
        bbox.extend(face)
    assert bbox.extmin.x > -100


if __name__ == "__main__":
    pytest.main([__file__])

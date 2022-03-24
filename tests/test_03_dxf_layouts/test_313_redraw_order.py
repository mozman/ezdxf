# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf


def test_set_redraw_order():
    doc = ezdxf.new()
    msp = doc.modelspace()
    p1 = msp.add_point((0, 0))
    p2 = msp.add_point((0, 0))
    p3 = msp.add_point((0, 0))
    msp.set_redraw_order([
        (p1.dxf.handle, "F"),
        (p2.dxf.handle, "E"),
        (p3.dxf.handle, "D"),
    ])

    result = list(msp.get_redraw_order())
    assert result[0] == (p1.dxf.handle, "F")
    assert result[1] == (p2.dxf.handle, "E")
    assert result[2] == (p3.dxf.handle, "D")


if __name__ == "__main__":
    pytest.main([__file__])

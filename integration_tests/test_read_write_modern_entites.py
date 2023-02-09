# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import pytest
import os
import ezdxf
from ezdxf.lldxf.const import LATEST_DXF_VERSION


def test_lwpolyline(tmpdir):
    dwg = ezdxf.new(LATEST_DXF_VERSION)
    msp = dwg.modelspace()
    # point format = (x, y, [start_width, [end_width, [bulge]]])
    points = [
        (0, 0, 0, 0.05),
        (3, 0, 0.1, 0.2, -0.5),
        (6, 0, 0.1, 0.05),
        (9, 0),
    ]

    msp.add_lwpolyline(points)
    filename = str(tmpdir.join("lwpolyline.dxf"))
    try:
        dwg.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail(
            "DXFError: {0} for DXF version {1}".format(str(e), dwg.dxfversion)
        )
    assert os.path.exists(filename)

    del dwg
    dwg = ezdxf.readfile(filename)
    msp = dwg.modelspace()
    lwpolyline = msp.query("LWPOLYLINE")[0]
    assert len(lwpolyline) == 4

    pts = lwpolyline.get_points()
    assert pts[0] == (0, 0, 0, 0.05, 0)
    assert pts[1] == (3, 0, 0.1, 0.2, -0.5)
    assert pts[2] == (6, 0, 0.1, 0.05, 0)
    assert pts[3] == (9, 0, 0, 0, 0)

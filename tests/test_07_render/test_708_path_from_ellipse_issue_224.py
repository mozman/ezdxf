#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import pytest
from ezdxf.layouts import VirtualLayout
from ezdxf.render import make_path


@pytest.fixture
def ellipse():
    layout = VirtualLayout()
    return layout.add_ellipse(
        center=(1999.488177113287, -1598.02265357955, 0.0),
        major_axis=(629.968069297, 0.0, 0.0),
        ratio=0.495263197,
        start_param=-1.261396328799999,
        end_param=-0.2505454928,
        dxfattribs={
            'layer': "0",
            'linetype': "Continuous",
            'color': 3,
            'extrusion': (0.0, 0.0, -1.0),
        },
    )


def test_end_points(ellipse):
    p = make_path(ellipse)

    assert ellipse.start_point.isclose(p.start)
    assert ellipse.end_point.isclose(p.end)

    # end point locations measured in BricsCAD:
    assert ellipse.start_point.isclose((2191.3054,  -1300.8375), abs_tol=1e-4)
    assert ellipse.end_point.isclose((2609.7870, -1520.6677), abs_tol=1e-4)

#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.document import Drawing
from ezdxf.math import Vec2, arc_angle_span_deg
from ezdxf.render.dim_curved import detect_closer_defpoint


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new(setup=True)


class TestDetectCloserDefpoints:
    @pytest.mark.parametrize(
        "d, offset",  # d=direction
        [
            (Vec2(1, 0), Vec2(0, 0)),  # +x direction
            (Vec2(0, 1), Vec2(1, -1)),  # +y direction
            (Vec2(-1, 0), Vec2(-2, 3)),  # -x direction
            (Vec2(0, -1), Vec2(2, -4)),  # -y direction
            (Vec2(2, -1), Vec2(20, 45)),  # angled
        ],
        ids=["(+x)", "(+y)", "(-x)", "(-y)", "angled"],
    )
    @pytest.mark.parametrize(
        "base",
        [
            0,
            0.5,
            1.0,
            1.5,
            2.0,  # equal -> p1
            -0.5,  # every base left of p1 is closer to p1
            -1.0,
            -100.0,
        ],
    )
    def test_p1_is_closer_to_base(self, base, d, offset):
        # e.g. for base=(-1, 0), d=(1, 0):
        #              base      p1        p2
        # (-x) <---2---(1)---0---(1)---2---(3)---> (+x)
        # By equality p1 if preferred over p2!
        # Shift system by an arbitrary offset!
        p1 = d * 1 + offset
        p2 = d * 3 + offset
        base = d * base + offset
        assert detect_closer_defpoint(d, base, p1, p2) is p1

    @pytest.mark.parametrize(
        "d, offset",  # d=direction
        [
            (Vec2(1, 0), Vec2(0, -1)),  # +x direction
            (Vec2(0, 1), Vec2(2, -2)),  # +y direction
            (Vec2(-1, 0), Vec2(2, 5)),  # -x direction
            (Vec2(0, -1), Vec2(1, 0)),  # -y direction
            (Vec2(2, -1), Vec2(20, 45)),  # angled
        ],
        ids=["(+x)", "(+y)", "(-x)", "(-y)", "angled"],
    )
    @pytest.mark.parametrize(
        "base",
        [
            2.5,
            3.0,
            4.0,  # every base right of p2 is closer to p2
            100.0,
        ],
    )
    def test_p2_is_closer_to_base(self, base, d, offset):
        # e.g. for base=(4.0, 0), d=(1, 0):
        #                      p1        p2    base
        # (-x) <---2---1---0---(1)---2---(3)---(4)---> (+x)
        # By equality p1 if preferred over p2!
        # Shift system by an arbitrary offset!
        p1 = d * 1 + offset
        p2 = d * 3 + offset
        base = d * base + offset
        assert detect_closer_defpoint(d, base, p1, p2) is p2


@pytest.mark.parametrize(
    "s,e",
    [
        [60, 120],
        [300, 240],  # passes 0
        [240, 300],
        [300, 30],  # passes 0
    ]
)
def test_dimension_line_divided_by_measurement_text(doc: Drawing, s, e):
    """Vertical centered measurement text should hide the part of the
    dimension line beneath the text. This creates two arcs instead of one.
    """
    msp = doc.modelspace()
    dim = msp.add_angular_dim_cra(
        center=Vec2(),
        radius=5,
        start_angle=s,
        end_angle=e,
        distance=2,
        override={"dimtad": 0},  # vertical centered text
    )
    dim.render()
    arcs = dim.dimension.get_geometry_block().query("ARC")
    assert len(arcs) == 2
    assert sum(
        arc_angle_span_deg(arc.dxf.start_angle, arc.dxf.end_angle)
        for arc in arcs
    ) < arc_angle_span_deg(
        s, e
    ), "sum of visual arcs should be smaller than the full arc"


if __name__ == "__main__":
    pytest.main([__file__])

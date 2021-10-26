#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec2
from ezdxf.render.dim_curved import detect_closer_defpoint


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


if __name__ == "__main__":
    pytest.main([__file__])

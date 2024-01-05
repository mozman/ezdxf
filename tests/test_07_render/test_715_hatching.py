#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pytest
from ezdxf.math import Vec2, Bezier4P
from ezdxf.render import hatching, forms
from ezdxf import path


class TestHatchBaseLine:
    def test_positive_line_distance(self):
        line = hatching.HatchBaseLine(
            origin=Vec2((1, 2)), direction=Vec2(2, 0), offset=Vec2(2, 2)
        )
        assert line.normal_distance == pytest.approx(2.0)

    def test_negative_line_distance(self):
        line = hatching.HatchBaseLine(
            origin=Vec2((1, 2)), direction=Vec2(2, 0), offset=Vec2(2, -2)
        )
        assert line.normal_distance == pytest.approx(-2.0)

    def test_hatch_line_direction_error(self):
        with pytest.raises(hatching.HatchLineDirectionError):
            hatching.HatchBaseLine(Vec2(), direction=Vec2(), offset=Vec2(1, 0))

    def test_dense_hatching_error(self):
        with pytest.raises(hatching.DenseHatchingLinesError):
            hatching.HatchBaseLine(
                Vec2(), direction=Vec2(1, 0), offset=Vec2(1, 0)
            )
        with pytest.raises(hatching.DenseHatchingLinesError):
            hatching.HatchBaseLine(
                Vec2(), direction=Vec2(1, 0), offset=Vec2(-1, 0)
            )

    def test_no_offset_error(self):
        with pytest.raises(hatching.DenseHatchingLinesError):
            hatching.HatchBaseLine(
                Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 0)
            )

    def test_very_small_offset_error(self):
        with pytest.raises(hatching.DenseHatchingLinesError):
            hatching.HatchBaseLine(
                Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1e-6)
            )


class TestIntersectHatchLine:
    @pytest.fixture
    def horizontal_baseline(self):
        return hatching.HatchBaseLine(
            Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1)
        )

    def test_intersect_line_collinear(self, horizontal_baseline):
        a = Vec2(3, 0)
        b = Vec2(10, 0)
        distance = 0
        hatch_line = horizontal_baseline.hatch_line(distance)
        ip = hatch_line.intersect_line(a, b, distance, distance)
        assert ip.type == hatching.IntersectionType.COLLINEAR
        assert ip.p0 is a
        assert ip.p1 is b

    def test_intersect_line_start(self, horizontal_baseline):
        a = Vec2(0, 0)
        b = Vec2(0, 10)
        hatch_line = horizontal_baseline.hatch_line(0)
        ip = hatch_line.intersect_line(a, b, 0, 10)
        assert ip.type == hatching.IntersectionType.START
        assert ip.p0 is a

    def test_intersect_line_end(self, horizontal_baseline):
        a = Vec2(0, 0)
        b = Vec2(0, 10)

        hatch_line = horizontal_baseline.hatch_line(10)
        ip = hatch_line.intersect_line(a, b, 0, 10)
        assert ip.type == hatching.IntersectionType.END
        assert ip.p0 is b

    @pytest.mark.parametrize("d", [-2, 0, 6])
    def test_intersect_line_regular(self, horizontal_baseline, d):
        a = Vec2(4, -3)
        b = Vec2(4, 7)
        dist_a = horizontal_baseline.signed_distance(a)
        dist_b = horizontal_baseline.signed_distance(b)

        hatch_line = horizontal_baseline.hatch_line(d)
        ip = hatch_line.intersect_line(a, b, dist_a, dist_b)
        assert ip.type == hatching.IntersectionType.REGULAR
        assert ip.p0.isclose((4, d))

    def test_cubic_bezier_curve(self, horizontal_baseline):
        # low level intersection tests:
        # test_630b - TestRayCubicBezierCurve2dIntersection()
        curve = Bezier4P(Vec2.list([(0, -2), (2, 6), (4, -6), (6, 2)]))
        hatch_line = horizontal_baseline.hatch_line(0)
        ips = hatch_line.intersect_cubic_bezier_curve(curve)
        assert len(ips) == 3
        assert ips[0].p0.isclose((0.6762099922755492, 0.0))
        assert ips[1].p0.isclose((3.0, 0.0))
        assert ips[2].p0.isclose((5.323790007724451, 0.0))

    def test_missing_line_in_gear_example(self):
        baseline = hatching.HatchBaseLine(
            Vec2(), direction=Vec2(1, 1), offset=Vec2(-1, 1)
        )
        polygon = [
            Vec2(-5.099019513592784, 6.164414002968977),
            Vec2(-6.892024376045109, 7.245688373094721),
            Vec2(-7.245688373094716, 6.892024376045114),
            Vec2(-6.164414002968974, 5.099019513592788),
        ]
        lines = list(hatching.hatch_polygons(baseline, [polygon]))
        assert len(lines) == 2


DATA = [
    ("10 l 10 l 10", 10),
    ("2 l 2 r 2 r 2 l 6 " "l 10 l 2 l 2 r 2 r 2 l 6", 14),
    (
        "2 l 2 r 2 l 2 r 2 r 4 l 4 l 10 l 2 l 2 r 2 l 2 r 2 r 4 l 4",
        18,
    ),
    (
        "2 r 2 l 2 r 2 l 2 l 4 r 4 l 10 l 2 r 2 l 2 r 2 l 2 l 4 r 4",
        18,
    ),
    (
        "2 l 2 r 2 r 2 l 2 l 4 r 2 r 4 l 2 l 10 l 2 r 2 l 2 l 2 r 2 r 4 l 2 l 4 r 2",
        22,
    ),
    ("3 @2,2 @2,-2 3 l 10 l @-2,-2 @-2,2 2 @-2,-2 @-2,2", 14),
    (
        "3 @1,1 @1,1 @1,-1 @1,-1 3 l 10 l @-1,-1 @-1,-1 @-1,1 @-1,1 2 @-1,-1 @-1,-1 @-1,1 @-1,1",
        14,
    ),
]


@pytest.mark.parametrize("d,count", DATA)
def test_hatch_polygons(d: str, count):
    """Visual check by the function collinear_hatching() in script
    exploration/hatching.py,

    """
    baseline = hatching.HatchBaseLine(
        Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1)
    )
    lines = list(hatching.hatch_polygons(baseline, [list(forms.turtle(d))]))
    assert len(lines) == count


@pytest.mark.parametrize("d,count", DATA)
def test_hatch_paths(d: str, count):
    """Visual check by the function collinear_hatching() in script
    exploration/hatching.py,

    """
    baseline = hatching.HatchBaseLine(
        Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1)
    )
    lines = list(
        hatching.hatch_paths(
            baseline, [path.from_vertices(forms.turtle(d), close=True)]
        )
    )
    assert len(lines) == count


def test_hatch_curved_path():
    """Visual check by the function collinear_hatching() in script
    exploration/hatching.py,

    """
    p = path.Path((0, 0))
    p.line_to((10, 0))
    p.curve3_to((10, 10), (14, 5))
    p.line_to((0, 10))
    baseline = hatching.HatchBaseLine(
        Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1)
    )
    lines = list(hatching.hatch_paths(baseline, [p]))
    assert len(lines) == 10


def test_hatch_path_with_hole():
    baseline = hatching.HatchBaseLine(
        Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1)
    )
    polygons = [
        list(forms.square(10)),
        list(forms.translate(forms.square(6), (2, 2))),
    ]
    ctrL_lines = list(hatching.hatch_polygons(baseline, polygons))

    p = path.Path((0, 0))
    p.line_to((10, 0))
    p.curve3_to((10, 10), (14, 5))
    p.line_to((0, 10))
    p.close_sub_path()
    p.move_to((2, 2))
    p.line_to((8, 2))
    p.line_to((8, 8))
    p.line_to((2, 8))

    lines = list(hatching.hatch_paths(baseline, [p]))
    assert len(lines) == len(ctrL_lines)


def test_vertical_hatching_with_hole():
    """Visual check by the 1st example for 90 deg in function hole_examples()
    in script exploration/hatching.py,

    """
    size = 10
    angle = 90

    polygons = [
        list(forms.square(size)),
        list(forms.translate(forms.square(size - 2), (1, 1))),
        list(forms.translate(forms.square(3), (2, 2))),
        list(forms.translate(forms.square(3), (4, 3))),
    ]
    direction = Vec2.from_deg_angle(angle)
    offset = direction.orthogonal() * 0.1
    baseline = hatching.HatchBaseLine(
        Vec2(0, 0), direction=direction, offset=offset
    )
    lines = list(hatching.hatch_polygons(baseline, polygons))
    assert len(lines) == 241


class TestLinePatternRendering:
    @pytest.fixture
    def baseline(self):
        return hatching.HatchBaseLine(
            Vec2(),
            direction=Vec2(1, 0),
            offset=Vec2(0, 1),
            line_pattern=[1.0, -0.5, 1.5, -1.0],
        )

    def test_pattern_length(self, baseline):
        assert baseline.pattern_renderer(0).pattern_length == 4.0

    def test_render_full_pattern(self, baseline):
        renderer = baseline.pattern_renderer(0)
        lines = list(renderer.render_full_pattern(0))
        dash1, dash2 = lines
        assert dash1[0] == (0, 0)
        assert dash1[1] == (1, 0)
        assert dash2[0] == (1.5, 0)
        assert dash2[1] == (3.0, 0)

    def test_render_start_to_offset(self, baseline):
        renderer = baseline.pattern_renderer(0)
        lines = list(
            renderer.render_offset_to_offset(
                index=0, s_offset=0.0, e_offset=2.0
            )
        )
        dash1, dash2 = lines
        assert dash1[0] == (0, 0)
        assert dash1[1] == (1, 0)
        assert dash2[0] == (1.5, 0)
        assert dash2[1] == (2.0, 0)

    def test_render_offset_to_end(self, baseline):
        renderer = baseline.pattern_renderer(0)
        lines = list(
            renderer.render_offset_to_offset(
                index=0, s_offset=0.5, e_offset=4.0
            )
        )
        dash1, dash2 = lines
        assert dash1[0] == (0.5, 0)
        assert dash1[1] == (1, 0)
        assert dash2[0] == (1.5, 0)
        assert dash2[1] == (3.0, 0)

    def test_render_offset_to_offset(self, baseline):
        renderer = baseline.pattern_renderer(0)
        lines = list(
            renderer.render_offset_to_offset(
                index=0, s_offset=0.5, e_offset=2.0
            )
        )
        dash1, dash2 = lines
        assert dash1[0] == (0.5, 0)
        assert dash1[1] == (1, 0)
        assert dash2[0] == (1.5, 0)
        assert dash2[1] == (2.0, 0)

    def test_hatch_line_full_pattern(self, baseline):
        renderer = baseline.pattern_renderer(0)
        lines = list(renderer.render(Vec2(0, 0), Vec2(12, 0)))
        assert len(lines) == 6, "expected 3 full pattern sequences"
        assert lines[0][0] == (0, 0)
        assert lines[-1][1] == (11, 0)

    def test_hatch_line_with_start_and_end_offset(self, baseline):
        renderer = baseline.pattern_renderer(0)
        lines = list(renderer.render(Vec2(1, 0), Vec2(10, 0)))
        assert len(lines) == 6
        assert lines[0][0] == (1, 0)
        assert lines[-1][1] == (10, 0)


def test_explode_earth1_pattern():
    """Visual check by the function explode_hatch_pattern() in script
    exploration/hatching.py,

    """
    from ezdxf.entities import Hatch

    hatch = Hatch.new()
    hatch.set_pattern_definition(
        [
            [0.0, (0.0, 0.0), (1.5875, 1.5875), [1.5875, -1.5875]],
            [0.0, (0.0, 0.5953125), (1.5875, 1.5875), [1.5875, -1.5875]],
            [0.0, (0.0, 1.190625), (1.5875, 1.5875), [1.5875, -1.5875]],
            [
                90.0,
                (0.1984375, 1.3890625),
                (-1.5875, 1.5875),
                [1.5875, -1.5875],
            ],
            [90.0, (0.79375, 1.3890625), (-1.5875, 1.5875), [1.5875, -1.5875]],
            [
                90.0,
                (1.3890625, 1.3890625),
                (-1.5875, 1.5875),
                [1.5875, -1.5875],
            ],
        ]
    )
    hatch.dxf.solid_fill = 0
    # 1. polyline path
    hatch.paths.add_polyline_path(
        [
            (0.0, 223.0, 0.0),
            (10.0, 223.0, 0.0),
            (10.0, 233.0, 0.0),
            (0.0, 233.0, 0.0),
        ],
        is_closed=1,
        flags=3,
    )
    # jiggle_origin=True has random behavior, which is not good for a test!
    lines = list(hatching.hatch_entity(hatch, jiggle_origin=False))
    assert len(lines) == 139


if __name__ == "__main__":
    pytest.main([__file__])

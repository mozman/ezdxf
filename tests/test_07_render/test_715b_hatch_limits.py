import pytest


from ezdxf.math import Vec2


from ezdxf.render import hatching


from ezdxf import path


class TestHatchingLimits:

    def test_huge_distance_range_stops_at_work_budget(self, baseline):
        polygon = Vec2.list([(0, 0), (1, 0), (1, 1e12)])
        control = hatching.HatchingControl(max_work=128)
        with pytest.raises(hatching.HatchingLimitError, match="work"):
            list(hatching.hatch_polygons(baseline, [polygon], control=control))
        assert control.work == 128

    @pytest.fixture
    def baseline(self):
        return hatching.HatchBaseLine(Vec2(), Vec2(1, 0), Vec2(0, 1))

    @pytest.mark.parametrize("as_path", [False, True])
    def test_cancel_inside_single_boundary(self, baseline, as_path, monkeypatch):
        polygon = Vec2.list([(0, 0), (1, 0), (1, 10000), (0, 10000)])
        intersections = 0
        original = hatching.HatchLine.intersect_line

        def intersect(*args):
            nonlocal intersections
            intersections += 1
            return original(*args)

        monkeypatch.setattr(hatching.HatchLine, "intersect_line", intersect)
        if as_path:
            generate = hatching.hatch_paths
            geometries = [path.from_vertices(polygon, close=True)]
        else:
            generate = hatching.hatch_polygons
            geometries = [polygon]
        assert list(generate(baseline, geometries, lambda: intersections >= 100)) == []
        assert 100 <= intersections < 164

    def test_cancel_before_first_work_item(self, baseline):
        polygon = Vec2.list([(0, 0), (1, 0), (1, 10)])
        control = hatching.HatchingControl(lambda: True)
        assert list(hatching.hatch_polygons(baseline, [polygon], control=control)) == []
        assert control.work == 0

    def test_huge_distance_range_uses_bounded_memory(self, baseline):
        tracemalloc = pytest.importorskip("tracemalloc", exc_type=ImportError)

        polygon = Vec2.list([(0, 0), (1, 0), (1, 1e12)])
        control = hatching.HatchingControl(max_work=128)
        tracemalloc.start()
        try:
            with pytest.raises(hatching.HatchingLimitError, match="work"):
                list(hatching.hatch_polygons(baseline, [polygon], control=control))
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        assert control.work == 128
        assert peak < 1_000_000

    def test_many_empty_boundaries_cancel(self, baseline):
        calls = 0

        def terminate():
            nonlocal calls
            calls += 1
            return calls == 3

        assert list(hatching.hatch_polygons(baseline, [[]] * 10000, terminate)) == []
        assert calls == 3

    def test_empty_boundaries_consume_work_budget(self, baseline):
        control = hatching.HatchingControl(max_work=5)
        with pytest.raises(hatching.HatchingLimitError):
            list(hatching.hatch_polygons(baseline, [[]] * 100, control=control))
        assert control.work == 5

    def test_degenerate_path_commands_are_counted(self, baseline):
        p = path.Path()
        for _ in range(1000):
            p.line_to((0, 0))
        control = hatching.HatchingControl(max_work=10)
        with pytest.raises(hatching.HatchingLimitError):
            list(hatching.hatch_paths(baseline, [p], control=control))
        assert control.work == 10

    def test_path_commands_are_materialized_only_as_needed(self, baseline):
        class TrackingPath(path.Path):
            materialized = 0

            def __getitem__(self, index):
                self.materialized += 1
                return super().__getitem__(index)

        p = TrackingPath()
        for _ in range(1000):
            p.line_to((0, 0))
        control = hatching.HatchingControl(max_work=10)
        with pytest.raises(hatching.HatchingLimitError):
            list(hatching.hatch_paths(baseline, [p], control=control))
        assert p.materialized <= 10

    def test_segment_budget_on_long_tiny_dash_pattern(self, baseline):
        renderer = hatching.PatternRenderer(baseline.hatch_line(0), [1e-6, -1e-6])
        control = hatching.HatchingControl(max_segments=5)
        output = []
        with pytest.raises(hatching.HatchingLimitError, match="segment"):
            for segment in renderer.render(Vec2(), Vec2(1e12, 0), control=control):
                output.append(segment)
        assert len(output) == 5

    def test_gap_only_pattern_has_work_budget(self, baseline):
        renderer = hatching.PatternRenderer(baseline.hatch_line(0), [-1e-6])
        control = hatching.HatchingControl(max_work=127)
        with pytest.raises(hatching.HatchingLimitError, match="work"):
            list(renderer.render(Vec2(), Vec2(1e12, 0), control=control))
        assert control.work == 127

    def test_cancel_inside_gap_only_pattern(self, baseline):
        renderer = hatching.PatternRenderer(baseline.hatch_line(0), [-1e-6])
        control = hatching.HatchingControl()
        control.terminate = lambda: control.work >= 100
        assert list(renderer.render(Vec2(), Vec2(1e12, 0), control=control)) == []
        assert 100 <= control.work < 164
        assert control.cancelled

    def test_shared_limits_across_pattern_lines(self, baseline):
        renderer = hatching.PatternRenderer(baseline.hatch_line(0), [])
        control = hatching.HatchingControl(max_segments=1)
        assert len(list(renderer.render(Vec2(), Vec2(1, 0), control=control))) == 1
        with pytest.raises(hatching.HatchingLimitError):
            list(renderer.render(Vec2(), Vec2(1, 0), control=control))

    def test_public_distances_still_return_list(self):
        assert hatching.hatch_line_distances([0, 3], 1) == [0, 1, 2]

    def test_limits_preserve_normal_output(self, baseline):
        polygon = Vec2.list([(0, 0), (10, 0), (10, 10), (0, 10)])
        expected = list(hatching.hatch_polygons(baseline, [polygon]))
        control = hatching.HatchingControl(max_work=None, max_segments=None)
        assert (
            list(hatching.hatch_polygons(baseline, [polygon], control=control))
            == expected
        )


@pytest.fixture
def elevated_hatch():
    from ezdxf.entities import Hatch

    hatch = Hatch.new(dxfattribs={"elevation": (0, 0, 3)})
    hatch.paths.add_polyline_path([(0, 0), (4, 0), (4, 4), (0, 4)])
    hatch.set_pattern_fill("TEST", definition=[[0, (0, 0.5), (0, 1), []]])
    return hatch


@pytest.mark.parametrize("extrusion", [(0, 0, 1)])
def test_hatch_entity_segment_budget_matches_output(elevated_hatch, extrusion):
    elevated_hatch.dxf.extrusion = extrusion
    control = hatching.HatchingControl(max_segments=1)
    lines = hatching.hatch_entity(elevated_hatch, jiggle_origin=False, control=control)
    next(lines)
    with pytest.raises(hatching.HatchingLimitError, match="segment"):
        next(lines)
    assert control.segments == 1

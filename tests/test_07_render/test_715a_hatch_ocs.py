import pytest


from ezdxf.render import hatching


@pytest.fixture
def elevated_hatch():
    from ezdxf.entities import Hatch

    hatch = Hatch.new(dxfattribs={"elevation": (0, 0, 3)})
    hatch.paths.add_polyline_path([(0, 0), (4, 0), (4, 4), (0, 4)])
    hatch.set_pattern_fill("TEST", definition=[[0, (0, 0.5), (0, 1), []]])
    return hatch


def test_hatch_entity_emits_each_transformed_segment_once(elevated_hatch):
    elevated_hatch.dxf.extrusion = (0, 1, 0)
    lines = list(hatching.hatch_entity(elevated_hatch, jiggle_origin=False))
    assert len(lines) == 4
    for index, (start, end) in enumerate(lines):
        assert start.isclose((0, 3, index + 0.5))
        assert end.isclose((-4, 3, index + 0.5))


def test_hatch_entity_preserves_elevation_without_ocs_transform(elevated_hatch):
    lines = list(hatching.hatch_entity(elevated_hatch, jiggle_origin=False))
    assert len(lines) == 4
    for index, (start, end) in enumerate(lines):
        assert start.isclose((0, index + 0.5, 3))
        assert end.isclose((4, index + 0.5, 3))

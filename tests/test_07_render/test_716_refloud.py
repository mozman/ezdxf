# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.render import revcloud


def test_create_revcloud():
    points = [(0, 0), (1, 0), (1, 1), (0, 1)]
    lw_points = revcloud.points(points, segment_length=0.1, bulge=0.5)
    assert len(lw_points) == 44


@pytest.mark.parametrize(
    "points", [[], [(0, 0)], [(0, 0), (0, 0)], [(0, 0), (1, 0), (0, 0)]]
)
def test_too_few_points_raises_exception(points):
    with pytest.raises(ValueError):
        revcloud.points(points, segment_length=0.1)


def test_too_small_segment_length_raises_exception():
    with pytest.raises(ValueError):
        revcloud.points( [(0, 0), (1, 0), (1, 1), (0, 1)], segment_length=0)

if __name__ == "__main__":
    pytest.main([__file__])

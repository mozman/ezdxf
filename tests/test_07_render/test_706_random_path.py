# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest
from ezdxf.render import random_2d_path, random_3d_path


def test_random_2d_path():
    points = list(random_2d_path(steps=100))
    assert len(points) == 100
    assert len(set(points)) > 97


def test_random_3d_path():
    points = list(random_3d_path(steps=100))
    assert len(points) == 100
    assert len(set(points)) > 97


if __name__ == "__main__":
    pytest.main([__file__])

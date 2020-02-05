# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import Vector, is_planar_face

REGULAR_FACE = Vector.list([(0, 0, 0), (1, 0, 1), (1, 1, 1), (0, 1, 0)])
IRREGULAR_FACE = Vector.list([(0, 0, 0), (1, 0, 1), (1, 1, 0), (0, 1, 0)])
REGULAR_FACE_WRONG_ORDER = Vector.list([(0, 0, 0), (1, 1, 1), (1, 0, 1), (0, 1, 0)])


def test_face_count():
    assert is_planar_face(REGULAR_FACE[:3]) is True
    assert is_planar_face(REGULAR_FACE[:2]) is False


def test_regular_face():
    assert is_planar_face(REGULAR_FACE) is True


def test_irregular_face():
    assert is_planar_face(IRREGULAR_FACE) is False


def test_does_not_detect_wrong_order():
    assert is_planar_face(REGULAR_FACE_WRONG_ORDER) is True


if __name__ == '__main__':
    pytest.main([__file__])

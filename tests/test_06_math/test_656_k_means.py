#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec3, k_means


def test_random_points():
    points = [Vec3.random(100) for _ in range(100)]
    clusters = k_means(points, 5, max_iter=5)
    assert len(clusters) == 5
    assert sum(map(len, clusters)) == 100


if __name__ == '__main__':
    pytest.main([__file__])

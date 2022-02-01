#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec3, k_means

POINTS = [Vec3.random(100) for _ in range(100)]


@pytest.mark.parametrize("k", [4, 5, 6])
def test_cluster_random_points(k):
    clusters = k_means(POINTS, k, max_iter=5)
    assert len(clusters) == k
    assert sum(map(len, clusters)) == 100


if __name__ == "__main__":
    pytest.main([__file__])

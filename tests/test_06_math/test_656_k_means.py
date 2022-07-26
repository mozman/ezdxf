#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec3
from ezdxf.math.clustering import k_means, average_cluster_radius, average_intra_cluster_distance

POINTS = [Vec3.random(100) for _ in range(100)]


@pytest.mark.parametrize("k", [4, 5, 6])
def test_cluster_random_points(k):
    clusters = k_means(POINTS, k, max_iter=5)
    assert len(clusters) == k
    assert sum(map(len, clusters)) == 100


def test_measure_average_cluster_radius():
    clusters = k_means(POINTS, 5, max_iter=5)
    assert average_cluster_radius(clusters) > 10.0


def test_measure_average_intra_cluster_distance():
    clusters = k_means(POINTS, 5, max_iter=5)
    assert average_intra_cluster_distance(clusters) > 10.0


if __name__ == "__main__":
    pytest.main([__file__])

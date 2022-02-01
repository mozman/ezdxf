#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import dbscan
from ezdxf.render import forms


def make_cluster(size, dx, dy, dz):
    return forms.cube().scale_uniform(size).translate(dx, dy, dz).vertices


def test_two_simple_cluster():
    c1 = make_cluster(1, 0, 0, 0)
    c2 = make_cluster(1.5, 5, 0, 0)
    points = list(c1)
    points.extend(c2)
    cluster = dbscan(points, radius=2)
    assert len(cluster) == 2
    cluster.sort()
    assert set(cluster[0]) == set(c1)
    assert set(cluster[1]) == set(c2)


def test_cluster_noise():
    cluster = dbscan(make_cluster(10, 0, 0, 0), radius=2)
    assert len(cluster) == 8  # all noise


if __name__ == "__main__":
    pytest.main([__file__])

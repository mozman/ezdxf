# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from ezdxf.math.perlin import snoise2, snoise3


def test_simplex_2d_range():
    for i in range(-100, 100, 10):
        x = i * 0.49
        y = -i * 0.67
        n = snoise2(x, y)
        assert -1.0 <= n <= 1.0, (x, y, n)


def test_simplex_2d_octaves_range():
    for i in range(-100, 100, 10):
        for o in range(10):
            x = -i * 0.49
            y = i * 0.67
            n = snoise2(x, y)
            assert -1.0 <= n <= 1.0, (x, n)


def test_simplex_3d_range():
    for i in range(-100, 100, 10):
        x = i * 0.31
        y = -i * 0.7
        z = i * 0.19
        n = snoise3(x, y, z)
        assert -1.0 <= n <= 1.0, (x, y, z, n)


def test_simplex_3d_octaves_range():
    for i in range(-100, 100, 10):
        x = -i * 0.12
        y = i * 0.55
        z = i * 0.34
        for o in range(10):
            n = snoise3(x, y, z)
            assert -1.0 <= n <= 1.0, (x, y, z, o+1, n)



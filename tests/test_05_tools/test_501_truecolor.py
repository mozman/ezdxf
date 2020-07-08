# Created: 2014-05-09
# License: MIT License
import pytest
from ezdxf.tools.rgb import int2rgb, rgb2int, aci2rgb, luminance


def test_rgb():
    r, g, b = int2rgb(0xA0B0C0)
    assert 0xA0 == r
    assert 0xB0 == g
    assert 0xC0 == b


def test_from_rgb():
    assert 0xA0B0C0 == rgb2int((0xA0, 0xB0, 0xC0))


def test_from_aci():
    assert (255, 0, 0) == aci2rgb(1)
    assert (255, 255, 255) == aci2rgb(7)


def test_0():
    with pytest.raises(IndexError):
        aci2rgb(0)


def test_256():
    with pytest.raises(IndexError):
        aci2rgb(256)


def test_luminance():
    black = luminance((0, 0, 0))
    blue = luminance((0, 0, 255))
    red = luminance((255, 0, 0))
    green = luminance((0, 255, 0))
    yellow = luminance((255, 255, 0))
    cyan = luminance((0, 255, 255))
    magenta = luminance((255, 0, 255))
    white = luminance((255, 255, 255))

    assert black == 0.0
    assert white == 1.0
    assert black < blue < red < magenta < green < cyan < yellow < white

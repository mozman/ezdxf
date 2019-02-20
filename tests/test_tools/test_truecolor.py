# Created: 2014-05-09
# License: MIT License
from __future__ import unicode_literals
import pytest
from ezdxf.tools.rgb import int2rgb, rgb2int, aci2rgb


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

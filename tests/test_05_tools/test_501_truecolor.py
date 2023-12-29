# Copyright (c) 2014-2023, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.colors import int2rgb, rgb2int, aci2rgb, luminance, RGB, RGBA


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


class TestRGB:
    def test_from_hex_(self):
        assert RGB.from_hex("#aabbcc") == (0xAA, 0xBB, 0xCC)

    def test_from_hex_with_alpha(self):
        assert RGB.from_hex("#aabbccdd") == (0xAA, 0xBB, 0xCC)

    def test_from_floats(self):
        assert RGB.from_floats((1, 0.5, 0)) == (255, 128, 0)

    def test_to_floats(self):
        assert RGB(255, 128, 0).to_floats() == (1.0, 0.5019607843137255, 0.0)

    def test_to_hex(self):
        assert RGB.from_hex("#aabbcc").to_hex() == "#aabbcc"

    def test_luminance(self):
        rgb = RGB.from_hex("#aabbcc")
        assert rgb.luminance == luminance(rgb)


class TestRGBA:
    def test_from_hex(self):
        assert RGBA.from_hex("#aabbccdd") == (0xAA, 0xBB, 0xCC, 0xDD)

    def test_to_hex(self):
        assert RGBA.from_hex("#aabbccdd").to_hex() == "#aabbccdd"

    def test_from_floats(self):
        assert RGBA.from_floats((1, 0.5, 0, 0)) == (255, 128, 0, 0)
        assert RGBA.from_floats((1, 0.5, 0, 1)) == (255, 128, 0, 255)

    def test_to_floats(self):
        assert RGBA(255, 128, 0, 255).to_floats() == (1.0, 0.5019607843137255, 0.0, 1.0)

    def test_luminance(self):
        rgba = RGBA.from_hex("#aabbcc")
        assert rgba.luminance == luminance(rgba)

    def test_default_alpha_channel_is_opaque(self):
        assert RGBA(0xAA, 0xBB, 0xCC) == (0xAA, 0xBB, 0xCC, 0xFF)
        assert RGBA.from_hex("#aabbcc") == (0xAA, 0xBB, 0xCC, 0xFF)
        assert RGBA.from_floats((1, 0.5, 0)) == (255, 128, 0, 255)


if __name__ == "__main__":
    pytest.main([__file__])

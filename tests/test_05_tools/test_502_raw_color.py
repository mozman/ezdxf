# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

from ezdxf.lldxf.const import BYBLOCK, BYLAYER
from ezdxf.tools import rgb
from ezdxf.tools.rgb import decode_raw_color, encode_raw_color


def test_decode_by_block():
    assert decode_raw_color(-1056964608) == (rgb.COLOR_BY_BLOCK, BYBLOCK)


def test_encode_by_block():
    assert encode_raw_color(BYBLOCK) == -1056964608


def test_decode_by_layer():
    assert decode_raw_color(-1073741824) == (rgb.COLOR_BY_LAYER, BYLAYER)


def test_encode_by_layer():
    assert encode_raw_color(BYLAYER) == -1073741824


def test_decode_aci():
    assert decode_raw_color(-1023410164) == (rgb.COLOR_ACI, 12)


def test_encode_aci():
    assert encode_raw_color(12) == -1023410164


def test_decode_rgb():
    assert decode_raw_color(-1039526882) == (rgb.COLOR_RGB, (10, 20, 30))


def test_encode_rgb():
    assert encode_raw_color((10, 20, 30)) == -1039526882

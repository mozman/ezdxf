# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

from ezdxf.lldxf.const import BYBLOCK, BYLAYER
from ezdxf import colors as clr


def test_decode_by_block():
    assert clr.decode_raw_color(-1056964608) == (clr.COLOR_TYPE_BY_BLOCK, BYBLOCK)


def test_encode_by_block():
    assert clr.encode_raw_color(BYBLOCK) == -1056964608


def test_decode_by_layer():
    assert clr.decode_raw_color(-1073741824) == (clr.COLOR_TYPE_BY_LAYER, BYLAYER)


def test_encode_by_layer():
    assert clr.encode_raw_color(BYLAYER) == -1073741824


def test_decode_aci():
    assert clr.decode_raw_color(-1023410164) == (clr.COLOR_TYPE_ACI, 12)


def test_encode_aci():
    assert clr.encode_raw_color(12) == -1023410164


def test_decode_rgb():
    assert clr.decode_raw_color(-1039526882) == (clr.COLOR_TYPE_RGB, (10, 20, 30))


def test_encode_rgb():
    assert clr.encode_raw_color((10, 20, 30)) == -1039526882

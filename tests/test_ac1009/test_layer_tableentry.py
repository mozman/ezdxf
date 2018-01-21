# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.legacy.tableentries import Layer
from ezdxf.lldxf.const import DXFInvalidLayerName


@pytest.fixture
def layer():
    return Layer.new('FFFF')


def test_new_layer(layer):
    assert len(layer.tags.noclass) == 6


def test_get_handle(layer):
    assert 'FFFF' == layer.dxf.handle


def test_get_name(layer):
    assert 'LAYERNAME' == layer.dxf.name


def test_get_flags(layer):
    assert layer.dxf.flags == 0


def test_get_color(layer):
    assert layer.dxf.color == 7


def test_get_linetype(layer):
    assert layer.dxf.linetype == 'CONTINUOUS'


def test_set_name(layer):
    layer.dxf.name = 'MOZMAN'
    assert 'MOZMAN' == layer.dxf.name


def test_set_color(layer):
    layer.dxf.color = '1'
    assert 1 == layer.dxf.color


def test_set_color_2(layer):
    layer.set_color(-1)
    assert 1 == layer.get_color()


def test_set_color_for_off_layer(layer):
    layer.set_color(7)
    layer.off()
    assert 7 == layer.get_color()
    assert -7 == layer.dxf.color


def test_is_locked(layer):
    layer.lock()
    assert layer.is_locked() is True


def test_is_not_locked(layer):
    assert layer.is_locked() is False


def test_is_on(layer):
    assert layer.is_on() is True


def test_is_off(layer):
    layer.dxf.color = -100
    assert layer.is_off() is True


def test_is_frozen(layer):
    assert layer.is_frozen() is False


def test_freeze(layer):
    layer.freeze()
    assert layer.is_frozen() is True
    assert 1 == layer.dxf.flags


def test_thaw(layer):
    layer.dxf.flags = 1
    assert layer.is_frozen() is True
    layer.thaw()
    assert layer.is_frozen() is False
    assert 0 == layer.dxf.flags


def test_invald_layer_name():
    with pytest.raises(DXFInvalidLayerName):
        Layer.new('FFFF', dxfattribs={'name': 'Layer/'})

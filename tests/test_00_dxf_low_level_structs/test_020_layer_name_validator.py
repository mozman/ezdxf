# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from ezdxf.lldxf.validator import is_valid_layer_name


def test_invalid_layer_name():
    assert is_valid_layer_name('Layer Layer') is True
    assert is_valid_layer_name('Layer/') is False
    assert is_valid_layer_name('Layer*') is False
    assert is_valid_layer_name('*Layer') is False
    assert is_valid_layer_name('Layer=') is False
    assert is_valid_layer_name('Layer;') is False
    assert is_valid_layer_name('Layer:') is False
    assert is_valid_layer_name('Layer<') is False
    assert is_valid_layer_name('Layer>') is False
    assert is_valid_layer_name('Layer`') is False
    assert is_valid_layer_name('\\Layer`') is False
    assert is_valid_layer_name('"Layer"') is False


def test_strange_but_valid_layer_name():
    assert is_valid_layer_name('Layer|Layer') is True


def test_is_adsk_special_layer():
    assert is_valid_layer_name('*adsk_xyz') is True
    assert is_valid_layer_name('*ADSK_xyz') is True
    assert is_valid_layer_name('ADSK_xyz*') is False

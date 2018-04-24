# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2000')


def test_generic_layer_filter(dwg):
    layer_filter = dwg.objects.create_new_dxf_entity('LAYER_FILTER', {})
    assert layer_filter.dxftype() == 'LAYER_FILTER'
    assert len(layer_filter.layers) == 0


def test_set_get_layer_filter(dwg):
    layer_filter = dwg.objects.create_new_dxf_entity('LAYER_FILTER', {})
    assert layer_filter.dxftype() == 'LAYER_FILTER'
    layer_filter.layers = ['FF', 'EE', 'DD']
    assert len(layer_filter.layers) == 3
    assert layer_filter.layers == ['FF', 'EE', 'DD']

    layer_filter.layers.append('Layer')
    assert layer_filter.layers[-1] == 'Layer'

    with pytest.raises(ezdxf.DXFValueError):
        layer_filter.layers = 'string not allowed'


def test_magic_methods(dwg):
    layer_filter = dwg.objects.create_new_dxf_entity('LAYER_FILTER', {})
    layer_filter.layers = ['FF', 'EE', 'DD', 'CC']
    assert len(layer_filter.layers) == 4
    assert layer_filter.layers[1] == 'EE'

    layer_filter.layers[1] = 'ABCD'
    assert layer_filter.layers[1] == 'ABCD'

    del layer_filter.layers[1:3]
    assert layer_filter.layers == ['FF', 'CC']

    layer_filter.layers[1:1] = ['EE', 'DD']
    assert layer_filter.layers == ['FF', 'EE', 'DD', 'CC']

    assert layer_filter.layers[1:3] == ['EE', 'DD']

    layer_filter.layers.append('Layer2')
    assert layer_filter.layers[-1] == 'Layer2'

    layer_filter.layers.extend(['L3', 'L4'])
    assert layer_filter.layers[-2:] == ['L3', 'L4']

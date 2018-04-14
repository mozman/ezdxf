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
    assert len(layer_filter) == 0


def test_set_get_layer_filter(dwg):
    layer_filter = dwg.objects.create_new_dxf_entity('LAYER_FILTER', {})
    assert layer_filter.dxftype() == 'LAYER_FILTER'
    layer_filter.set_layer_names(['FF', 'EE', 'DD'])
    assert len(layer_filter) == 3
    assert layer_filter.get_layer_names() == ['FF', 'EE', 'DD']


def test_magic_methods(dwg):
    layer_filter = dwg.objects.create_new_dxf_entity('LAYER_FILTER', {})
    layer_filter.set_layer_names(['FF', 'EE', 'DD', 'CC'])
    assert len(layer_filter) == 4
    assert layer_filter[1] == 'EE'

    layer_filter[1] = 'ABCD'
    assert layer_filter[1] == 'ABCD'

    del layer_filter[1:3]
    assert layer_filter.get_layer_names() == ['FF', 'CC']

    layer_filter[1:1] = ['EE', 'DD']
    assert layer_filter.get_layer_names() == ['FF', 'EE', 'DD', 'CC']

    assert layer_filter[1:3] == ['EE', 'DD']

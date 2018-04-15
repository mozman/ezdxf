# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_generic_field_list(dwg):
    field_list = dwg.objects.create_new_dxf_entity('FIELDLIST', {})
    assert field_list.dxftype() == 'FIELDLIST'
    assert len(field_list) == 0


def test_set_get_field_list(dwg):
    field_list = dwg.objects.create_new_dxf_entity('FIELDLIST', {})
    assert field_list.dxftype() == 'FIELDLIST'
    field_list.set_ids(['FF', 'EE', 'DD'])
    assert len(field_list) == 3
    assert field_list.get_ids() == ['FF', 'EE', 'DD']

    field_list.append('FFFF')
    assert field_list[-1] == 'FFFF'


def test_magic_methods(dwg):
    field_list = dwg.objects.create_new_dxf_entity('FIELDLIST', {})
    field_list.set_ids(['FF', 'EE', 'DD', 'CC'])
    assert len(field_list) == 4
    assert field_list[1] == 'EE'

    field_list[1] = 'ABCD'
    assert field_list[1] == 'ABCD'

    del field_list[1:3]
    assert field_list.get_ids() == ['FF', 'CC']

    field_list[1:1] = ['EE', 'DD']
    assert field_list.get_ids() == ['FF', 'EE', 'DD', 'CC']

    assert field_list[1:3] == ['EE', 'DD']

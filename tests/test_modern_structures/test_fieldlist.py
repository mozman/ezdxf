# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_is_registered():
    from ezdxf.lldxf import loader
    assert loader.is_registered('FIELDLIST', legacy=False)


def test_generic_field_list(dwg):
    field_list = dwg.objects.create_new_dxf_entity('FIELDLIST', {})
    assert field_list.dxftype() == 'FIELDLIST'
    assert len(field_list.handles) == 0


def test_set_get_field_list(dwg):
    field_list = dwg.objects.create_new_dxf_entity('FIELDLIST', {})
    assert field_list.dxftype() == 'FIELDLIST'
    field_list.handles = ['FF', 'EE', 'DD']
    handles = field_list.handles
    assert len(handles) == 3
    assert handles == ['FF', 'EE', 'DD']

    handles.append('FFFF')
    assert handles[-1] == 'FFFF'


def test_magic_methods(dwg):
    field_list = dwg.objects.create_new_dxf_entity('FIELDLIST', {})
    field_list.handles = ['FF', 'EE', 'DD', 'CC']
    handles = field_list.handles
    assert len(handles) == 4
    assert handles[1] == 'EE'

    handles[1] = 'ABCD'
    assert handles[1] == 'ABCD'

    del handles[1:3]
    assert handles[:] == ['FF', 'CC']

    handles[1:1] = ['EE', 'DD']
    assert handles == ['FF', 'EE', 'DD', 'CC']
    assert handles[1:3] == ['EE', 'DD']

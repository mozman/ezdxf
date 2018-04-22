# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_is_registered():
    from ezdxf.lldxf import loader
    assert loader.is_registered('IDBUFFER', legacy=False)


def test_generic_id_buffer(dwg):
    id_buffer = dwg.objects.create_new_dxf_entity('IDBUFFER', {})
    assert id_buffer.dxftype() == 'IDBUFFER'
    assert len(id_buffer.handles) == 0


def test_set_get_id_buffer(dwg):
    id_buffer = dwg.objects.create_new_dxf_entity('IDBUFFER', {})
    assert id_buffer.dxftype() == 'IDBUFFER'
    handles = id_buffer.handles
    handles.set_ids(['FF', 'EE', 'DD'])
    assert len(handles) == 3
    assert handles.get_ids() == ['FF', 'EE', 'DD']

    handles.append('FFFF')
    assert handles[-1] == 'FFFF'

    handles.clear()
    assert len(handles) == 0


def test_magic_methods(dwg):
    id_buffer = dwg.objects.create_new_dxf_entity('IDBUFFER', {})
    handles = id_buffer.handles
    handles.set_ids(['FF', 'EE', 'DD', 'CC'])
    assert len(handles) == 4
    assert handles[1] == 'EE'

    handles[1] = 'ABCD'
    assert handles[1] == 'ABCD'

    del handles[1:3]
    assert handles.get_ids() == ['FF', 'CC']

    handles[1:1] = ['EE', 'DD']
    assert handles.get_ids() == ['FF', 'EE', 'DD', 'CC']

    assert handles[1:3] == ['EE', 'DD']

    handles += 'AAAA'
    assert handles[-1] == 'AAAA'


def test_dxf_tags(dwg):
    id_buffer = dwg.objects.create_new_dxf_entity('IDBUFFER', {})
    id_buffer.handles.set_ids(['FF', 'EE', 'DD', 'CC'])
    tags = list(id_buffer.handles.dxftags())
    assert len(tags) == 4
    assert tags[0] == (330, 'FF')
    assert tags[-1] == (330, 'CC')


def test_clone(dwg):
    id_buffer = dwg.objects.create_new_dxf_entity('IDBUFFER', {})
    id_buffer.handles.set_ids(['FF', 'EE', 'DD', 'CC'])
    handles = id_buffer.handles
    handles2 = handles.clone()
    handles2[-1] = 'ABCD'
    assert handles[:-1] == handles2[:-1]
    assert handles[-1] != handles2[-1]

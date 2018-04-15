# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_generic_id_buffer(dwg):
    id_buffer = dwg.objects.create_new_dxf_entity('IDBUFFER', {})
    assert id_buffer.dxftype() == 'IDBUFFER'
    assert len(id_buffer) == 0


def test_set_get_id_buffer(dwg):
    id_buffer = dwg.objects.create_new_dxf_entity('IDBUFFER', {})
    assert id_buffer.dxftype() == 'IDBUFFER'
    id_buffer.set_ids(['FF', 'EE', 'DD'])
    assert len(id_buffer) == 3
    assert id_buffer.get_ids() == ['FF', 'EE', 'DD']

    id_buffer.append('FFFF')
    assert id_buffer[-1] == 'FFFF'

    id_buffer.clear()
    assert len(id_buffer) == 0


def test_magic_methods(dwg):
    id_buffer = dwg.objects.create_new_dxf_entity('IDBUFFER', {})
    id_buffer.set_ids(['FF', 'EE', 'DD', 'CC'])
    assert len(id_buffer) == 4
    assert id_buffer[1] == 'EE'

    id_buffer[1] = 'ABCD'
    assert id_buffer[1] == 'ABCD'

    del id_buffer[1:3]
    assert id_buffer.get_ids() == ['FF', 'CC']

    id_buffer[1:1] = ['EE', 'DD']
    assert id_buffer.get_ids() == ['FF', 'EE', 'DD', 'CC']

    assert id_buffer[1:3] == ['EE', 'DD']

    id_buffer += 'AAAA'
    assert id_buffer[-1] == 'AAAA'




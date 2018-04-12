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
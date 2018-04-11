# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_generic_data_table(dwg):
    sun = dwg.objects.create_new_dxf_entity('DATATABLE', {})
    assert sun.dxftype() == 'DATATABLE'
    assert sun.dxf.version == 2

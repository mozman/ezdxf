# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_generic_data_table(dwg):
    datatable = dwg.objects.create_new_dxf_entity('DATATABLE', {})
    assert datatable.dxftype() == 'DATATABLE'
    assert datatable.dxf.version == 2

# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_generic_table_style(dwg):
    table_style = dwg.objects.create_new_dxf_entity('TABLESTYLE', {})
    assert table_style.dxftype() == 'TABLESTYLE'
    assert table_style.dxf.version == 0
    assert table_style.dxf.name == 'Standard'

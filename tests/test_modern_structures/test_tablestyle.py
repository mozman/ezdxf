# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_generic_table_style(dwg):
    sun = dwg.objects.create_new_dxf_entity('TABLESTYLE', {})
    assert sun.dxftype() == 'TABLESTYLE'
    assert sun.dxf.version == 0
    assert sun.dxf.name == 'Standard'

# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_visualstyle(dwg):
    vstyle = dwg.objects.create_new_dxf_entity('VISUALSTYLE', dxfattribs={'description': 'Testing', 'style_type': 7})
    assert vstyle.dxftype() == 'VISUALSTYLE'
    assert vstyle.dxf.description == "Testing"
    assert vstyle.dxf.style_type == 7

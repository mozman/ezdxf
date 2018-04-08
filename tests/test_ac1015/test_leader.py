# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def msp():
    dwg = ezdxf.new('R2000')
    return dwg.modelspace()


def test_generic_leader(msp):
    leader = msp.build_and_add_entity('LEADER', {})
    assert leader.dxftype() == 'LEADER'
    assert leader.dxf.annotation_type == 3

    vertices = list(leader.get_vertices())
    assert len(vertices) == 1
    assert vertices[0] == (0, 0, 0)

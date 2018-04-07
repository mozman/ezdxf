# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2010')


def test_material_manager(dwg):
    materials = dwg.materials
    assert 'ByLayer' in materials
    assert 'ByBlock' in materials
    assert 'Global' in materials
    assert 'Test' not in materials

    global_material = materials.get('Global')
    assert global_material.dxf.name == 'Global'
    assert global_material.dxf.channel_flags == 63


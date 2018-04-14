# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_sun(dwg):
    sun = dwg.objects.create_new_dxf_entity('FIELD', {})
    assert sun.dxftype() == 'FIELD'
    assert sun.dxf.evaluator_id == '_text'

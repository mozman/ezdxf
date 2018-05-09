# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_vba_project(dwg):
    vba = dwg.objects.create_new_dxf_entity('VBA_PROJECT', {})
    assert vba.dxftype() == 'VBA_PROJECT'
    assert vba.dxf.count == 0

    data = b'abcdefghij' * 100  # 1000 bytes => 4 DXFBinaryTags() with <= 254 bytes
    assert len(data) == 1000

    vba.set_data(data)
    assert vba.dxf.count == 4
    assert len(vba.AcDbVbaProject[-1].value) == 238

    b = vba.get_data()
    assert b == data

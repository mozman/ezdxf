# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Important assumption: ezdxf can already write correct DXF files
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dxf12(tmpdir_factory):
    doc = ezdxf.new2()
    msp = doc.modelspace()
    msp.add_line((0, 0), (1, 0))
    psp = doc.layout()
    psp.add_circle((0, 0), 1)
    filename = tmpdir_factory.mktemp("dxf12").join("test.dxf")
    doc.saveas(filename, dxfversion='R12')
    return filename


def test_load_dxf12(dxf12):
    doc = ezdxf.readfile2(dxf12)
    assert doc.dxfversion == ezdxf.DXF12

    msp = doc.modelspace()
    assert len(msp) == 1
    assert msp[0].dxftype() == 'LINE'

    psp = doc.layout()
    assert len(psp) == 1
    assert psp[0].dxftype() == 'CIRCLE'

# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Important assumption: ezdxf can already write correct DXF files
import pytest
import ezdxf


@pytest.fixture(scope='module', params=['R12', 'R2000'])
def dxf(request, tmpdir_factory):
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_line((0, 0), (1, 0))
    psp = doc.layout()
    psp.add_circle((0, 0), 1)
    filename = tmpdir_factory.mktemp(request.param).join("test.dxf")
    doc.dxfversion = request.param
    doc.saveas(filename)
    return filename


def test_load_dxf(dxf):
    doc = ezdxf.readfile(dxf)

    msp = doc.modelspace()
    assert len(msp) == 1
    assert msp[0].dxftype() == 'LINE'

    psp = doc.layout()
    assert len(psp) == 1
    assert psp[0].dxftype() == 'CIRCLE'

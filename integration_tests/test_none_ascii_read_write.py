# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import pytest
import os
import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new

NONE_ASCII = "äöüÄÖÜß±ØáàÀÁóòÓÒéèÉÈ"


@pytest.fixture(params=versions_supported_by_new)
def doc(request):
    return ezdxf.new2(request.param)


def test_write_and_read_unicode(doc, tmpdir):
    msp = doc.modelspace()
    msp.add_text(NONE_ASCII)
    filename = str(tmpdir.join('none_ascii_%s.dxf' % doc.dxfversion))
    try:
        doc.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), doc.dxfversion))
    assert os.path.exists(filename)

    doc = ezdxf.readfile2(filename)
    text = doc.modelspace().query('TEXT')
    assert len(text) == 1
    assert text[0].dxf.text == NONE_ASCII

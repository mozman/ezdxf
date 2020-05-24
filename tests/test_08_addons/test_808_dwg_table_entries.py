# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import base64
import ezdxf
from ezdxf.addons.dwg import FileHeader
from ezdxf.addons.dwg.const import *
from ezdxf.addons.dwg.objects import DwgAppID, DwgTextStyle
from ezdxf.entities.factory import EntityFactory


@pytest.fixture(scope='module')
def factory():
    doc = ezdxf.new('R2000')
    return EntityFactory(doc)


@pytest.fixture(scope='module')
def specs():
    return FileHeader(base64.b64decode(
        "QUMxMDE1AAAAAAAGAdwAAAAhNx4ABgAAAACLNwYANAIAAAGSPAYATwMAAAKYuAcATQ"
        "IAAAPlugcANQAAAASzuwcABAAAAAVhAAAAewAAACLalaBOKJmCGuVeQeBfnTpNAA=="
    ), crc_check=True)


def test_specs(specs):
    assert specs.version == ACAD_2000


OBJECT_12 = "UN0AAAAARKkEQUNBRMAEEJMFAA=="


def test_appid_12(specs, factory):
    data = base64.b64decode(OBJECT_12)
    dwg_obj = DwgAppID(specs, data, handle='12')
    assert dwg_obj.object_type == 67
    dwg_obj.update_dxfname({})

    dxf_obj = dwg_obj.dxf(factory)
    assert dxf_obj.dxf.name == 'ACAD'


OBJECT_11 = (
    "TW8AQAAARFDlESAAUAHkFyaWFsRwAAAACkIU3RhbmRhcmTCYAAAAAAAAAARAQlhcmlhbC5"
    "0dGaQQMwUA"
)


def test_style_11(specs, factory):
    data = base64.b64decode(OBJECT_11)
    dwg_obj = DwgTextStyle(specs, data, handle='11')
    assert dwg_obj.object_type == 53
    dwg_obj.update_dxfname({})

    dxf_obj = dwg_obj.dxf(factory)
    assert dxf_obj.dxf.name == 'Standard'
    assert dxf_obj.dxf.flags == 0
    assert dxf_obj.dxf.height == 0
    assert dxf_obj.dxf.width == 1
    assert dxf_obj.dxf.oblique == 0
    assert dxf_obj.dxf.generation_flags == 0
    assert dxf_obj.dxf.last_height == 2.5
    assert dxf_obj.dxf.font == 'arial.ttf'
    assert dxf_obj.dxf.bigfont == ''
    # unresolved appid 'ACAD' has handle 12
    xdata = dxf_obj.get_xdata('12')
    assert xdata[0] == (1000, 'Arial')
    assert xdata[1] == (1071, 0)


if __name__ == '__main__':
    pytest.main([__file__])

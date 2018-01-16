# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.legacy.tableentries import AppID



@pytest.fixture
def appid():
    return AppID.new('FFFF', dxfattribs={
        'name': 'EZDXF',
    })


def test_name(appid):
    assert appid.dxf.name == 'EZDXF'

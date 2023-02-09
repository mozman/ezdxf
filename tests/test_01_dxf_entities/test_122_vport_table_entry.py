# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.entities.vport import VPort


@pytest.fixture
def vport():
    return VPort.new(
        "FFFF",
        dxfattribs={
            "name": "VP1",
        },
    )


def test_name(vport):
    assert vport.dxf.name == "VP1"

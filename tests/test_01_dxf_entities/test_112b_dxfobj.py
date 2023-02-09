#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.entities import (
    DXFObject,
    is_dxf_object,
    DXFTagStorage,
    is_graphic_entity,
)

XRECORD = """  0
XRECORD
5
0
330
0
100
AcDbXrecord
280
1
"""


@pytest.fixture
def entity():
    return DXFTagStorage.from_text(XRECORD)


def test_is_dxf_object():
    assert is_dxf_object(DXFObject()) is True


def test_wrapped_xrecord_is_a_dxf_object(entity):
    assert is_dxf_object(entity) is True


def test_wrapped_xrecord_is_not_a_graphic_entity(entity):
    assert is_graphic_entity(entity) is False


if __name__ == "__main__":
    pytest.main([__file__])

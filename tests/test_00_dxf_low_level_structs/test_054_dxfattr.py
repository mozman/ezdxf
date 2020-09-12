# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest
from ezdxf.lldxf.attributes import DXFAttr, RETURN_DEFAULT


def test_return_default():
    attr = DXFAttr(
        code=62,
        default=12,
        validator=lambda x: False,
        fixer=RETURN_DEFAULT,
    )
    assert attr.fixer(7) == 12

    attr2 = DXFAttr(
        code=63,
        default=13,
        validator=lambda x: False,
        fixer=RETURN_DEFAULT,
    )
    assert attr2.fixer(7) == 13


if __name__ == '__main__':
    pytest.main([__file__])

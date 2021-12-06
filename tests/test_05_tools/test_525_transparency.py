#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf import colors

# DXF transparency value 0x020000TT
# 0x00 = fully transparent
# 0xff = opaque


@pytest.mark.parametrize("t_int, t_float", [
    (0x02000000, 1.0),
    (0x0200007F, 0.5),
    (0x020000FF, 0.0),
    (0, 1.0),
    (127, 0.5),
    (255, 0.0),
])
def test_transparency_to_float(t_int, t_float):
    assert round(colors.transparency2float(t_int), 2) == t_float


@pytest.mark.parametrize("t_int, t_float", [
    (0x02000000, 1.0),
    (0x0200007F, 0.5),
    (0x020000FF, 0.0),
])
def test_float_to_transparency(t_int, t_float):
    assert colors.float2transparency(t_float) == t_int


if __name__ == '__main__':
    pytest.main([__file__])

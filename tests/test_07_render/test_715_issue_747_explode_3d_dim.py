#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import math
import pytest
import ezdxf
from ezdxf.math import UCS, Vec3
from ezdxf.layouts import Modelspace


@pytest.fixture(scope="module")
def msp() -> Modelspace:
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    base = Vec3(0, 5)
    p1 = Vec3(-4, 3)
    p2 = Vec3(-1, 0)
    p4 = Vec3(4, 3)
    p3 = Vec3(1, 0)
    ucs = UCS(origin=(5, 7, -3)).rotate_local_x(math.radians(45))
    dim = msp.add_angular_dim_2l(
        base=base, line1=(p1, p2), line2=(p3, p4), dimstyle="EZ_CURVED"
    )
    dim.render(ucs=ucs)
    dim.dimension.explode()
    return msp


# Run example "examples/render/explode_3d_dimension.py" to create the DXF files
# for a visual comparison.

EXPECTED_EXT = Vec3(0.0, -0.7071067811865476, 0.7071067811865476)


def test_exploded_arrow_blocks(msp: Modelspace):
    b1, b2 = msp.query("INSERT")
    assert EXPECTED_EXT.isclose(b1.dxf.extrusion)
    assert EXPECTED_EXT.isclose(b2.dxf.extrusion)
    assert b1.dxf.insert.isclose(
        (9.242640687119284, 6.0710678118654755, -7.071067811865476)
    )
    assert b2.dxf.insert.isclose(
        (0.7573593128807152, 6.0710678118654755, -7.071067811865476)
    )


def test_exploded_arc(msp: Modelspace):
    arc = msp.query("ARC")[0]
    assert EXPECTED_EXT.isclose(arc.dxf.extrusion)
    assert arc.dxf.center.isclose((5.0, 1.8284271247461898, -7.071067811865476))
    assert math.isclose(arc.dxf.radius, 6.0)
    assert math.isclose(arc.dxf.start_angle, 47.38732414637843)
    assert math.isclose(arc.dxf.end_angle, 132.61267585362157)


def test_exploded_mtext(msp: Modelspace):
    mtext = msp.query("MTEXT")[0]
    assert EXPECTED_EXT.isclose(mtext.dxf.extrusion)
    assert mtext.dxf.insert.isclose(
        (5.0, 10.694632931699713, 0.6946329316997115)
    )
    assert mtext.dxf.text_direction.isclose((1.0, 0, 0))


def test_exploded_extension_line_1(msp: Modelspace):
    ext1, _ = msp.query("LINE")
    assert ext1.dxf.start.isclose(
        (9.08838834764832, 9.183820343559644, -0.8161796564403581)
    )
    assert ext1.dxf.end.isclose(
        (9.507805730064241, 9.480393218813454, -0.5196067811865479)
    )


def test_exploded_extension_line_2(msp: Modelspace):
    _, ext2 = msp.query("LINE")
    assert ext2.dxf.start.isclose(
        (0.9116116523516817, 9.183820343559644, -0.8161796564403581)
    )
    assert ext2.dxf.end.isclose(
        (0.49219426993575954, 9.480393218813454, -0.5196067811865479)
    )


if __name__ == "__main__":
    pytest.main([__file__])

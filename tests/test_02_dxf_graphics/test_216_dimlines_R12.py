# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope="module")
def dxf12():
    dwg = ezdxf.new("R12", setup="all")
    return dwg


def test_dimstyle_standard_exist(dxf12):
    assert "EZDXF" in dxf12.dimstyles


def test_dimstyle_override(dxf12):
    msp = dxf12.modelspace()
    dimstyle = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),
        dxfattribs={
            "dimstyle": "EZDXF",
        },
    )
    dimline = dimstyle.dimension
    assert dimline.dxf.dimstyle == "EZDXF"

    preset = {
        "dimtxsty": "TEST",  # virtual attribute - 'dimtxsty_handle' stores the text style handle
        "dimexe": 0.777,
        "dimblk": ezdxf.ARROWS.dot_blank,
    }
    dimstyle.update(preset)
    assert dimstyle["dimtxsty"] == "TEST"
    assert dimstyle["dimexe"] == 0.777

    assert dimstyle["invalid"] is None

    # ignores invalid attributes
    dimstyle.update({"invalid": 7})
    assert dimstyle["invalid"] == 7
    dstyle_orig = dimstyle.get_dstyle_dict()
    assert len(dstyle_orig) == 0

    dimstyle.commit()
    # check group code 5 handling for 'dimblk'
    data = dimline.get_xdata_list("ACAD", "DSTYLE")
    for tag in data:
        if tag.value == ezdxf.ARROWS.dot_blank:
            assert (
                tag.code == 1000
            ), "Despite group code 5, 'dimblk' should be treated as string, not as handle"

    dstyle = dimstyle.get_dstyle_dict()
    assert dstyle["dimexe"] == 0.777
    # unsupported DXF DimStyle attributes are not stored in dstyle
    assert "dimtxsty" not in dstyle, "dimtxsty is not a DXF12 attribute"


def test_dimstyle_override_arrows(dxf12):
    msp = dxf12.modelspace()
    preset = {
        "dimblk": "XYZ",
        "dimblk1": "ABC",
        "dimblk2": "DEF",
        "dimldrblk": "ZZZLDR",  # not supported by DXF12, but used by ezdxf for rendering
    }

    dimstyle = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),
        dimstyle="EZDXF",
        override=preset,
    )

    assert dimstyle["dimblk"] == "XYZ"
    assert dimstyle["dimblk1"] == "ABC"
    assert dimstyle["dimblk2"] == "DEF"
    assert dimstyle["dimldrblk"] == "ZZZLDR"

    dstyle_orig = dimstyle.get_dstyle_dict()
    assert len(dstyle_orig) == 0

    dimstyle.commit()
    dstyle = dimstyle.get_dstyle_dict()
    assert dstyle["dimblk"] == "XYZ"
    assert dstyle["dimblk1"] == "ABC"
    assert dstyle["dimblk2"] == "DEF"
    assert "dimldrblk" not in dstyle, "not supported by DXF12"

    dimstyle.set_arrows(blk="BLK", blk1="B1", blk2="B2", ldrblk="LBLK")
    assert dimstyle["dimblk"] == "BLK"
    assert dimstyle["dimblk1"] == "B1"
    assert dimstyle["dimblk2"] == "B2"
    assert (
        dimstyle["dimldrblk"] == "LBLK"
    )  # not supported by DXF12, but used by ezdxf for rendering

    dimstyle.commit()
    dstyle = dimstyle.get_dstyle_dict()
    assert dstyle["dimblk"] == "BLK"
    assert dstyle["dimblk1"] == "B1"
    assert dstyle["dimblk2"] == "B2"
    assert "dimnldrblk" not in dstyle, "not supported by DXF12"


def test_dimstyle_override_linetypes(dxf12):
    msp = dxf12.modelspace()
    preset = {
        "dimltype": "DOT",
        "dimltex1": "DOT2",
        "dimltex2": "DOTX2",
    }
    dimstyle = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),
        dimstyle="EZDXF",
        override=preset,
    )
    assert dimstyle["dimltype"] == "DOT"
    assert dimstyle["dimltex1"] == "DOT2"
    assert dimstyle["dimltex2"] == "DOTX2"

    dimstyle.commit()
    dstyle = dimstyle.get_dstyle_dict()
    assert "dimltype" not in dstyle, "not supported by DXF12"
    assert "dimltype_handle" not in dstyle, "not supported by DXF12"
    assert "dimltex1" not in dstyle, "not supported by DXF12"
    assert "dimltex1_handle" not in dstyle, "not supported by DXF12"
    assert "dimltex2" not in dstyle, "not supported by DXF12"
    assert "dimltex2_handle" not in dstyle, "not supported by DXF12"


def test_horizontal_dimline(dxf12):
    msp = dxf12.modelspace()
    dimstyle = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),
    )
    dimline = dimstyle.dimension
    assert dimline.dxf.dimstyle == "EZDXF"

    dimstyle.render()
    block_name = dimline.dxf.geometry
    assert block_name.startswith("*D")

    # shortcut for: block = dxf12.blocks.get(block_name)
    block = dimline.get_geometry_block()
    assert len(list(block.query("TEXT"))) == 1
    assert len(list(block.query("INSERT"))) == 2
    assert (
        len(list(block.query("LINE"))) == 3
    )  # dimension line + 2 extension lines
    assert len(list(block.query("POINT"))) == 3  # def points

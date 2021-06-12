# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.lldxf.tagger import internal_tag_compiler
from ezdxf.document import Drawing, CREATED_BY_EZDXF, WRITTEN_BY_EZDXF
from ezdxf import DXFValueError, decode_base64


def test_dxfversion_1():
    doc = Drawing.from_tags(internal_tag_compiler(TEST_HEADER))
    assert "AC1009" == doc.dxfversion


@pytest.fixture(scope="module")
def dwg_r12():
    return Drawing.new("AC1009")


def test_dxfversion_2(dwg_r12):
    assert "AC1009" == dwg_r12.dxfversion


def test_acad_release(dwg_r12):
    assert "R12" == dwg_r12.acad_release


def test_get_layer(dwg_r12):
    layer = dwg_r12.layers.get("0")
    assert "0" == layer.dxf.name


def test_error_getting_not_existing_layer(dwg_r12):
    with pytest.raises(DXFValueError):
        layer = dwg_r12.layers.get("TEST_NOT_EXISTING_LAYER")


def test_create_layer(dwg_r12):
    layer = dwg_r12.layers.new("TEST_NEW_LAYER")
    assert "TEST_NEW_LAYER" == layer.dxf.name


def test_error_adding_existing_layer(dwg_r12):
    with pytest.raises(DXFValueError):
        layer = dwg_r12.layers.new("0")


def test_has_layer(dwg_r12):
    assert "0" in dwg_r12.layers


def test_has_not_layer(dwg_r12):
    assert "TEST_LAYER_NOT_EXISTS" not in dwg_r12.layers


def test_removing_layer(dwg_r12):
    dwg_r12.layers.new("TEST_NEW_LAYER_2")
    assert "TEST_NEW_LAYER_2" in dwg_r12.layers
    dwg_r12.layers.remove("TEST_NEW_LAYER_2")
    assert "TEST_NEW_LAYER_2" not in dwg_r12.layers


def test_error_removing_not_existing_layer(dwg_r12):
    with pytest.raises(DXFValueError):
        dwg_r12.layers.remove("TEST_LAYER_NOT_EXISTS")


@pytest.fixture(scope="module")
def dwg_r2000():
    return Drawing.new("AC1015")


def test_r2000_dxfversion(dwg_r2000):
    assert "AC1015" == dwg_r2000.dxfversion


def test_r2000_acad_release(dwg_r2000):
    assert "R2000" == dwg_r2000.acad_release


@pytest.fixture
def min_r12():
    return Drawing.from_tags(internal_tag_compiler(MINIMALISTIC_DXF12))


def test_min_r12_header_section(min_r12):
    assert hasattr(min_r12, "header")
    assert min_r12.header["$ACADVER"] == "AC1009"
    assert min_r12.header["$DWGCODEPAGE"] == "ANSI_1252"


def test_min_r12_layers_table(min_r12):
    assert hasattr(min_r12, "layers")
    assert len(min_r12.layers) == 2
    assert "0" in min_r12.layers
    assert "Defpoints" in min_r12.layers


def test_min_r12_styles_table(min_r12):
    assert hasattr(min_r12, "styles")
    assert len(min_r12.styles) == 1
    assert "Standard" in min_r12.styles


def test_min_r12_linetypes_table(min_r12):
    assert hasattr(min_r12, "linetypes")
    assert len(min_r12.linetypes) == 3
    assert "continuous" in min_r12.linetypes
    assert "ByLayer" in min_r12.linetypes
    assert "ByBlock" in min_r12.linetypes


def test_min_r12_blocks_section(min_r12):
    assert hasattr(min_r12, "blocks")
    assert len(min_r12.blocks) == 2
    assert "*Model_Space" in min_r12.blocks
    assert "*Paper_Space" in min_r12.blocks


def test_min_r12_entity_section(min_r12):
    assert hasattr(min_r12, "entities")
    assert len(min_r12.entities) == 0


def test_chain_layout_and_block(dwg_r12, dwg_r2000):
    for dwg in (dwg_r12, dwg_r2000):
        msp = dwg.modelspace()
        line_msp = msp.add_line((0, 0), (1, 1))
        blk = dwg.blocks.new("TEST_CHAIN")
        line_blk = blk.add_line((0, 0), (1, 1))

        handles = list(e.dxf.handle for e in dwg.chain_layouts_and_blocks())
        # check for unique handles
        assert len(handles) == len(set(handles))

        check = {line_msp.dxf.handle, line_blk.dxf.handle}
        assert check.intersection(handles) == check


def test_base64_encoding_r12(dwg_r12):
    data = dwg_r12.encode_base64()
    doc = decode_base64(data)
    assert doc.acad_release == "R12"


def test_base64_encoding_r2000(dwg_r2000):
    data = dwg_r2000.encode_base64()
    doc = decode_base64(data)
    assert doc.acad_release == "R2000"


def test_set_drawing_units(dwg_r12):
    dwg_r12.units = 6
    assert dwg_r12.header["$INSUNITS"] == 6
    dwg_r12.units = 5
    assert dwg_r12.header["$INSUNITS"] == 5


def test_created_by_ezdxf_metadata_r2000(dwg_r2000):
    metadata = dwg_r2000.ezdxf_metadata().load()
    assert metadata[CREATED_BY_EZDXF] == ezdxf.__version__


@pytest.mark.xfail(reason="storing XDATA in layer 0 does not work (Autodesk!)")
def test_created_by_ezdxf_metadata_r12(dwg_r12):
    metadata = dwg_r12.ezdxf_metadata().load()
    assert metadata[CREATED_BY_EZDXF] == ezdxf.__version__


def test_written_by_ezdxf_metadata_r2000(dwg_r2000, tmp_path):
    dwg_r2000.saveas(tmp_path / "r2000.dxf")
    metadata = dwg_r2000.ezdxf_metadata().load()
    assert metadata[WRITTEN_BY_EZDXF] == ezdxf.__version__


@pytest.mark.xfail(reason="storing XDATA in layer 0 does not work (Autodesk!)")
def test_written_by_ezdxf_metadata_r12(dwg_r12, tmp_path):
    dwg_r12.saveas(tmp_path / "r12.dxf")
    metadata = dwg_r12.ezdxf_metadata().load()
    assert metadata[WRITTEN_BY_EZDXF] == ezdxf.__version__


MINIMALISTIC_DXF12 = """  0
SECTION
  2
ENTITIES
  0
ENDSEC
  0
EOF
"""

TEST_HEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$DWGCODEPAGE
  3
ANSI_1252
  9
$HANDSEED
  5
FF
  0
ENDSEC
  0
SECTION
  2
ENTITIES
  0
ENDSEC
  0
EOF
"""

TESTCOPY = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  9
$TDUPDATE
 40
0.
  9
$HANDSEED
  5
FF
  0
ENDSEC
  0
SECTION
  2
OBJECTS
  0
ENDSEC
  0
SECTION
  2
FANTASYSECTION
  1
everything should be copied
  0
ENDSEC
  0
SECTION
  2
ALPHASECTION
  1
everything should be copied
  0
ENDSEC
  0
SECTION
  2
OMEGASECTION
  1
everything should be copied
  0
ENDSEC
  0
EOF
"""

# Purpose: test drawing
# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from ezdxf.lldxf.tagger import internal_tag_compiler
from ezdxf.drawing import Drawing
from ezdxf.templates import TemplateLoader
from ezdxf import is_dxf_file
from ezdxf import DXFValueError


def test_dxfversion_1():
    dwg = Drawing(internal_tag_compiler(TEST_HEADER))
    assert 'AC1009' == dwg.dxfversion


@pytest.fixture(scope='module')
def dwg_r12():
    return Drawing.new('AC1009')


def test_dxfversion_2(dwg_r12):
    assert 'AC1009' == dwg_r12.dxfversion


def test_acad_release(dwg_r12):
    assert 'R12' == dwg_r12.acad_release


def test_get_layer(dwg_r12):
    layer = dwg_r12.layers.get('0')
    assert '0' == layer.dxf.name


def test_error_getting_not_existing_layer(dwg_r12):
    with pytest.raises(DXFValueError):
        layer = dwg_r12.layers.get('TEST_NOT_EXISTING_LAYER')


def test_create_layer(dwg_r12):
    layer = dwg_r12.layers.new('TEST_NEW_LAYER')
    assert 'TEST_NEW_LAYER' == layer.dxf.name


def test_error_adding_existing_layer(dwg_r12):
    with pytest.raises(DXFValueError):
        layer = dwg_r12.layers.new('0')


def test_has_layer(dwg_r12):
    assert '0' in dwg_r12.layers


def test_has_not_layer(dwg_r12):
    assert 'TEST_LAYER_NOT_EXISTS' not in dwg_r12.layers


def test_removing_layer(dwg_r12):
    dwg_r12.layers.new('TEST_NEW_LAYER_2')
    assert 'TEST_NEW_LAYER_2' in dwg_r12.layers
    dwg_r12.layers.remove('TEST_NEW_LAYER_2')
    assert 'TEST_NEW_LAYER_2' not in dwg_r12.layers


def test_error_removing_not_existing_layer(dwg_r12):
    with pytest.raises(DXFValueError):
        dwg_r12.layers.remove('TEST_LAYER_NOT_EXISTS')


@pytest.fixture(scope='module')
def dwg_r2000():
    return Drawing.new('AC1015')


def test_r2000_dxfversion(dwg_r2000):
    assert 'AC1015' == dwg_r2000.dxfversion


def test_r2000_acad_release(dwg_r2000):
        assert 'R2000' == dwg_r2000.acad_release


def test_template():
    template_file = TemplateLoader().filepath('AC1009')
    assert is_dxf_file(template_file) is True


@pytest.fixture
def min_r12():
    return Drawing(internal_tag_compiler(MINIMALISTIC_DXF12))


def test_min_r12_header_section(min_r12):
    assert hasattr(min_r12, 'header')
    assert min_r12.header['$ACADVER'] == 'AC1009'
    assert min_r12.header['$DWGCODEPAGE'] == 'ANSI_1252'


def test_min_r12_layers_table(min_r12):
    assert hasattr(min_r12, 'layers')
    assert len(min_r12.layers) == 0


def test_min_r12_styles_table(min_r12):
    assert hasattr(min_r12, 'styles')
    assert len(min_r12.styles) == 0


def test_min_r12_linetypes_table(min_r12):
    assert hasattr(min_r12, 'linetypes')
    assert len(min_r12.linetypes) == 0


def test_min_r12_blocks_section(min_r12):
    assert hasattr(min_r12, 'blocks')
    assert len(min_r12.blocks) == 0


def test_min_r12_entity_section(min_r12):
    assert hasattr(min_r12, 'entities')
    assert len(min_r12.entities) == 0


def test_chain_layout_and_block(dwg_r12, dwg_r2000):
    for dwg in (dwg_r12, dwg_r2000):
        msp = dwg.modelspace()
        line_msp = msp.add_line((0, 0), (1, 1))
        blk = dwg.blocks.new('TEST_CHAIN')
        line_blk = blk.add_line((0, 0), (1, 1))

        handles = list(e.dxf.handle for e in dwg.chain_layouts_and_blocks())
        # check for unique handles
        assert len(handles) == len(set(handles))

        check = {line_msp.dxf.handle, line_blk.dxf.handle}
        assert check.intersection(handles) == check


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

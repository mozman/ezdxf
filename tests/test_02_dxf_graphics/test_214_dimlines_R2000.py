# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.dimension import Dimension


@pytest.fixture(scope='module')
def dxf2000():
    return ezdxf.new('R2000', setup='all')


@pytest.fixture(scope='module')
def dxf2007():
    return ezdxf.new('R2007', setup='all')


def test_dimstyle_standard_exist(dxf2000):
    assert 'EZDXF' in dxf2000.dimstyles


def test_rotated_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.LINEAR
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dim_type == Dimension.LINEAR
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.insert == (0, 0, 0)
    assert dimline.dxf.defpoint2 == (0, 0, 0)
    assert dimline.dxf.defpoint3 == (0, 0, 0)
    assert dimline.dxf.angle == 0.
    assert dimline.dxf.oblique_angle == 0.


def test_aligned_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.ALIGNED
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dim_type == Dimension.ALIGNED
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.insert == (0, 0, 0)
    assert dimline.dxf.defpoint2 == (0, 0, 0)
    assert dimline.dxf.defpoint3 == (0, 0, 0)
    assert dimline.dxf.angle == 0.
    assert dimline.dxf.oblique_angle == 0.


def test_angular_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.ANGULAR
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dim_type == Dimension.ANGULAR
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint2 == (0, 0, 0)
    assert dimline.dxf.defpoint3 == (0, 0, 0)
    assert dimline.dxf.defpoint4 == (0, 0, 0)
    assert dimline.dxf.defpoint5 == (0, 0, 0)


def test_angular_3p_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.ANGULAR_3P
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dim_type == Dimension.ANGULAR_3P


def test_radius_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.RADIUS
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dim_type == Dimension.RADIUS
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint4 == (0, 0, 0)
    assert dimline.supports_dxf_attrib('leader_length')


def test_diameter_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.DIAMETER
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dim_type == Dimension.DIAMETER
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint4 == (0, 0, 0)
    assert dimline.supports_dxf_attrib('leader_length')


def test_ordinate_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.ORDINATE
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dim_type == Dimension.ORDINATE
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint2 == (0, 0, 0)
    assert dimline.dxf.defpoint3 == (0, 0, 0)


def test_add_horizontal_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dimstyle = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),

    )
    dimline = dimstyle.dimension
    assert dimline.dxf.dimstyle == 'EZDXF'
    dimstyle.render()
    block_name = dimline.dxf.geometry
    assert block_name.startswith('*D')

    block = dxf2000.blocks.get(block_name)
    assert len(list(block.query('MTEXT'))) == 1
    assert len(list(block.query('INSERT'))) == 2
    assert len(list(block.query('LINE'))) == 3  # dimension line + 2 extension lines
    assert len(list(block.query('POINT'))) == 3  # def points


def test_dimstyle_override(dxf2000):
    msp = dxf2000.modelspace()
    dimstyle = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),
        dxfattribs={
            'dimstyle': 'EZDXF',
        }
    )
    dimline = dimstyle.dimension
    assert dimline.dxf.dimstyle == 'EZDXF'
    if 'TEST' not in dxf2000.styles:  # text style must exists
        dxf2000.styles.new('TEST')

    preset = {
        'dimtxsty': 'TEST',
        'dimexe': 0.777,
    }
    dimstyle.update(preset)
    assert dimstyle['dimtxsty'] == 'TEST'
    assert dimstyle['dimexe'] == 0.777

    assert dimstyle['invalid'] is None
    dimstyle.update({'invalid': 7})
    # ezdxf 0.10 and later uses internally only resource names not handles for dim style attributes
    # unknown attributes are ignored
    dstyle_orig = dimstyle.get_dstyle_dict()
    assert len(dstyle_orig) == 0

    dimstyle.commit()
    # ezdxf 0.10 and later uses internally only resource names not handles for dim style attributes
    dstyle = dimstyle.get_dstyle_dict()

    assert dstyle['dimexe'] == 0.777

    # handle attributes not available, just stored transparent in XDATA
    assert 'dimtxsty_handle' not in dstyle

    assert dstyle['dimtxsty'] == 'TEST'


def test_linetype_override_R2000(dxf2000):
    msp = dxf2000.modelspace()
    preset = {
        'dimltype': 'DOT',
        'dimltex1': 'DOT2',
        'dimltex2': 'DOTX2',
    }
    dimstyle = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),
        dimstyle='EZDXF',
        override=preset,
    )
    assert dimstyle['dimltype'] == 'DOT'
    assert dimstyle['dimltex1'] == 'DOT2'
    assert dimstyle['dimltex2'] == 'DOTX2'

    dimstyle.commit()
    # ezdxf 0.10 and later uses internally only resource names not handles for dim style attributes
    dstyle = dimstyle.get_dstyle_dict()

    # handle attributes not available, just stored transparent in XDATA
    assert 'dimltype_handle' not in dstyle
    assert 'dimltex1_handle' not in dstyle
    assert 'dimltex2_handle' not in dstyle

    # line type not supported by DXF R2000
    assert 'dimltype' not in dstyle
    assert 'dimltex1' not in dstyle
    assert 'dimltex2' not in dstyle


def test_linetype_override_R2007(dxf2007):
    msp = dxf2007.modelspace()
    preset = {
        'dimltype': 'DOT',
        'dimltex1': 'DOT2',
        'dimltex2': 'DOTX2',
    }
    dimstyle = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),
        dimstyle='EZDXF',
        override=preset,
    )
    assert dimstyle['dimltype'] == 'DOT'
    assert dimstyle['dimltex1'] == 'DOT2'
    assert dimstyle['dimltex2'] == 'DOTX2'

    dimstyle.commit()
    # ezdxf 0.10 and later uses internally only resource names not handles for dim style attributes
    dstyle = dimstyle.get_dstyle_dict()

    # handle attributes not available, just stored transparent in XDATA
    assert 'dimltype_handle' not in dstyle
    assert 'dimltex1_handle' not in dstyle
    assert 'dimltex2_handle' not in dstyle

    assert dstyle['dimltype'] == 'DOT'
    assert dstyle['dimltex1'] == 'DOT2'
    assert dstyle['dimltex2'] == 'DOTX2'


def test_dimstyle_override_arrows(dxf2000):
    msp = dxf2000.modelspace()
    arrows = ezdxf.ARROWS
    blocks = dxf2000.blocks

    arrows.create_block(blocks, arrows.dot_blank)
    arrows.create_block(blocks, arrows.box)
    arrows.create_block(blocks, arrows.closed)
    arrows.create_block(blocks, arrows.closed_filled)

    preset = {
        'dimblk': arrows.dot_blank,
        'dimblk1': arrows.box,
        'dimblk2': arrows.closed,
        'dimldrblk': arrows.closed_filled,  # virtual attribute
    }
    dimstyle = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),
        dimstyle='EZDXF',
        override=preset,
    )
    # still as block names stored
    assert dimstyle['dimblk'] == arrows.dot_blank
    assert dimstyle['dimblk1'] == arrows.box
    assert dimstyle['dimblk2'] == arrows.closed
    assert dimstyle['dimldrblk'] == arrows.closed_filled

    dstyle_orig = dimstyle.get_dstyle_dict()
    assert len(dstyle_orig) == 0

    dimstyle.commit()
    # ezdxf 0.10 and later uses internally only resource names not handles for dim style attributes
    dstyle = dimstyle.get_dstyle_dict()

    # handle attributes not available, just stored transparent in XDATA
    assert 'dimblk_handle' not in dstyle
    assert 'dimblk1_handle' not in dstyle
    assert 'dimblk2_handle' not in dstyle
    assert 'dimldrblk_handle' not in dstyle

    assert dstyle['dimblk'] == arrows.dot_blank
    assert dstyle['dimblk1'] == arrows.box
    assert dstyle['dimblk2'] == arrows.closed
    assert dstyle['dimldrblk'] == ''  # special handle for closed filled

    dimstyle.set_arrows(blk=arrows.closed, blk1=arrows.dot_blank, blk2=arrows.box, ldrblk=arrows.dot_small)
    assert dimstyle['dimblk'] == arrows.closed
    assert dimstyle['dimblk1'] == arrows.dot_blank
    assert dimstyle['dimblk2'] == arrows.box
    assert dimstyle['dimldrblk'] == arrows.dot_small

    dimstyle.commit()
    # ezdxf 0.10 and later uses internally only resource names not handles for dim style attributes
    dstyle = dimstyle.get_dstyle_dict()
    assert dstyle['dimblk'] == arrows.closed
    assert dstyle['dimblk1'] == arrows.dot_blank
    assert dstyle['dimblk2'] == arrows.box
    # create acad arrows on demand
    assert dstyle['dimldrblk'] == arrows.dot_small

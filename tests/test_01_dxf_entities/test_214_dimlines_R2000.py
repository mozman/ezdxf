# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.dimension import Dimension


@pytest.fixture(scope='module')
def dxf2000():
    return ezdxf.new2('R2000', setup='all')


@pytest.fixture(scope='module')
def dxf2007():
    return ezdxf.new2('R2007', setup='all')


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
        'dimtxsty': 'TEST',  # virtual attribute - 'dimtxsty_handle' stores the text style handle
        'dimexe': 0.777,
    }
    dimstyle.update(preset)
    assert dimstyle['dimtxsty'] == 'TEST'
    assert dimstyle['dimexe'] == 0.777

    assert dimstyle['invalid'] is None
    dimstyle.update({'invalid': 7})
    # unknown attributes are ignored
    dstyle_orig = dimstyle.get_dstyle_dict()
    assert len(dstyle_orig) == 0

    dimstyle.commit()
    dstyle = dimstyle.get_dstyle_dict()
    assert dstyle['dimexe'] == 0.777
    assert 'dimtxsty' not in dstyle, 'do not store "dimtxsty" in dstyle, because virtual attribute'
    assert 'dimtxsty_handle' in dstyle, 'expected handle of text style'
    assert dstyle['dimtxsty_handle'] == dxf2000.styles.get('TEST').dxf.handle


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
    dstyle = dimstyle.get_dstyle_dict()
    assert 'dimltype_handle' not in dstyle, "not supported by DXF R2000"
    assert 'dimltex1_handle' not in dstyle, "not supported by DXF R2000"
    assert 'dimltex2_handle' not in dstyle, "not supported by DXF R2000"
    assert 'dimltype' not in dstyle, "not a real dimvar"
    assert 'dimltex1' not in dstyle, "not a real dimvar"
    assert 'dimltex2' not in dstyle, "not a real dimvar"


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

    dstyle = dimstyle.get_dstyle_dict()
    assert dstyle['dimltype_handle'] == dxf2007.linetypes.get('DOT').dxf.handle
    assert dstyle['dimltex1_handle'] == dxf2007.linetypes.get('DOT2').dxf.handle
    assert dstyle['dimltex2_handle'] == dxf2007.linetypes.get('DOTX2').dxf.handle
    assert 'dimltype' not in dstyle, "not a real dimvar"
    assert 'dimltex1' not in dstyle, "not a real dimvar"
    assert 'dimltex2' not in dstyle, "not a real dimvar"


def test_dimstyle_override_arrows(dxf2000):
    msp = dxf2000.modelspace()
    arrows = ezdxf.ARROWS
    blocks = dxf2000.blocks

    dot_blank = arrows.create_block(blocks, arrows.dot_blank)
    dimblk = blocks.get(dot_blank)

    box = arrows.create_block(blocks, arrows.box)
    dimblk1 = blocks.get(box)

    closed = arrows.create_block(blocks, arrows.closed)
    dimblk2 = blocks.get(closed)

    closed_filled = arrows.create_block(blocks, arrows.closed_filled)
    dimldrblk = blocks.get(closed_filled)

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
    # now store blocks as block handles
    dstyle = dimstyle.get_dstyle_dict()
    assert 'dimblk' not in dstyle, 'Do not store block name, dimblk_handle is required'
    assert 'dimblk1' not in dstyle, 'Do not store block name, dimblk1_handle is required'
    assert 'dimblk2' not in dstyle, 'Do not store block name, dimblk2_handle is required'
    assert 'dimldrblk' not in dstyle, 'Do not store block name, dimldrblk_handle is required'

    assert dstyle['dimblk_handle'] == dimblk.block_record_handle
    assert dstyle['dimblk1_handle'] == dimblk1.block_record_handle
    assert dstyle['dimblk2_handle'] == dimblk2.block_record_handle
    assert dstyle['dimldrblk_handle'] == '0'  # special handle for closed filled

    dimstyle.set_arrows(blk=arrows.closed, blk1=arrows.dot_blank, blk2=arrows.box, ldrblk=arrows.dot_small)
    assert dimstyle['dimblk'] == arrows.closed
    assert dimstyle['dimblk1'] == arrows.dot_blank
    assert dimstyle['dimblk2'] == arrows.box
    assert dimstyle['dimldrblk'] == arrows.dot_small

    dimstyle.commit()
    dstyle = dimstyle.get_dstyle_dict()
    assert dstyle['dimblk_handle'] == dimblk2.block_record_handle
    assert dstyle['dimblk1_handle'] == dimblk.block_record_handle
    assert dstyle['dimblk2_handle'] == dimblk1.block_record_handle
    # create acad arrows on demand
    assert dstyle['dimldrblk_handle'] == blocks.get(arrows.block_name(arrows.dot_small)).block_record_handle

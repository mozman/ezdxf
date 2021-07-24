# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.dimension import Dimension
from ezdxf.protocols import SupportsVirtualEntities, query_virtual_entities

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
    assert dimline.dimtype == Dimension.LINEAR
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
    assert dimline.dimtype == Dimension.ALIGNED
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
    assert dimline.dimtype == Dimension.ANGULAR
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
    assert dimline.dimtype == Dimension.ANGULAR_3P


def test_radius_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.RADIUS
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dimtype == Dimension.RADIUS
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint4 == (0, 0, 0)
    assert dimline.is_supported_dxf_attrib('leader_length')


def test_diameter_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.DIAMETER
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dimtype == Dimension.DIAMETER
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint4 == (0, 0, 0)
    assert dimline.is_supported_dxf_attrib('leader_length')


def test_ordinate_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.ORDINATE
    }
    dimline = msp.new_entity('DIMENSION', dxfattribs)
    assert dimline.dimtype == Dimension.ORDINATE
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint2 == (0, 0, 0)
    assert dimline.dxf.defpoint3 == (0, 0, 0)


def add_linear_dimension(doc):
    msp = doc.modelspace()
    override = msp.add_linear_dim(
        base=(3, 2, 0),
        p1=(0, 0, 0),
        p2=(3, 0, 0),

    )
    override.render()
    return override.dimension


def test_add_horizontal_dimline(dxf2000):
    dimline = add_linear_dimension(dxf2000)
    assert dimline.dxf.dimstyle == 'EZDXF'
    block_name = dimline.dxf.geometry
    assert block_name.startswith('*D')

    block = dimline.get_geometry_block()
    assert len(list(block.query('MTEXT'))) == 1
    assert len(list(block.query('INSERT'))) == 2
    assert len(
        list(block.query('LINE'))) == 3  # dimension line + 2 extension lines
    assert len(list(block.query('POINT'))) == 3  # def points


def test_virtual_entities_and_explode(dxf2000):
    dimline = add_linear_dimension(dxf2000)

    parts = list(dimline.virtual_entities())
    assert len(parts) == 9
    geometry = dimline.dxf.geometry
    parts = dimline.explode()
    assert len(list(parts.query('MTEXT'))) == 1
    assert len(list(parts.query('INSERT'))) == 2
    assert len(
        list(parts.query('LINE'))) == 3  # dimension line + 2 extension lines
    assert len(list(parts.query('POINT'))) == 3  # def points
    assert dimline.is_alive is False
    assert geometry in dxf2000.blocks, 'Do not destroy anonymous block, may be used by block references.'


def test_transformation_of_associated_anonymous_geometry_block(dxf2000):
    dimline = add_linear_dimension(dxf2000)
    dx, dy = 1, 1
    block = dimline.get_geometry_block()
    original_points = [e.dxf.location for e in block if e.dxftype() == 'POINT']
    dimline.translate(dx, dy, 0)
    transformed_points = [e.dxf.location for e in block if
                          e.dxftype() == 'POINT']
    for o, t in zip(original_points, transformed_points):
        assert t.isclose(o + (dx, dy))


def test_copy_dimension_with_geometry_block(dxf2000):
    dimline = add_linear_dimension(dxf2000)
    vcopy = dimline.copy()
    assert vcopy.virtual_block_content is not None
    assert vcopy.dxf.hasattr('geometry') is False
    block = dimline.get_geometry_block()
    assert len(vcopy.virtual_block_content) == len(block)
    for copy, original in zip(vcopy.virtual_block_content, block):
        assert copy.is_virtual is True
        assert original.is_virtual is False
        assert copy.dxftype() == original.dxftype()


def test_destroy_virtual_dimension_copy(dxf2000):
    dimline = add_linear_dimension(dxf2000)
    dimline.destroy()
    assert hasattr(dimline, 'virtual_block_content') is False


def test_transform_virtual_geometry_block(dxf2000):
    original = add_linear_dimension(dxf2000)

    original_points = [e.dxf.location for e in original.virtual_entities()
                       if e.dxftype() == 'POINT']
    vcopy = original.copy()
    dx, dy = 1, 1
    vcopy.translate(dx, dy, 0)
    transformed_points = [e.dxf.location for e in vcopy.virtual_entities() if
                          e.dxftype() == 'POINT']
    assert len(transformed_points) == len(original_points)
    for o, t in zip(original_points, transformed_points):
        assert t.isclose(o + (dx, dy))


def test_add_virtual_dimension_copy_to_layout(dxf2000):
    dimline = add_linear_dimension(dxf2000)
    vcopy = dimline.copy()
    msp = dxf2000.modelspace()
    content = vcopy.virtual_block_content
    msp.add_entity(vcopy)
    assert vcopy.is_virtual is False
    assert vcopy.virtual_block_content is None
    assert all(not e.is_virtual for e in content), \
        "all entities should be non virtual"
    db = dxf2000.entitydb
    assert all(e.dxf.handle in db for e in content), \
        "all entities should be stored in the entity database"
    assert all(e.doc is dxf2000 for e in content), \
        "all entities should be bound to the document"


def test_supports_virtual_entities_protocol(dxf2000):
    dimline = add_linear_dimension(dxf2000)
    assert isinstance(dimline, SupportsVirtualEntities) is True
    assert len(query_virtual_entities(dimline)) > 0


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

    dimstyle.set_arrows(blk=arrows.closed, blk1=arrows.dot_blank,
                        blk2=arrows.box, ldrblk=arrows.dot_small)
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

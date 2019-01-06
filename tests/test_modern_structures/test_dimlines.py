# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.lldxf.const import DXFAttributeError
from ezdxf.modern.dimension import Dimension


@pytest.fixture(scope='module')
def dxf2000():
    dwg = ezdxf.new('R2000', setup='all')
    return dwg


def test_dimstyle_standard_exist(dxf2000):
    assert 'EZDXF' in dxf2000.dimstyles


def test_rotated_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.LINEAR
    }
    dimline = msp.build_and_add_entity('DIMENSION', dxfattribs)
    aligned = dimline.tags.subclasses[3][0]
    assert aligned.code == 100 and aligned.value == 'AcDbAlignedDimension'
    rotated = dimline.tags.subclasses[4][0]
    assert rotated.code == 100 and rotated.value == 'AcDbRotatedDimension'
    assert len(dimline.tags.subclasses) == 5

    dimline = dimline.cast()
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
    dimline = msp.build_and_add_entity('DIMENSION', dxfattribs)
    aligned = dimline.tags.subclasses[3][0]
    assert aligned.code == 100 and aligned.value == 'AcDbAlignedDimension'
    assert len(dimline.tags.subclasses) == 4

    dimline = dimline.cast()
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
    dimline = msp.build_and_add_entity('DIMENSION', dxfattribs)
    angular = dimline.tags.subclasses[3][0]
    assert angular.code == 100 and angular.value == 'AcDb3dPointAngularDimension'
    assert len(dimline.tags.subclasses) == 4

    dimline = dimline.cast()
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
    dimline = msp.build_and_add_entity('DIMENSION', dxfattribs)
    angular = dimline.tags.subclasses[3][0]
    assert angular.code == 100 and angular.value == 'AcDb3dPointAngularDimension'
    assert len(dimline.tags.subclasses) == 4


def test_radius_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.RADIUS
    }
    dimline = msp.build_and_add_entity('DIMENSION', dxfattribs)
    radius = dimline.tags.subclasses[3][0]
    assert radius.code == 100 and radius.value == 'AcDbRadialDimension'
    assert len(dimline.tags.subclasses) == 4

    dimline = dimline.cast()
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint4 == (0, 0, 0)
    assert dimline.supports_dxf_attrib('leader_length')


def test_diameter_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.DIAMETER
    }
    dimline = msp.build_and_add_entity('DIMENSION', dxfattribs)
    diameter = dimline.tags.subclasses[3][0]
    assert diameter.code == 100 and diameter.value == 'AcDbDiametricDimension'
    assert len(dimline.tags.subclasses) == 4

    dimline = dimline.cast()
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint4 == (0, 0, 0)
    assert dimline.supports_dxf_attrib('leader_length')


def test_ordinate_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dxfattribs = {
        'dimtype': Dimension.ORDINATE
    }
    dimline = msp.build_and_add_entity('DIMENSION', dxfattribs)
    ordinate = dimline.tags.subclasses[3][0]
    assert ordinate.code == 100 and ordinate.value == 'AcDbOrdinateDimension'
    assert len(dimline.tags.subclasses) == 4

    dimline = dimline.cast()
    assert dimline.dxf.defpoint == (0, 0, 0)
    assert dimline.dxf.defpoint2 == (0, 0, 0)
    assert dimline.dxf.defpoint3 == (0, 0, 0)


def test_add_horizontal_dimline(dxf2000):
    msp = dxf2000.modelspace()
    dimline = msp.add_linear_dim(
        base=(3, 2, 0),
        ext1=(0, 0, 0),
        ext2=(3, 0, 0),

    )
    assert dimline.dxf.dimstyle == 'EZDXF'

    msp.render_dimension(dimline)
    block_name = dimline.dxf.geometry
    assert block_name.startswith('*D')

    block = dxf2000.blocks.get(block_name)
    assert len(list(block.query('TEXT'))) == 1
    assert len(list(block.query('LINE'))) == 5  # dimension line + 2 extension lines
    assert len(list(block.query('POINT'))) == 3  # def points


def test_dimstyle_override(dxf2000):
    msp = dxf2000.modelspace()
    dimline = msp.add_linear_dim(
        base=(3, 2, 0),
        ext1=(0, 0, 0),
        ext2=(3, 0, 0),
        dxfattribs={
            'dimstyle': 'EZDXF',
        }
    )
    assert dimline.dxf.dimstyle == 'EZDXF'
    if 'TEST' not in dxf2000.styles:  # text style must exists
        dxf2000.styles.new('TEST')

    preset = {
        'dimtxsty': 'TEST',  # virtual attribute - 'dimtxsty_handle' stores the text style handle
        'dimexe': 0.777,
    }
    dimstyle = dimline.dimstyle_override(preset)
    assert dimstyle['dimtxsty'] == 'TEST'
    assert dimstyle['dimexe'] == 0.777

    with pytest.raises(DXFAttributeError):
        _ = dimstyle['invalid']

    with pytest.raises(DXFAttributeError):
        dimstyle.update({'invalid': 0})

    dstyle_orig = dimstyle.get_dstyle_dict()
    assert len(dstyle_orig) == 0

    dimstyle.commit()
    dstyle = dimstyle.get_dstyle_dict()
    assert dstyle['dimexe'] == 0.777
    assert 'dimtxsty' not in dstyle, 'do not store "dimtxsty" in dstyle, because virtual attribute'
    assert 'dimtxsty_handle' in dstyle, 'expected handle of text style'
    assert dstyle['dimtxsty_handle'] == dxf2000.styles.get('TEST').dxf.handle


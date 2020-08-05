# Copyright (c) 2016-2020, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.entities.image import ImageDef, Image


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new('R2000')


@pytest.fixture(scope='module')
def image_def(doc):
    return ImageDef.from_text(IMAGE_DEF, doc)


def test_set_raster_variables():
    doc = ezdxf.new('R2000')
    assert 'ACAD_IMAGE_VARS' not in doc.rootdict
    doc.set_raster_variables(frame=0, quality=1, units='m')
    raster_vars = doc.rootdict['ACAD_IMAGE_VARS']
    assert raster_vars.dxftype() == 'RASTERVARIABLES'
    assert raster_vars.dxf.frame == 0
    assert raster_vars.dxf.quality == 1
    assert raster_vars.dxf.units == 3  # m

    assert 'ACAD_IMAGE_VARS' in doc.rootdict
    doc.set_raster_variables(frame=1, quality=0, units='km')
    raster_vars = doc.rootdict['ACAD_IMAGE_VARS']
    assert raster_vars.dxftype() == 'RASTERVARIABLES'
    assert raster_vars.dxf.frame == 1
    assert raster_vars.dxf.quality == 0
    assert raster_vars.dxf.units == 4  # km


def test_imagedef_attribs(image_def):
    assert 'IMAGEDEF' == image_def.dxftype()
    assert 0 == image_def.dxf.class_version
    assert 'mycat.jpg' == image_def.dxf.filename
    assert (640., 360.) == image_def.dxf.image_size
    assert (.01, .01) == image_def.dxf.pixel_size
    assert 1 == image_def.dxf.loaded
    assert 0 == image_def.dxf.resolution_units


@pytest.fixture(scope='module')
def image(doc):
    return Image.from_text(IMAGE, doc)


def test_image_dxf_attribs(image):
    assert 'IMAGE' == image.dxftype()
    assert (0., 0., 0.) == image.dxf.insert
    assert (.01, 0., 0.) == image.dxf.u_pixel
    assert (0., .01, 0.) == image.dxf.v_pixel
    assert (640., 360.) == image.dxf.image_size
    assert 7 == image.dxf.flags
    assert 0 == image.dxf.clipping
    assert 50 == image.dxf.brightness
    assert 50 == image.dxf.contrast
    assert 0 == image.dxf.fade
    assert 'DEAD' == image.dxf.image_def_reactor_handle
    assert 1 == image.dxf.clipping_boundary_type
    assert 2 == image.dxf.count_boundary_points
    x, y = image.dxf.image_size[:2]
    assert [(-.5, -.5), (x-.5, y-.5)] == image.boundary_path


def test_boundary_path(image):
    assert [(-.5, -.5), (639.5, 359.5)] == image.boundary_path


def test_reset_boundary_path(image):
    image.reset_boundary_path()
    assert 2 == image.dxf.count_boundary_points
    assert image.get_flag_state(image.USE_CLIPPING_BOUNDARY) is False
    assert image.dxf.clipping == 0
    x, y = image.dxf.image_size[:2]
    assert [(-.5, -.5), (x-.5, y-.5)] == image.boundary_path


def test_set_boundary_path(image):
    image.set_boundary_path([(0, 0), (640, 180), (320, 360)])  # 3 vertices triangle
    assert 4 == image.dxf.count_boundary_points
    assert 2 == image.dxf.clipping_boundary_type
    # auto close
    assert [(0, 0), (640, 180), (320, 360), (0, 0)] == image.boundary_path
    assert image.dxf.clipping == 1
    assert image.get_flag_state(image.USE_CLIPPING_BOUNDARY) is True


@pytest.fixture
def new_doc():
    return ezdxf.new('R2000')


def test_new_image_def(new_doc):
    rootdict = new_doc.rootdict
    assert 'ACAD_IMAGE_DICT' not in rootdict
    imagedef = new_doc.add_image_def('mycat.jpg', size_in_pixel=(640, 360))

    # check internals image_def_owner -> ACAD_IMAGE_DICT
    image_dict = rootdict['ACAD_IMAGE_DICT']
    assert imagedef.dxf.owner == image_dict.dxf.handle

    assert 'mycat.jpg' == imagedef.dxf.filename
    assert (640., 360.) == imagedef.dxf.image_size

    # rest are default values
    assert (.01, .01) == imagedef.dxf.pixel_size
    assert 1 == imagedef.dxf.loaded
    assert 0 == imagedef.dxf.resolution_units


def test_create_and_delete_image(new_doc):
    msp = new_doc.modelspace()
    image_def = new_doc.add_image_def('mycat.jpg', size_in_pixel=(640, 360))
    image = msp.add_image(image_def=image_def, insert=(0, 0), size_in_units=(3.2, 1.8))
    assert (0, 0, 0) == image.dxf.insert
    assert (0.005, 0, 0) == image.dxf.u_pixel
    assert (0., 0.005, 0) == image.dxf.v_pixel
    assert (640, 360) == image.dxf.image_size
    assert image_def.dxf.handle == image.dxf.image_def_handle
    assert 3 == image.dxf.flags
    assert 0 == image.dxf.clipping
    assert 2 == image.dxf.count_boundary_points
    x, y = image.dxf.image_size.vec2
    assert [(-.5, -.5), (x-.5, y-.5)] == image.boundary_path

    image_def2 = image.get_image_def()
    assert image_def.dxf.handle, image_def2.dxf.handle

    # does image def reactor exists
    reactor_handle = image.dxf.image_def_reactor_handle
    assert reactor_handle in new_doc.objects
    reactor = new_doc.entitydb[reactor_handle]
    assert image.dxf.handle == reactor.dxf.owner, "IMAGE is not owner of IMAGEDEF_REACTOR"
    assert image.dxf.handle == reactor.dxf.image_handle, "IMAGEDEF_REACTOR does not point to IMAGE"

    assert reactor_handle in image_def2.get_reactors(), "Reactor handle not in IMAGE_DEF reactors."

    # delete image
    msp.delete_entity(image)
    assert reactor.is_alive is False
    assert reactor_handle not in new_doc.objects, "IMAGEDEF_REACTOR not deleted for objects section"
    assert reactor_handle not in new_doc.entitydb, "IMAGEDEF_REACTOR not deleted for entity database"
    assert reactor_handle not in image_def2.get_reactors(), "Reactor handle not deleted from IMAGE_DEF reactors."


def test_create_and_copy_image(new_doc):
    msp = new_doc.modelspace()
    entitydb = new_doc.entitydb
    image_def = new_doc.add_image_def('mycat.jpg', size_in_pixel=(640, 360))
    image = msp.add_image(image_def=image_def, insert=(0, 0), size_in_units=(3.2, 1.8))
    reactor_handle = image.dxf.image_def_reactor_handle
    copy = image.copy()
    entitydb.add(copy)
    msp.add_entity(copy)
    reactor_handle_of_copy = copy.dxf.image_def_reactor_handle

    # Each image has it's own ImageDefReactor
    assert reactor_handle in entitydb
    assert reactor_handle_of_copy in entitydb
    assert reactor_handle != reactor_handle_of_copy

    # Both images are linked to ImageDef
    assert reactor_handle in image_def.reactors
    assert reactor_handle_of_copy in image_def.reactors


def test_generic_wipeout(doc):
    msp = doc.modelspace()
    wipeout = msp.new_entity('WIPEOUT', {'insert': (0, 0, 0)})
    assert wipeout.dxftype() == 'WIPEOUT'
    assert wipeout.dxf.insert == (0, 0, 0)

    doc.set_wipeout_variables(frame=1)
    wipeout_variables = doc.rootdict['ACAD_WIPEOUT_VARS']
    assert wipeout_variables.dxf.frame == 1


IMAGE_DEF = """  0
IMAGEDEF
  5
DEAD
330
DEAD
100
AcDbRasterImageDef
 90
        0
  1
mycat.jpg
 10
640.0
 20
360.0
 11
0.01
 21
0.01
280
     1
281
     0
"""

IMAGE = """  0
IMAGE
  5
1DF
330
1F
100
AcDbEntity
  8
0
100
AcDbRasterImage
 90
        0
 10
0.0
 20
0.0
 30
0.0
 11
0.01
 21
0.0
 31
0.0
 12
0.0
 22
0.01
 32
0.0
 13
640.0
 23
360.0
340
DEAD
 70
     7
280
     0
281
    50
282
    50
283
     0
360
DEAD
 71
     1
 91
        2
 14
-.5
 24
-.5
 14
639.5
 24
359.5
"""
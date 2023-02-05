# Copyright (c) 2016-2023, Manfred Moitzi
# License: MIT License
import pytest
import logging

import ezdxf
from ezdxf.entities.image import ImageDef, Image

logger = logging.getLogger("ezdxf")


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new("R2000")


@pytest.fixture(scope="module")
def image_def(doc):
    return ImageDef.from_text(IMAGE_DEF, doc)


def test_set_raster_variables():
    doc = ezdxf.new("R2000")
    assert "ACAD_IMAGE_VARS" not in doc.rootdict
    doc.set_raster_variables(frame=0, quality=1, units="m")
    raster_vars = doc.rootdict["ACAD_IMAGE_VARS"]
    assert raster_vars.dxftype() == "RASTERVARIABLES"
    assert raster_vars.dxf.frame == 0
    assert raster_vars.dxf.quality == 1
    assert raster_vars.dxf.units == 3  # m

    assert "ACAD_IMAGE_VARS" in doc.rootdict
    doc.set_raster_variables(frame=1, quality=0, units="km")
    raster_vars = doc.rootdict["ACAD_IMAGE_VARS"]
    assert raster_vars.dxftype() == "RASTERVARIABLES"
    assert raster_vars.dxf.frame == 1
    assert raster_vars.dxf.quality == 0
    assert raster_vars.dxf.units == 4  # km


def test_imagedef_attribs(image_def):
    assert image_def.dxftype() == "IMAGEDEF"
    assert image_def.dxf.class_version == 0
    assert image_def.dxf.filename == "mycat.jpg"
    assert image_def.dxf.image_size.isclose((640.0, 360.0))
    assert image_def.dxf.pixel_size.isclose((0.01, 0.01))
    assert image_def.dxf.loaded == 1
    assert image_def.dxf.resolution_units == 0


@pytest.fixture(scope="module")
def image(doc):
    return Image.from_text(IMAGE, doc)


def test_image_dxf_attribs(image):
    assert "IMAGE" == image.dxftype()
    assert image.dxf.insert.isclose((0.0, 0.0, 0.0))
    assert image.dxf.u_pixel.isclose((0.01, 0.0, 0.0))
    assert image.dxf.v_pixel.isclose((0.0, 0.01, 0.0))
    assert image.dxf.image_size.isclose((640.0, 360.0))
    assert image.dxf.flags == 7
    assert image.dxf.clipping == 0
    assert image.dxf.brightness == 50
    assert image.dxf.contrast == 50
    assert image.dxf.fade == 0
    assert image.dxf.image_def_reactor_handle == "DEAD"
    assert image.dxf.clipping_boundary_type == 1
    assert image.dxf.count_boundary_points == 2
    x, y, *_ = image.dxf.image_size
    assert image.boundary_path == [(-0.5, -0.5), (x - 0.5, y - 0.5)]


def test_boundary_path(image):
    assert [(-0.5, -0.5), (639.5, 359.5)] == image.boundary_path


def test_reset_boundary_path(image):
    image.reset_boundary_path()
    assert 2 == image.dxf.count_boundary_points
    assert image.get_flag_state(image.USE_CLIPPING_BOUNDARY) is False
    assert image.dxf.clipping == 0
    x, y, *_ = image.dxf.image_size
    assert [(-0.5, -0.5), (x - 0.5, y - 0.5)] == image.boundary_path


def test_set_boundary_path(image):
    image.set_boundary_path(
        [(0, 0), (640, 180), (320, 360)]
    )  # 3 vertices triangle
    assert image.dxf.count_boundary_points == 4
    assert image.dxf.clipping_boundary_type == 2
    # auto close
    assert [(0, 0), (640, 180), (320, 360), (0, 0)] == image.boundary_path
    assert image.dxf.clipping == 1
    assert image.get_flag_state(image.USE_CLIPPING_BOUNDARY) is True


def test_post_load_hook_creates_image_def_reactor(doc):
    image_def = doc.add_image_def("test.jpg", (1, 1))
    msp = doc.modelspace()
    image = msp.add_image(image_def, (0, 0), (1, 1))
    old_reactor_handle = image.dxf.image_def_reactor_handle

    # Hack to unlink Image from ImageDefReactor!
    image.dxf.image_def_reactor_handle = None
    command = image.post_load_hook(doc)

    assert command is not None, "must return a fixer as callable object"
    command()  # execute fix
    handle = image.dxf.image_def_reactor_handle
    reactor = doc.entitydb[handle]

    assert handle is not None, "must have an ImageDefReactor"
    assert handle != old_reactor_handle, "must have a new ImageDefReactor"
    assert (
        handle in image_def.reactors
    ), "ImageDef must be linked to ImageDefReactor"
    assert (
        reactor.dxf.image_handle == image.dxf.handle
    ), "ImageDefReactor must be linked to Image"


def test_exception_while_fixing_image_def_reactor(doc):
    from io import StringIO

    stream = StringIO()
    logging_handler = logging.StreamHandler(stream)
    logger.addHandler(logging_handler)

    image_def = doc.add_image_def("test.jpg", (1, 1))
    msp = doc.modelspace()
    image = msp.add_image(image_def, (0, 0), (1, 1))

    # Hack to unlink Image from ImageDefReactor!
    image.dxf.image_def_reactor_handle = None
    command = image.post_load_hook(doc)

    # Sabotage execution:
    image.doc = None
    try:
        command()
        msg = stream.getvalue()
    finally:
        logger.removeHandler(logging_handler)

    assert image.is_alive is False, "Exception while fixing must destroy IMAGE"
    assert "AttributeError" in msg
    # Example logging message:
    # ------------------------
    # An exception occurred while executing fixing command for IMAGE(#30), destroying entity.
    # Traceback (most recent call last):
    #   File "D:\Source\ezdxf.git\src\ezdxf\entities\image.py", line 173, in _fix_missing_image_def_reactor
    #     self._create_image_def_reactor()
    #   File "D:\Source\ezdxf.git\src\ezdxf\entities\image.py", line 186, in _create_image_def_reactor
    #     image_def_reactor = self.doc.objects.add_image_def_reactor(
    # AttributeError: 'NoneType' object has no attribute 'objects'


def test_post_load_hook_destroys_image_without_valid_image_def(doc):
    image_def = doc.add_image_def("test.jpg", (1, 1))
    msp = doc.modelspace()
    image = msp.add_image(image_def, (0, 0), (1, 1))

    # Hack to unlink Image from ImageDef!
    image.dxf.image_def_handle = None
    image.post_load_hook(doc)

    assert (
        image.is_alive is False
    ), "Image with invalid ImageDef must be destroyed"


@pytest.fixture
def new_doc():
    return ezdxf.new("R2000")


def test_new_image_def(new_doc):
    rootdict = new_doc.rootdict
    assert "ACAD_IMAGE_DICT" not in rootdict
    imagedef = new_doc.add_image_def("mycat.jpg", size_in_pixel=(640, 360))

    # check internals image_def_owner -> ACAD_IMAGE_DICT
    image_dict = rootdict["ACAD_IMAGE_DICT"]
    assert imagedef.dxf.owner == image_dict.dxf.handle

    assert imagedef.dxf.filename == "mycat.jpg"
    assert imagedef.dxf.image_size.isclose((640.0, 360.0))

    # rest are default values
    assert imagedef.dxf.pixel_size.isclose((0.01, 0.01))
    assert imagedef.dxf.loaded == 1
    assert imagedef.dxf.resolution_units == 0


def test_create_and_delete_image(new_doc):
    msp = new_doc.modelspace()
    image_def = new_doc.add_image_def("mycat.jpg", size_in_pixel=(640, 360))
    image = msp.add_image(
        image_def=image_def, insert=(0, 0), size_in_units=(3.2, 1.8)
    )
    assert image.dxf.insert.isclose((0, 0, 0))
    assert image.dxf.u_pixel.isclose((0.005, 0, 0))
    assert image.dxf.v_pixel.isclose((0.0, 0.005, 0))
    assert image.dxf.image_size.isclose((640, 360))
    assert image_def.dxf.handle == image.dxf.image_def_handle
    assert image.dxf.flags == 3
    assert image.dxf.clipping == 0
    assert image.dxf.count_boundary_points == 2
    x, y = image.dxf.image_size.vec2
    assert image.boundary_path == [(-0.5, -0.5), (x - 0.5, y - 0.5)]

    image_def2 = image.image_def
    assert image_def.dxf.handle, image_def2.dxf.handle

    # does image def reactor exists
    reactor_handle = image.dxf.image_def_reactor_handle
    assert reactor_handle in new_doc.objects
    reactor = new_doc.entitydb[reactor_handle]
    assert (
        image.dxf.handle == reactor.dxf.owner
    ), "IMAGE is not owner of IMAGEDEF_REACTOR"
    assert (
        image.dxf.handle == reactor.dxf.image_handle
    ), "IMAGEDEF_REACTOR does not point to IMAGE"

    assert (
        reactor_handle in image_def2.get_reactors()
    ), "Reactor handle not in IMAGE_DEF reactors."

    # delete image
    msp.delete_entity(image)
    new_doc.entitydb.purge()
    assert reactor.is_alive is False
    assert (
        reactor_handle not in new_doc.objects
    ), "IMAGEDEF_REACTOR not deleted for objects section"
    assert (
        reactor_handle not in new_doc.entitydb
    ), "IMAGEDEF_REACTOR not deleted for entity database"
    assert (
        reactor_handle not in image_def2.get_reactors()
    ), "Reactor handle not deleted from IMAGE_DEF reactors."


def create_image(doc):
    msp = doc.modelspace()
    image_def = doc.add_image_def("mycat.jpg", size_in_pixel=(640, 360))
    image = msp.add_image(
        image_def=image_def, insert=(0, 0), size_in_units=(3.2, 1.8)
    )
    image.boundary_path = [(0, 0), (1, 1), (2, 2), (3, 3)]
    return image_def, image


def test_create_and_copy_image(new_doc):
    msp = new_doc.modelspace()
    entitydb = new_doc.entitydb
    image_def, image = create_image(new_doc)
    reactor_handle = image.dxf.image_def_reactor_handle
    copy = image.copy()
    msp.add_entity(copy)
    reactor_handle_of_copy = copy.dxf.image_def_reactor_handle

    # Each image has it's own ImageDefReactor
    assert (
        reactor_handle in entitydb
    ), "ImageDefReactor of source image not stored in EntityDB."
    assert (
        reactor_handle_of_copy in entitydb
    ), "ImageDefReactor of copy not stored in EntityDB."
    assert (
        reactor_handle != reactor_handle_of_copy
    ), "Source image and copy must not have the same ImageDefReactor."

    # Both images are linked to same ImageDef object.
    assert (
        reactor_handle in image_def.reactors
    ), "ImageDefReactor of source image not stored in ImageDef object."
    assert (
        reactor_handle_of_copy in image_def.reactors
    ), "ImageDefReactor of copied image not stored in ImageDef object."
    assert (
        image.boundary_path == copy.boundary_path
    ), "Invalid copy of boundary path."
    assert (
        image.boundary_path is not copy.boundary_path
    ), "Copied image needs an independent copy of the boundary path."


def test_moving_to_another_layout(new_doc):
    msp = new_doc.modelspace()
    image_def, image = create_image(new_doc)
    old_reactor_handle = image.dxf.image_def_reactor_handle
    blk = new_doc.blocks.new("TEST")
    msp.move_to_layout(image, blk)
    # Moving between layouts should not alter the ImageDefReactor
    assert (
        image.dxf.image_def_reactor_handle == old_reactor_handle
    ), "Moved image got a new ImageDefReactor without necessity."


def test_copying_to_another_layout(new_doc):
    image_def, image = create_image(new_doc)
    old_reactor_handle = image.dxf.image_def_reactor_handle
    blk = new_doc.blocks.new("TEST")
    copy = new_doc.entitydb.duplicate_entity(image)

    # duplicate_entity() binds entity to document and triggers the
    # post_bind_hook() to create a new ImageDefReactor:
    copy_reactor_handle = copy.dxf.image_def_reactor_handle
    assert (
        copy_reactor_handle != "0"
    ), "Image copy did not get a new ImageDefReactor"
    assert (
        copy_reactor_handle != old_reactor_handle
    ), "Image copy has the same ImageDefReactor as the source image."

    blk.add_entity(copy)

    # unlinking an image, does not remove the ImageDefReactor
    blk.unlink_entity(copy)
    assert (
        copy.dxf.image_def_reactor_handle == copy_reactor_handle
    ), "Removed ImageDefReactor from unlinked image."

    # Keep reactor if adding an image with existing ImageDefReactor
    blk.add_entity(copy)
    assert (
        copy.dxf.image_def_reactor_handle == copy_reactor_handle
    ), "Relinked image got new ImageDefReactor without necessity."


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

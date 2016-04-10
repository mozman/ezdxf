# Purpose: support for the Ac1015 IMAGE entity
# Created: 07.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..dxfentity import DXFEntity

from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.tags import DXFTag, Tags
from ..lldxf.classifiedtags import ClassifiedTags
from ..lldxf import const

_IMAGE_TPL = """ 0
IMAGE
 5
0
330
0
100
AcDbEntity
  8
0
100
AcDbRasterImage
 90
0.0
 10
0
 20
0.0
 30
0.0
 11
0.0
 21
0.0
 31
0.0
 12
0.0
 22
0.0
 32
0.0
 13
640
 23
320
340
0
 70
     3
280
     0
281
    50
282
    50
283
     0
360
0
 71
  1
 91
  2
"""

image_subclass = DefSubclass('AcDbRasterImage', {
    'insert': DXFAttr(10, xtype='Point3D'),
    'u_pixel': DXFAttr(11, xtype='Point3D'),  # U-vector of a single pixel (points along the visual bottom of the image, starting at the insertion point)
    'v_pixel': DXFAttr(12, xtype='Point3D'),  # V-vector of a single pixel (points along the visual left side of the image, starting at the insertion point)
    'image_size': DXFAttr(13, xtype='Point2D'),  # Image size in pixels
    'image_def': DXFAttr(340),  # Hard reference to image def object
    'flags': DXFAttr(70, default=3),  # Image display properties:
    # 1 = Show image
    # 2 = Show image when not aligned with screen
    # 4 = Use clipping boundary
    # 8 = Transparency is on
    'clipping': DXFAttr(280, default=0),  # Clipping state: 0 = Off; 1 = On
    'brightness': DXFAttr(281, default=50),  # Brightness value (0-100; default = 50)
    'contrast': DXFAttr(282, default=50),  # Contrast value (0-100; default = 50)
    'fade': DXFAttr(283, default=0),  # Fade value (0-100; default = 0)
    'image_def_reactor': DXFAttr(360),  # Hard reference to image def reactor object, not required by AutoCAD
    'clipping_boundary_type': DXFAttr(71, default=1),  # Clipping boundary type. 1 = Rectangular; 2 = Polygonal
    'count_boundary_points': DXFAttr(91),  # Number of clip boundary vertices that follow
    # boundary path coordinates are pixel coordinates NOT drawing units
})


class Image(ModernGraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_IMAGE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, image_subclass)

    def post_new_hook(self):
        self.reset_boundary_path()

    def set_boundary_path(self, vertices):
        vertices = list(vertices)
        self._set_path_tags(vertices)
        self.dxf.flags |= 4  # use clipping boundary
        self.dxf.clipping_boundary_type = 1 if len(vertices) < 3 else 2

    def _set_path_tags(self, vertices):
        boundary = [DXFTag(14, value) for value in vertices]
        subclasstags = Tags(tag for tag in self.tags.subclasses[2] if tag.code != 14)
        subclasstags.extend(boundary)
        self.tags.subclasses[2] = subclasstags
        self.dxf.count_boundary_points = len(vertices)

    def reset_boundary_path(self):
        self._set_path_tags([(0., 0.), self.dxf.image_size])
        self.dxf.flags &= (1 + 2 + 8)  # do not use boundary
        self.dxf.clipping = 0

    def get_boundary_path(self):
        image_subclass = self.tags.subclasses[2]
        return [tag.value for tag in image_subclass if tag.code == 14]

    def get_image_def(self):
        return self.dxffactory.wrap_handle(self.dxf.image_def)

    def destroy(self):
        super(Image, self).destroy()
        # remove rectors
        image_def = self.get_image_def()
        reactor_handle = self.dxf.image_def_reactor
        image_def.remove_reactor_handle(reactor_handle)
        if self.drawing is not None:
            reactor = self.dxffactory.wrap_handle(reactor_handle)
            self.drawing.objects.delete_entity(reactor)



_IMAGE_DEF_TPL = """  0
IMAGEDEF
  5
0
330
0
102
{ACAD_REACTORS
102
}
100
AcDbRasterImageDef
 90
  0
  1
path/filename.jpg
 10
640
 20
480
 11
0.01
 21
0.01
280
  1
281
  0
"""

image_def_subclass = DefSubclass('AcDbRasterImageDef', {
    'class_version': DXFAttr(90),  # class version
    'filename': DXFAttr(1),  # File name of image
    'image_size': DXFAttr(10, xtype='Point2D'),  # image size in pixels
    'pixel_size': DXFAttr(11, xtype='Point2D'),  # Default size of one pixel in AutoCAD units
    'loaded': DXFAttr(280, default=1),
    'resolution_units': DXFAttr(281, default=0),  # Resolution units. 0 = No units; 2 = Centimeters; 5 = Inch
})


# IMAGEDEF - requires entry in objects table ACAD_IMAGE_DICT, ACAD_IMAGE_DICT exists not by default
class ImageDef(DXFEntity):
    TEMPLATE = ClassifiedTags.from_text(_IMAGE_DEF_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, image_def_subclass)

_IMAGE_DEF_REACTOR_TPL = """  0
IMAGEDEF_REACTOR
  5
0
330
0
100
AcDbRasterImageDefReactor
 90
2
330
0
"""


# IMAGEDEF_REACTOR is not required by AutoCAD
# owner -> IMAGE
class ImageDefReactor(DXFEntity):
    TEMPLATE = ClassifiedTags.from_text(_IMAGE_DEF_REACTOR_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbRasterImageDef', {
        'image': DXFAttr(330),  # handle to image
    }))

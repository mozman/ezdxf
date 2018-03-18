# Purpose: support for the Ac1015 IMAGE entity
# Created: 07.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..dxfentity import DXFEntity

from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.tags import DXFTag, Tags
from ..lldxf.extendedtags import ExtendedTags
from ezdxf.algebra import Vector


_IMAGE_CLS = """  0
CLASS
1
IMAGE
2
AcDbRasterImage
3
ISM
90
2175
91
0
280
0
281
1
"""
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
0
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
    'clipping': DXFAttr(280, default=0),  # Clipping state: 0 = Off; 1 = On
    'brightness': DXFAttr(281, default=50),  # Brightness value (0-100; default = 50)
    'contrast': DXFAttr(282, default=50),  # Contrast value (0-100; default = 50)
    'fade': DXFAttr(283, default=0),  # Fade value (0-100; default = 0)
    'image_def_reactor': DXFAttr(360),  # Hard reference to image def reactor object, not required by AutoCAD
    'clipping_boundary_type': DXFAttr(71, default=1),  # Clipping boundary type. 1 = Rectangular; 2 = Polygonal
    'count_boundary_points': DXFAttr(91),  # Number of clip boundary vertices that follow
    'clip_mode': DXFAttr(290, dxfversion='AC1024'),  # 0 = outside, 1 = inside mode
    # boundary path coordinates are pixel coordinates NOT drawing units
})


class Image(ModernGraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_IMAGE_TPL)
    CLASS = ExtendedTags.from_text(_IMAGE_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, image_subclass)
    # flags for IMAGE
    SHOW_IMAGE = 1
    SHOW_IMAGE_WHEN_NOT_ALIGNED = 2
    USE_CLIPPING_BOUNDARY = 4
    USE_TRANSPARENCY = 8

    def post_new_hook(self):
        self.reset_boundary_path()

    def set_boundary_path(self, vertices):
        vertices = list(vertices)
        if len(vertices) > 2 and vertices[-1] != vertices[0]:
            vertices.append(vertices[0])  # close path, else AutoCAD crashes
        self._set_path_tags(vertices)
        self.set_flag_state(self.USE_CLIPPING_BOUNDARY, state=True)
        self.dxf.clipping = 1
        self.dxf.clipping_boundary_type = 1 if len(vertices) < 3 else 2

    def _set_path_tags(self, vertices):
        boundary = [DXFTag(14, value) for value in vertices]
        subclasstags = Tags(tag for tag in self.tags.subclasses[2] if tag.code != 14)
        subclasstags.extend(boundary)
        self.tags.subclasses[2] = subclasstags
        self.dxf.count_boundary_points = len(vertices)

    def reset_boundary_path(self):
        lower_left_corner = (-.5, -.5)
        upper_right_corner = Vector(self.dxf.image_size) + lower_left_corner
        self._set_path_tags([lower_left_corner, upper_right_corner.tup2])
        self.set_flag_state(Image.USE_CLIPPING_BOUNDARY, state=False)
        self.dxf.clipping = 0
        self.dxf.clipping_boundary_type = 1

    def get_boundary_path(self):
        image_subclass = self.tags.subclasses[2]
        return [tag.value for tag in image_subclass if tag.code == 14]

    def get_image_def(self):
        return self.dxffactory.wrap_handle(self.dxf.image_def)

    def destroy(self):
        super(Image, self).destroy()
        # remove rectors
        image_def = self.get_image_def()
        reactor_handle = self.get_dxf_attrib('image_def_reactor', None)
        if reactor_handle is None:
            return
        image_def.remove_reactor_handle(reactor_handle)
        if self.drawing is not None:
            reactor = self.dxffactory.wrap_handle(reactor_handle)
            self.drawing.objects.delete_entity(reactor)

_IMAGE_DEF_CLS = """  0
CLASS
1
IMAGEDEF
2
AcDbRasterImageDef
3
ISM
90
0
91
0
280
0
281
0
"""

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
    TEMPLATE = ExtendedTags.from_text(_IMAGE_DEF_TPL)
    CLASS = ExtendedTags.from_text(_IMAGE_DEF_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, image_def_subclass)


_IMAGE_DEF_REACTOR_CLS = """  0
CLASS
  1
IMAGEDEF_REACTOR
  2
AcDbRasterImageDefReactor
  3
ISM
 90
1
 91
0
280
0
281
0
"""
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
    TEMPLATE = ExtendedTags.from_text(_IMAGE_DEF_REACTOR_TPL)
    CLASS = ExtendedTags.from_text(_IMAGE_DEF_REACTOR_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbRasterImageDef', {
        'image': DXFAttr(330),  # handle to image
    }))


_RASTER_VARIABLES_CLS = """  0
CLASS
1
RASTERVARIABLES
2
AcDbRasterVariables
3
ISM
90
0
91
0
280
0
281
0
"""
_RASTER_VARIABLES_TPL = """  0
RASTERVARIABLES
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbRasterVariables
90
0
70
0
71
1
72
3
"""


class RasterVariables(DXFEntity):
    TEMPLATE = ExtendedTags.from_text(_RASTER_VARIABLES_TPL)
    CLASS = ExtendedTags.from_text(_RASTER_VARIABLES_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbRasterVariables', {
            'version': DXFAttr(90, default=0),
            'frame': DXFAttr(70, default=0),  # 0 = no frame; 1= show frame
            'quality': DXFAttr(71, default=1),  # 0=draft; 1=high
            'units': DXFAttr(72, default=3),  # 0 = None; 1 = mm; 2 = cm 3 = m; 4 = km; 5 = in 6 = ft; 7 = yd; 8 = mi
        }),
    )

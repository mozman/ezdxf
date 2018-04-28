# Created: 03.04.2016
# Copyright (C) 2016-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..dxfentity import DXFEntity
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.types import DXFVertex
from ..lldxf.tags import Tags
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf import const

_PDFUNDERLAY_CLS = """0
CLASS
1
PDFUNDERLAY
2
AcDbPdfReference
3
ObjectDBX Classes
90
4095
91
0
280
0
281
1
"""

_PDFUNDERLAY_TPL = """0
PDFUNDERLAY
5
0
330
0
100
AcDbEntity
8
0
100
AcDbUnderlayReference
340
0
10
0.0
20
0.0
30
0.0
41
1.0
42
1.0
43
1.0
50
0.0
280
2
281
100
282
0
"""

underlay_subclass = DefSubclass('AcDbUnderlayReference', {
    'underlay_def': DXFAttr(340),  # Hard reference to underlay definition object
    'insert': DXFAttr(10, xtype='Point3D'),
    'scale_x': DXFAttr(41, default=1.),  # scale x factor
    'scale_y': DXFAttr(42, default=1.),  # scale y factor
    'scale_z': DXFAttr(43, default=1.),  # scale z factor
    'rotation': DXFAttr(50, default=0.),  # rotation angle in degrees?
    'extrusion': DXFAttr(210, xtype='Point3D'),
    'flags': DXFAttr(280, default=0),  # Underlay display properties:
    # 1 = Clipping is on
    # 2 = Underlay is on
    # 4 = Monochrome
    # 8 = Adjust for background
    'contrast': DXFAttr(281, default=100),  # Contrast value (20-100; default = 100)
    'fade': DXFAttr(282, default=0),  # Fade value (0-80; default = 0)
})


class PdfUnderlay(ModernGraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_PDFUNDERLAY_TPL)
    CLASS = ExtendedTags.from_text(_PDFUNDERLAY_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, underlay_subclass)

    @property
    def clipping(self):
        return bool(self.dxf.flags & const.UNDERLAY_CLIPPING)

    @clipping.setter
    def clipping(self, state):
        self.set_flags(const.UNDERLAY_CLIPPING, state)

    @property
    def on(self):
        return bool(self.dxf.flags & const.UNDERLAY_ON)

    @on.setter
    def on(self, state):
        self.set_flags(const.UNDERLAY_ON, state)

    @property
    def monochrome(self):
        return bool(self.dxf.flags & const.UNDERLAY_MONOCHROME)

    @monochrome.setter
    def monochrome(self, state):
        self.set_flags(const.UNDERLAY_MONOCHROME, state)

    @property
    def adjust_for_background(self):
        return bool(self.dxf.flags & const.UNDERLAY_ADJUST_FOR_BG)

    @adjust_for_background.setter
    def adjust_for_background(self, state):
        self.set_flags(const.UNDERLAY_ADJUST_FOR_BG, state)

    @property
    def scale(self):
        return self.dxf.scale_x, self.dxf.scale_y, self.dxf.scale_z

    @scale.setter
    def scale(self, scale):
        if type(scale) in (float, int):
            x, y, z = scale, scale, scale
        else:
            x, y, z = scale
        self.dxf.scale_x = x
        self.dxf.scale_y = y
        self.dxf.scale_z = z

    def set_flags(self, flag, state=True):
        if state:
            self.dxf.flags = self.dxf.flags | flag
        else:
            self.dxf.flags = self.dxf.flags & ~flag

    def set_boundary_path(self, vertices):  # path coordinates as drawing coordinates but unscaled
        vertices = list(vertices)
        self._set_path_tags(vertices)
        self.clipping = bool(len(vertices))

    def _set_path_tags(self, vertices):
        boundary = [DXFVertex(11, value) for value in vertices]
        subclasstags = Tags(tag for tag in self.tags.subclasses[2] if tag.code != 11)  # filter out existing path tags
        subclasstags.extend(boundary)
        self.tags.subclasses[2] = subclasstags

    def reset_boundary_path(self):
        self._set_path_tags([])
        self.clipping = False

    def get_boundary_path(self):
        underlay_subclass = self.tags.subclasses[2]
        return [tag.value for tag in underlay_subclass if tag.code == 11]  # fetch path tags

    def get_underlay_def(self):
        return self.dxffactory.wrap_handle(self.dxf.underlay_def)

    def destroy(self):
        super(PdfUnderlay, self).destroy()
        underlay_def = self.get_underlay_def()
        underlay_def.remove_reactor_handle(self.dxf.handle)


_DWFUNDERLAY_CLS = """0
CLASS
1
DWFUNDERLAY
2
AcDbDwfReference
3
ObjectDBX Classes
90
1153
91
0
280
0
281
1
"""


class DwfUnderlay(PdfUnderlay):
    TEMPLATE = ExtendedTags.from_text(_PDFUNDERLAY_TPL.replace('PDF', 'DWF'))
    CLASS = ExtendedTags.from_text(_DWFUNDERLAY_CLS)


_DGNUNDERLAY_CLS = """0
CLASS
1
DGNUNDERLAY
2
AcDbDgnReference
3
ObjectDBX Classes
90
1153
91
0
280
0
281
1
"""


class DgnUnderlay(PdfUnderlay):
    TEMPLATE = ExtendedTags.from_text(_PDFUNDERLAY_TPL.replace('PDF', 'DGN'))
    CLASS = ExtendedTags.from_text(_DGNUNDERLAY_CLS)


_PDF_DEF_CLS = """0
CLASS
1
PDFDEFINITION
2
AcDbPdfDefinition
3
ObjectDBX Classes
90
1153
91
0
280
0
281
0
"""
# Using reactors in PdfDefinition for well defined UNDERLAYS
_PDF_DEF_TPL = """0
PDFDEFINITION
5
0
102
{ACAD_REACTORS
102
}
330
0
100
AcDbUnderlayDefinition
1
noname.pdf
2
1
"""

underlay_def_subclass = DefSubclass('AcDbUnderlayDefinition', {
    'filename': DXFAttr(1),  # File name of underlay
    'name': DXFAttr(2),  # underlay name - pdf=page number to display; dgn=default; dwf=????
})


# (PDF|DWF|DGN)DEFINITION - requires entry in objects table ACAD_(PDF|DWF|DGN)DEFINITIONS,
# ACAD_(PDF|DWF|DGN)DEFINITIONS do not exist by default
class PdfDefinition(DXFEntity):
    TEMPLATE = ExtendedTags.from_text(_PDF_DEF_TPL)
    CLASS = ExtendedTags.from_text(_PDF_DEF_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, underlay_def_subclass)

    @property
    def entity_name(self):
        return self.dxftype()[:3] + "UNDERLAY"

    def post_new_hook(self):
        self.set_reactors([self.dxf.owner])


_DWF_DEF_CLS = """0
CLASS
1
DWFDEFINITION
2
AcDbDwfDefinition
3
ObjectDBX Classes
90
1153
91
0
280
0
281
0
"""


class DwfDefinition(PdfDefinition):
    TEMPLATE = ExtendedTags.from_text(_PDF_DEF_TPL.replace('PDF', 'DWF'))
    CLASS = ExtendedTags.from_text(_DWF_DEF_CLS)


_DGN_DEF_CLS = """0
CLASS
1
DGNDEFINITION
2
AcDbDgnDefinition
3
ObjectDBX Classes
90
1153
91
0
280
0
281
0
"""


class DgnDefinition(PdfDefinition):
    TEMPLATE = ExtendedTags.from_text(_PDF_DEF_TPL.replace('PDF', 'DGN'))
    CLASS = ExtendedTags.from_text(_DGN_DEF_CLS)

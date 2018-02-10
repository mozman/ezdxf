# Purpose: support for ACIS based 3D entities - BODY, REGION, 3DSOLID
# Created: 24.05.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from contextlib import contextmanager

from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf.types import convert_tags_to_text_lines, convert_text_lines_to_tags
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..tools import crypt

_BODY_TPL = """  0
BODY
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbModelerGeometry
 70
1
"""

modeler_geometry_subclass = DefSubclass('AcDbModelerGeometry', {
    'version': DXFAttr(70, default=1),
})


class Body(ModernGraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_BODY_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, modeler_geometry_subclass)

    def get_acis_data(self):
        modeler_geometry = self.tags.subclasses[2]
        text_lines = convert_tags_to_text_lines(tag for tag in modeler_geometry if tag.code in (1, 3))
        return crypt.decode(text_lines)

    def set_acis_data(self, text_lines):
        def cleanup(lines):
            for line in lines:
                yield line.rstrip().replace('\n', '')

        modeler_geometry = self.tags.subclasses[2]
        # remove existing text
        modeler_geometry[:] = (tag for tag in modeler_geometry if tag.code not in (1, 3))
        modeler_geometry.extend(convert_text_lines_to_tags(crypt.encode(cleanup(text_lines))))

    @contextmanager
    def edit_data(self):
        data = ModelerGeometryData(self)
        yield data
        self.set_acis_data(data.text_lines)


class ModelerGeometryData(object):
    def __init__(self, body):
        self.text_lines = list(body.get_acis_data())

    def __str__(self):
        return "\n".join(self.text_lines)

    def set_text(self, text, sep='\n'):
        self.text_lines = text.split(sep)


class Region(Body):
    TEMPLATE = ExtendedTags.from_text(_BODY_TPL.replace('BODY', 'REGION'))


_3DSOLID_TPL = """  0
3DSOLID
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbModelerGeometry
 70
1
100
AcDb3dSolid
350
0
"""


class Solid3d(Body):
    TEMPLATE = ExtendedTags.from_text(_3DSOLID_TPL)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        entity_subclass,
        modeler_geometry_subclass,
        DefSubclass('AcDb3dSolid', {'history': DXFAttr(350, default=0)})
    )


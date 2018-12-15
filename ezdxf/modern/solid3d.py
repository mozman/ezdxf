# Created: 24.05.2015
# Copyright (c) 2015-2018, Manfred Moitzi
# License: MIT License
from typing import Iterable
from contextlib import contextmanager

from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.tools import crypt

from .graphics import none_subclass, entity_subclass, ModernGraphicEntity

_BODY_TPL = """0
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


def convert_tags_to_text_lines(line_tags: Iterable[DXFTag]) -> Iterable[str]:
    """
    Args:
        line_tags: tags with code 1 or 3, tag with code 3 is the tail of previous line with more than 255 chars.

    Returns: yield strings

    """
    line_tags = iter(line_tags)
    try:
        line = next(line_tags).value  # raises StopIteration
    except StopIteration:
        return
    while True:
        try:
            tag = next(line_tags)
        except StopIteration:
            if line:
                yield line
            return
        if tag.code == 3:
            line += tag.value
            continue
        yield line
        line = tag.value


def convert_text_lines_to_tags(text_lines: Iterable[str]) -> Iterable[DXFTag]:
    for line in text_lines:
        yield DXFTag(1, line[:255])
        if len(line) > 255:
            yield DXFTag(3, line[255:])  # tail (max. 255 chars), what if line > 510 chars???


class Body(ModernGraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_BODY_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, modeler_geometry_subclass)

    def get_acis_data(self) -> Iterable[str]:
        modeler_geometry = self.tags.subclasses[2]
        text_lines = convert_tags_to_text_lines(tag for tag in modeler_geometry if tag.code in (1, 3))
        return crypt.decode(text_lines)

    def set_acis_data(self, text_lines: Iterable[str]) -> None:
        def cleanup(lines):
            for line in lines:
                yield line.rstrip().replace('\n', '')

        modeler_geometry = self.tags.subclasses[2]
        # remove existing text
        modeler_geometry[:] = (tag for tag in modeler_geometry if tag.code not in (1, 3))
        modeler_geometry.extend(convert_text_lines_to_tags(crypt.encode(cleanup(text_lines))))

    @contextmanager
    def edit_data(self) -> 'ModelerGeometryData':
        data = ModelerGeometryData(self)
        yield data
        self.set_acis_data(data.text_lines)


class ModelerGeometryData:
    def __init__(self, body: 'Body'):
        self.text_lines = list(body.get_acis_data())

    def __str__(self) -> str:
        return "\n".join(self.text_lines)

    def set_text(self, text: str, sep: str = '\n') -> None:
        self.text_lines = text.split(sep)


class Region(Body):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_BODY_TPL.replace('BODY', 'REGION'))


_3DSOLID_TPL = """0
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
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_3DSOLID_TPL)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        entity_subclass,
        modeler_geometry_subclass,
        DefSubclass('AcDb3dSolid', {'history': DXFAttr(350, default=0)})
    )

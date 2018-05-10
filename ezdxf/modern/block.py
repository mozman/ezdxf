# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ..legacy import block
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, ModernGraphicEntityExtension, ModernGraphicEntity


_BLOCK_TPL = """0
BLOCK
5
0
330
0
100
AcDbEntity
8
0
100
AcDbBlockBegin
2
BLOCKNAME
3
BLOCKNAME
70
0
10
0.0
20
0.0
30
0.0
1

"""
block_subclass = (
    DefSubclass('AcDbEntity', {'layer': DXFAttr(8, default='0')}),
    DefSubclass('AcDbBlockBegin', {
        'name': DXFAttr(2),
        'name2': DXFAttr(3),
        'description': DXFAttr(4),
        'flags': DXFAttr(70),
        'base_point': DXFAttr(10, xtype='Point2D/3D'),
        'xref_path': DXFAttr(1, default=""),
    })
)


class Block(block.Block, ModernGraphicEntityExtension):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_BLOCK_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, *block_subclass)


_ENDBLOCK_TPL = """0
ENDBLK
5
0
330
0
100
AcDbEntity
8
0
100
AcDbBlockEnd
"""
endblock_subclass = (
    DefSubclass('AcDbEntity', {'layer': DXFAttr(8, default='0')}),
    DefSubclass('AcDbBlockEnd', {}),
)


class EndBlk(ModernGraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_ENDBLOCK_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, *endblock_subclass)


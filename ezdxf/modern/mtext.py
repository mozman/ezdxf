# Purpose: support for the Ac1015 MTEXT entity
# Created: 24.05.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager
import math

from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.tags import DXFTag
from ..lldxf.classifiedtags import ClassifiedTags
from ..lldxf import const
from ..tools import safe_3D_point

_MTEXT_TPL = """ 0
MTEXT
 5
0
330
0
100
AcDbEntity
  8
0
100
AcDbMText
 50
0.0
 40
1.0
 41
1.0
 71
1
 72
5
 73
1
  1

"""

mtext_subclass = DefSubclass('AcDbMText', {
    'insert': DXFAttr(10, xtype='Point3D'),
    'char_height': DXFAttr(40),  # nominal (initial) text height
    'width': DXFAttr(41),  # reference column width
    'attachment_point': DXFAttr(71),
    # 1 = Top left; 2 = Top center; 3 = Top right
    # 4 = Middle left; 5 = Middle center; 6 = Middle right
    # 7 = Bottom left; 8 = Bottom center; 9 = Bottom right
    'flow_direction': DXFAttr(72),
    # 1 = Left to right
    # 3 = Top to bottom
    # 5 = By style (the flow direction is inherited from the associated text style)
    'style': DXFAttr(7, default='STANDARD'),  # text style name
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    'text_direction': DXFAttr(11, xtype='Point3D'),  # x-axis direction vector (in WCS)
    # If *rotation* and *text_direction* are present, *text_direction* wins
    'rect_width': DXFAttr(42),  # Horizontal width of the characters that make up the mtext entity.
    # This value will always be equal to or less than the value of *width*, (read-only, ignored if supplied)
    'rect_height': DXFAttr(43),  # vertical height of the mtext entity (read-only, ignored if supplied)
    'rotation': DXFAttr(50, default=0.0),  # in degrees (circle=360 deg) -  error in DXF reference, which says radians
    'line_spacing_style': DXFAttr(73),  # line spacing style (optional):
    # 1 = At least (taller characters will override)
    # 2 = Exact (taller characters will not override)
    'line_spacing_factor': DXFAttr(44),  # line spacing factor (optional):
    # Percentage of default (3-on-5) line spacing to be applied. Valid values
    # range from 0.25 to 4.00
})


class MText(ModernGraphicEntity):  # MTEXT will be extended in DXF version AC1021 (ACAD 2007)
    TEMPLATE = ClassifiedTags.from_text(_MTEXT_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, mtext_subclass)

    def get_text(self):
        tags = self.tags.get_subclass('AcDbMText')
        tail = ""
        parts = []
        for tag in tags:
            if tag.code == 1:
                tail = tag.value
            if tag.code == 3:
                parts.append(tag.value)
        parts.append(tail)
        return "".join(parts)

    def set_text(self, text):
        tags = self.tags.get_subclass('AcDbMText')
        tags.remove_tags(codes=(1, 3))
        str_chunks = split_string_in_chunks(text, size=250)
        if len(str_chunks) == 0:
            str_chunks.append("")
        while len(str_chunks) > 1:
            tags.append(DXFTag(3, str_chunks.pop(0)))
        tags.append(DXFTag(1, str_chunks[0]))
        return self

    def get_rotation(self):
        try:
            vector = self.dxf.text_direction
        except ValueError:
            rotation = self.get_dxf_attrib('rotation', 0.0)
        else:
            radians = math.atan2(vector[1], vector[0])  # ignores z-axis
            rotation = math.degrees(radians)
        return rotation

    def set_rotation(self, angle):
        del self.dxf.text_direction  # *text_direction* has higher priority than *rotation*, therefore delete it
        self.dxf.rotation = angle
        return self

    def set_location(self, insert, rotation=None, attachment_point=None):
        self.dxf.insert = safe_3D_point(insert)
        if rotation is not None:
            self.set_rotation(rotation)
        if attachment_point is not None:
            self.dxf.attachment_point = attachment_point
        return self

    @contextmanager
    def edit_data(self):
        buffer = MTextData(self.get_text())
        yield buffer
        self.set_text(buffer.text)

    buffer = edit_data  # alias

##################################################
# MTEXT inline codes
# \L	Start underline
# \l	Stop underline
# \O	Start overstrike
# \o	Stop overstrike
# \K	Start strike-through
# \k	Stop strike-through
# \P	New paragraph (new line)
# \pxi	Control codes for bullets, numbered paragraphs and columns
# \X	Paragraph wrap on the dimension line (only in dimensions)
# \Q	Slanting (obliquing) text by angle - e.g. \Q30;
# \H	Text height - e.g. \H3x;
# \W	Text width - e.g. \W0.8x;
# \F	Font selection
#
#     e.g. \Fgdt;o - GDT-tolerance
#     e.g. \Fkroeger|b0|i0|c238|p10 - font Kroeger, non-bold, non-italic, codepage 238, pitch 10
#
# \S	Stacking, fractions
#
#     e.g. \SA^B:
#     A
#     B
#     e.g. \SX/Y:
#     X
#     -
#     Y
#     e.g. \S1#4:
#     1/4
#
# \A	Alignment
#
#     \A0; = bottom
#     \A1; = center
#     \A2; = top
#
# \C	Color change
#
#     \C1; = red
#     \C2; = yellow
#     \C3; = green
#     \C4; = cyan
#     \C5; = blue
#     \C6; = magenta
#     \C7; = white
#
# \T	Tracking, char.spacing - e.g. \T2;
# \~	Non-wrapping space, hard space
# {}	Braces - define the text area influenced by the code
# \	Escape character - e.g. \\ = "\", \{ = "{"
#
# Codes and braces can be nested up to 8 levels deep


class MTextData(object):
    UNDERLINE_START = '\\L;'
    UNDERLINE_STOP = '\\l;'
    UNDERLINE = UNDERLINE_START + '%s' + UNDERLINE_STOP
    OVERSTRIKE_START = '\\O;'
    OVERSTRIKE_STOP = '\\o;'
    OVERSTRIKE = OVERSTRIKE_START + '%s' + OVERSTRIKE_STOP
    STRIKE_START = '\\K;'
    STRIKE_STOP = '\\k;'
    STRIKE = STRIKE_START + '%s' + STRIKE_STOP
    NEW_LINE = '\\P;'
    GROUP_START = '{'
    GROUP_END = '}'
    GROUP = GROUP_START + '%s' + GROUP_END
    NBSP = '\\~'  # none breaking space

    def __init__(self, text):
        self.text = text

    def __iadd__(self, text):
        self.text += text
        return self
    append = __iadd__

    def set_font(self, name, bold=False, italic=False, codepage=1252, pitch=0):
        bold_flag = 1 if bold else 0
        italic_flag = 1 if italic else 0
        s = "\\F{}|b{}|i{}|c{}|p{};".format(name, bold_flag, italic_flag, codepage, pitch)
        self.append(s)

    def set_color(self, color_name):
        self.append("\\C%d" % const.MTEXT_COLOR_INDEX[color_name.lower()])


def split_string_in_chunks(s, size=250):
    chunks = []
    pos = 0
    while True:
        chunk = s[pos:pos+size]
        chunk_len = len(chunk)
        if chunk_len:
            chunks.append(chunk)
            if chunk_len < size:
                return chunks
            pos += size
        else:
            return chunks

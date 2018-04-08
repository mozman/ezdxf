# Purpose: DXF 12 graphics entities
# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from .graphics import ExtendedTags, make_attribs, DXFAttr
from .text import Text
from ..lldxf import const
from ..tools import set_flag_state


_ATTRIB_TPL = """  0
ATTRIB
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
  1
DEFAULTTEXT
  2
TAG
 70
0
 50
0.0
 51
0.0
 41
1.0
  7
STANDARD
 71
0
 72
0
 73
0
 74
0
 11
0.0
 21
0.0
 31
0.0
"""


class Attrib(Text):
    TEMPLATE = ExtendedTags.from_text(_ATTRIB_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'rotation': DXFAttr(50, default=0.0),
        'oblique': DXFAttr(51, default=0.0),
        'width': DXFAttr(41, default=1.0),  # width factor
        'style': DXFAttr(7, default='STANDARD'),
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'valign': DXFAttr(74, default=0),  # vertical justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    })

    @property
    def is_const(self):
        """
        This is a constant attribute.
        """
        return bool(self.dxf.flags & const.ATTRIB_CONST)

    @is_const.setter
    def is_const(self, state):
        """
        This is a constant attribute.
        """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_CONST, state)

    @property
    def is_invisible(self):
        """
        Attribute is invisible (does not appear).
        """
        return bool(self.dxf.flags & const.ATTRIB_INVISIBLE)

    @is_invisible.setter
    def is_invisible(self, state):
        """
        Attribute is invisible (does not appear).
        """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_INVISIBLE, state)

    @property
    def is_verify(self):
        """
        Verification is required on input of this attribute. (CAD application feature)
        """
        return bool(self.dxf.flags & const.ATTRIB_VERIFY)

    @is_verify.setter
    def is_verify(self, state):
        """
        Verification is required on input of this attribute. (CAD application feature)
        """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_VERIFY, state)


    @property
    def is_preset(self):
        """
        No prompt during insertion. (CAD application feature)
        """
        return bool(self.dxf.flags & const.ATTRIB_IS_PRESET)

    @is_preset.setter
    def is_preset(self, state):
        """
        No prompt during insertion. (CAD application feature)
        """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_IS_PRESET, state)


_ATTDEF_TPL = """  0
ATTDEF
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
  1
DEFAULTTEXT
  3
PROMPTTEXT
  2
TAG
 70
0
 50
0.0
 51
0.0
 41
1.0
  7
STANDARD
 71
0
 72
0
 73
0
 74
0
 11
0.0
 21
0.0
 31
0.0
"""


class Attdef(Attrib):
    TEMPLATE = ExtendedTags.from_text(_ATTDEF_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'prompt': DXFAttr(3),
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'rotation': DXFAttr(50, default=0.0),
        'oblique': DXFAttr(51, default=0.0),
        'width': DXFAttr(41, default=1.0),  # width factor
        'style': DXFAttr(7, default='STANDARD'),
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'valign': DXFAttr(74, default=0),  # vertical justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    })


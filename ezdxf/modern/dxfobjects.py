# Created: 22.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..dxfentity import DXFEntity

none_subclass = DefSubclass(None, {
    'handle': DXFAttr(5),
    'owner': DXFAttr(330),
})


class DXFClass(DXFEntity):
    DXFATTRIBS = DXFAttributes(
        DefSubclass(None, {
            'name': DXFAttr(1),
            'cpp_class_name': DXFAttr(2),
            'app_name': DXFAttr(3),
            'flags': DXFAttr(90),
            'instance_count': DXFAttr(91, dxfversion='AC1018'),
            'was_a_proxy': DXFAttr(280),
            'is_an_entity': DXFAttr(281),
        }),
    )


class DXFObject(DXFEntity):
    def audit(self, auditor):
        auditor.check_pointer_target_exists(self, zero_pointer_valid=False)


_PLACEHOLDER_TPL = """0
ACDBPLACEHOLDER
5
0
330
0
"""


class ACDBPlaceHolder(DXFEntity):
    TEMPLATE = ExtendedTags.from_text(_PLACEHOLDER_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, )

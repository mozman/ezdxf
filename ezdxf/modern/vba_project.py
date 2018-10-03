# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import array

from ezdxf.tools.c23 import PY3
from ezdxf.lldxf.types import DXFBinaryTag
from ezdxf.tools.binarydata import array_to_bytes

from .dxfobjects import DXFObject, none_subclass, DefSubclass, DXFAttr, DXFAttributes, ExtendedTags

_VBA_PROJECT_TPL = """0
VBA_PROJECT
5
0
330
0
100
AcDbVbaProject
90
0
"""

vba_project_subclass = DefSubclass('AcDbVbaProject', {
    'count': DXFAttr(90),  # Number of bytes of binary chunk data (contained in the group code 310 records that follow)
    # 310: DXF: Binary object data (multiple entries containing VBA project data)
})


class VBAProject(DXFObject):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, vba_project_subclass)
    TEMPLATE = ExtendedTags.from_text(_VBA_PROJECT_TPL)
    # CLASS = ExtendedTags.from_text(_VBA_PROJECT_CLS)

    @property
    def AcDbVbaProject(self):
        return self.tags.subclasses[1]

    def get_data(self):
        byte_array = array.array('B')
        for byte_data in (tag.value for tag in self.AcDbVbaProject if tag.code == 310):
            if not PY3:
                byte_data = (ord(b) for b in byte_data)
            byte_array.extend(byte_data)
        return array_to_bytes(byte_array)

    def set_data(self, byte_data):
        self.clear()
        vba_tags = self.AcDbVbaProject
        start = 0
        count = 0
        while start < len(byte_data):
            vba_tags.append(DXFBinaryTag(310, byte_data[start:start+254]))
            count += 1
            start += 254
        self.dxf.count = count

    def clear(self):
        self.AcDbVbaProject.remove_tags(codes=(310, ))

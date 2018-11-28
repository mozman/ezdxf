# Created: 22.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT-License
from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, DXFAttr, none_subclass

_XRECORD_TPL = """  0
XRECORD
5
0
330
0
100
AcDbXrecord
280
"""


class XRecord(DXFObject):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbXrecord', {
            'cloning': DXFAttr(280),
            # 0=not applicable; 1=keep existing; 2=use clone; 3=<xref>$0$<name>; 4=$0$<name>; 5=Unmangle name
        }),
    )

    @property
    def content_tags(self):
        return self.tags.get_subclass('AcDbXrecord')

    @staticmethod
    def _adjust_index(index):
        return index if index < 0 else index + 2

    def __len__(self):
        # ignore first tags = (100, 'AcDbXrecord'), (280, ...)
        return len(self.content_tags) - 2

    def __getitem__(self, index):
        """
        Returns DXF tag at position *index*.
        """
        # skip first tags = (100, 'AcDbXrecord'), (280, ...)
        return self.content_tags[XRecord._adjust_index(index)]

    def __setitem__(self, index, dxftag):
        """
        Replace DXF tag at position *index* with *dxftag*.
        """
        # skip first tags = (100, 'AcDbXrecord'), (280, ...)
        self.content_tags[XRecord._adjust_index(index)] = dxftag

    def __iter__(self):
        """
        Iterate over data, yielding DXF tags as named tuple *(code, value)*.
        """
        tags = iter(self.content_tags)
        next(tags)  # skip (100, 'AcDbXrecord')
        next(tags)  # skip (280, ...)
        return tags

    def append(self, dxftag):
        """
        Append *dxftag* at the end of the tag list.
        """
        self.content_tags.append(dxftag)

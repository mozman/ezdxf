# Purpose: dxf objects wrapper, dxf-objects are non-graphical entities
# all dxf objects resides in the OBJECTS SECTION
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .tags import DXFTag
from .dxfattr import DXFAttr, DXFAttributes, DefSubclass
from .entity import GenericWrapper

ENTRY_NAME_CODE = 3

class DXFDictionary(GenericWrapper):
    DXFATTRIBS = DXFAttributes(
        DefSubclass(None, {
            'handle': DXFAttr(5, None),
            'parent': DXFAttr(330, None),
        }),
        DefSubclass('AcDbDictionary', {
            'hard_owned': DXFAttr(280, None),
            'cloning': DXFAttr(281, None),
        }),
    )

    def __init__(self, tags):
        super(DXFDictionary, self).__init__(tags)

    def keys(self):
        return (item[0] for item in self.items())

    def items(self):
        content_tags = self._get_content_tags()
        for index, tag in enumerate(content_tags):
            if tag.code == ENTRY_NAME_CODE:
                yield tag.value, content_tags[index + 1].value

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.add(key, value)

    def __contains__(self, key):
        return False if self._get_item_index(key) is None else True

    def __len__(self):
        return self.count()

    def count(self):
        return sum(1 for tag in self._get_content_tags() if tag.code == ENTRY_NAME_CODE)

    def get(self, key, default=KeyError):
        index = self._get_item_index(key)
        if index is None:
            if default is KeyError:
                raise KeyError("Item key=='{}' not found.".format(key))
            else:
                return default
        else:
            content_tags = self._get_content_tags()
            return content_tags[index + 1].value

    def add(self, key, value, code=350):
        index = self._get_item_index(key)
        value_tag = DXFTag(code, value)
        content_tags = self._get_content_tags()
        if index is None:  # create new entry
            content_tags.append(DXFTag(ENTRY_NAME_CODE, key))
            content_tags.append(value_tag)
        else:  # always replace existing values, until I understand the 281-tag (name mangling)
            content_tags[index + 1] = value_tag

    def _get_item_index(self, key):
        for index, tag in enumerate(self._get_content_tags()):
            if tag.code == ENTRY_NAME_CODE and tag.value == key:
                return index
        return None

    def _get_content_tags(self):
        return self.tags.get_subclass('AcDbDictionary')

class DXFLayout(GenericWrapper):
    DXFATTRIBS = DXFAttributes(
        DefSubclass(None, {
            'handle': DXFAttr(5, None),
            'parent': DXFAttr(330, None),
        }),
        DefSubclass('AcDbPlotSettings', {}),
        DefSubclass('AcDbLayout', {
            'name': DXFAttr(1, None),  # layout name
            'flags': DXFAttr(70, None),
            'taborder': DXFAttr(71, None),
            'limmin': DXFAttr(10, 'Point2D'),  # minimum limits
            'limmax': DXFAttr(11, 'Point2D'),  # maximum limits
            'insertbase': DXFAttr(12, 'Point3D'),  # Insertion base point for this layout
            'extmin': DXFAttr(14, 'Point3D'),  # Minimum extents for this layout
            'extmax': DXFAttr(15, 'Point3D'),  # Maximum extents for this layout
            'elevation': DXFAttr(146, None),
            'ucsorigin': DXFAttr(13, 'Point3D'),
            'ucsxaxis': DXFAttr(16, 'Point3D'),
            'ucsyaxis': DXFAttr(17, 'Point3D'),
            'ucstype': DXFAttr(76, None),
            # Orthographic type of UCS 0 = UCS is not orthographic;
            # 1 = Top; 2 = Bottom; 3 = Front; 4 = Back; 5 = Left; 6 = Right
            'block_record': DXFAttr(330, None),
            'viewport': DXFAttr(331, None),
            # ID/handle to the viewport that was last active in this
            # layout when the layout was current
            'ucs': DXFAttr(345, None),
            #ID/handle of AcDbUCSTableRecord if UCS is a named
            # UCS. If not present, then UCS is unnamed
            'baseucs': DXFAttr(345, None),
            #ID/handle of AcDbUCSTableRecord of base UCS if UCS is
            # orthographic (76 code is non-zero). If not present and
            # 76 code is non-zero, then base UCS is taken to be WORLD
        }))

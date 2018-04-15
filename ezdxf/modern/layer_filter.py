# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from ..lldxf.types import DXFTag
from .dxfobjects import ExtendedTags, DefSubclass, DXFAttributes
from .dxfobjects import none_subclass, DXFObject

_LAYER_FILTER_TPL = """0
LAYER_FILTER
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbFilter
100
AcDbLayerFilter
"""


class LayerFilter(DXFObject):
    # Requires AC1015/R2000
    TEMPLATE = ExtendedTags.from_text(_LAYER_FILTER_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbFilter', {}), DefSubclass('AcDbLayerFilter', {}),)
    BUFFER_START_INDEX = 1

    @property
    def layer_filter_subclass(self):
        return self.tags.subclasses[2]  # 2nd subclass

    def get_layer_names(self):
        return [tag.value for tag in self.layer_filter_subclass[self.BUFFER_START_INDEX:]]

    def set_layer_names(self, names):
        self.layer_filter_subclass[self.BUFFER_START_INDEX:] = [DXFTag(330, layer_name) for layer_name in names]

    def __len__(self):
        return len(self.layer_filter_subclass) - self.BUFFER_START_INDEX

    def __iter__(self):
        return iter(self.get_layer_names())

    def __getitem__(self, item):
        return self.get_layer_names()[item]

    def __setitem__(self, item, value):
        handles = self.get_layer_names()
        handles[item] = value
        self.set_layer_names(handles)

    def __delitem__(self, key):
        handles = self.get_layer_names()
        del handles[key]
        self.set_layer_names(handles)

    def append(self, name):
        self.layer_filter_subclass.append(DXFTag(330, name))

    def __iadd__(self, name):
        self.append(name)
        return self


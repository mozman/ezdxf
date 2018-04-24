# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .dxfobjects import ExtendedTags, DefSubclass, DXFAttributes
from .dxfobjects import none_subclass, DXFObject
from ..lldxf.const import DXFValueError
from ..lldxf import loader
from ..lldxf.packedtags import TagList
from ..tools.c23 import isstring

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


@loader.register('LAYER_FILTER', legacy=False)
def tag_processor(tags):
    subclass = tags.get_subclass('AcDbLayerFilter')
    names = TagList.from_tags(subclass)
    names.replace_tags(subclass)
    return tags


class LayerFilter(DXFObject):
    # Requires AC1015/R2000
    TEMPLATE = tag_processor(ExtendedTags.from_text(_LAYER_FILTER_TPL))
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbFilter', {}), DefSubclass('AcDbLayerFilter', {}),)
    BUFFER_START_INDEX = 1

    @property
    def layer_filter_subclass(self):
        return self.tags.subclasses[2]

    @property
    def layers(self):
        try:
            return self._cached_layers
        except AttributeError:
            self._cached_layers = self.layer_filter_subclass.get_first_value(TagList.code)
            return self._cached_layers

    @layers.setter
    def layers(self, names):
        if isstring(names):
            raise DXFValueError('requires iterable but not string')
        self.layers[:] = list(names)


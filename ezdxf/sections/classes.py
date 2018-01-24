# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"
from collections import Counter
from ..lldxf.tags import group_tags
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.const import DXFStructureError
from ..modern.dxfobjects import DXFClass


class ClassesSection(object):
    name = 'CLASSES'

    def __init__(self, entities=None, drawing=None):
        self.classes = []  # DXFClasses are not stored in the entities database!
        self.drawing = drawing
        if entities is not None:
            self._build(iter(entities), drawing)

    def __iter__(self):
        return iter(self.classes)

    def _build(self, entities, drawing):
        section_head = next(entities)
        if section_head[0] != (0, 'SECTION') or section_head[1] != (2, 'CLASSES'):
            raise DXFStructureError("Critical structure error in CLASSES section.")

        for class_tags in entities:
            # DXFClasses are not stored in the entities database!
            self.classes.append(DXFClass(ExtendedTags(class_tags), drawing))

    def write(self, tagwriter):
        tagwriter.write_str("  0\nSECTION\n  2\nCLASSES\n")
        for dxfclass in self.classes:
            tagwriter.write_tags(dxfclass.tags)
        tagwriter.write_str("  0\nENDSEC\n")

    def update_instance_counters(self):
        if len(self.classes) == 0:
            return  # nothing to do
        if self.drawing is not None and self.drawing.dxfversion < 'AC1018':
            return  # instance counter not supported
        counter = Counter()
        for entity in self.drawing.entities:
            counter[entity.dxftype()] += 1
        if 'objects' in self.drawing.sections:
            for obj in self.drawing.objects:
                counter[obj.dxftype()] += 1

        for dxfclass in self.classes:
            dxfclass.dxf.instance_count = counter[dxfclass.dxf.name]

    def reset_instance_counters(self):
        if self.drawing is not None and self.drawing.dxfversion < 'AC1018':
            return  # instance counter not supported
        for dxfclass in self.classes:
            dxfclass.dxf.instance_count = 0

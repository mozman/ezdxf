# Purpose: entity section
# Created: 13.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from collections import Counter
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.const import DXFStructureError
from ..modern.dxfobjects import DXFClass


class ClassesSection(object):
    name = 'CLASSES'

    def __init__(self, entities=None, drawing=None):
        self.classes = []  # DXFClasses are not stored in the entities database!
        self.drawing = drawing
        self.registrated_classes = set()
        if entities is not None:
            self._build(iter(entities))

    def __iter__(self):
        return iter(self.classes)

    def _build(self, entities):
        section_head = next(entities)
        if section_head[0] != (0, 'SECTION') or section_head[1] != (2, 'CLASSES'):
            raise DXFStructureError("Critical structure error in CLASSES section.")

        for class_tags in entities:
            self.register(ExtendedTags(class_tags))

    def register(self, tags):
        if tags.noclass.get_first_value(1) in self.registrated_classes:
            return
        dxf_class = DXFClass(tags, self.drawing)
        self.registrated_classes.add(dxf_class.dxf.name)
        # DXFClasses are not stored in the entities database!
        self.classes.append(dxf_class)

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

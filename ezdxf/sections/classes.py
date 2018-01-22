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
    name = 'classes'

    def __init__(self, tags, drawing):
        self.classes = []  # DXFClasses are not stored in the drawing database!
        if tags is not None:
            self._build(tags)

    def __iter__(self):
        return iter(self.classes)

    def _build(self, tags):
        if tags[0] != (0, 'SECTION') or tags[1] != (2, self.name.upper()) or tags[-1] != (0, 'ENDSEC'):
            raise DXFStructureError("Critical structure error in {} section.".format(self.name.upper()))

        if len(tags) == 3:  # empty entities section
            return

        for class_tags in group_tags(tags[2:-1]):
            # DXFClasses are not stored in the drawing database!
            self.classes.append(DXFClass(ExtendedTags(class_tags)))

    def write(self, tagwriter):
        tagwriter.write_str("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        for dxfclass in self.classes:
            tagwriter.write_tags(dxfclass.tags)
        tagwriter.write_tag2(0, "ENDSEC")

    def update_instance_counters(self, entities):
        if len(self.classes) == 0:
            return  # nothing to do
        counter = Counter()
        for entity in entities:
            counter[entity.dxftype()] += 1

        for dxfclass in self.classes:
            dxfclass.dxf.instance_count = counter[dxfclass.dxf.name]

    def reset_instance_counters(self):
        for dxfclass in self.classes:
            dxfclass.dxf.instance_count = 0

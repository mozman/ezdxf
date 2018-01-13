# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .abstract import AbstractSection
from ..lldxf.tags import write_tags
from ..lldxf.extendedtags import ExtendedTags


class ClassEntitySpace(list):
    def __init__(self, entitydb):
        self._entitydb = entitydb

    def store_tags(self, tags):
        if isinstance(tags, ExtendedTags):
            self.append(tags)
        else:
            self.append(tags.tags)

    def write(self, stream):
        for class_tags in self:
            write_tags(stream, (tag for tag in class_tags if tag.code != 5))


class ClassesSection(AbstractSection):
    name = 'classes'

    def __init__(self, tags, drawing):
        entity_space = ClassEntitySpace(drawing.entitydb)
        super(ClassesSection, self).__init__(entity_space, tags, drawing)

    def __iter__(self):
        wrap = self.dxffactory.wrap_entity
        for tags in self._entity_space:
            yield wrap(tags)

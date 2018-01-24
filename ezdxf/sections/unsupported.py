# Purpose: default chunk
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


class UnsupportedSection(object):
    def __init__(self, entities, drawing):
        self.entities = entities
        self._drawing = drawing

    @property
    def dxffactory(self):
        return self._drawing.dxffactory

    @property
    def name(self):
        return self.entities[0][1].value

    def write(self, tagwriter):
        for entity in self.entities:
            tagwriter.write_tags(entity)
        tagwriter.write_tag2(0, 'ENDSEC')

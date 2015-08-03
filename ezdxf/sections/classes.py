# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..entityspace import EntitySpace
from .abstract import AbstractSection


class ClassesSection(AbstractSection):
    name = 'classes'

    def __init__(self, tags, drawing):
        entity_space = EntitySpace(drawing.entitydb)
        super(ClassesSection, self).__init__(entity_space, tags, drawing)

    def __iter__(self):  # no layout setting required/possible
        for handle in self._entity_space:
            yield self.dxffactory.wrap_handle(handle)


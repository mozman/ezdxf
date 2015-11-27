# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..entityspace import LayoutSpaces
from .abstract import AbstractSection


class EntitySection(AbstractSection):
    name = 'entities'

    def __init__(self, tags, drawing):
        layout_spaces = LayoutSpaces(drawing.entitydb, drawing.dxfversion)
        super(EntitySection, self).__init__(layout_spaces, tags, drawing)

    def get_layout_space(self, key):
        return self._entity_space.get_entity_space(key)

    # start of public interface

    def __iter__(self):
        dxffactory = self.dxffactory
        for handle in self._entity_space.handles():
            entity = dxffactory.wrap_handle(handle)
            yield entity

    # end of public interface

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        # Just write *Model_Space and the active *Paper_Space into the ENTITIES section.
        layout_keys = [self.drawing.modelspace().layout_key]
        paperspace_key = self.drawing.get_active_layout_key()
        if paperspace_key is not None:
            layout_keys.append(paperspace_key)
        self._entity_space.write(stream, layout_keys)
        stream.write("  0\nENDSEC\n")

    def repair_model_space(self, model_space_layout_key):
        self._entity_space.repair_model_space(model_space_layout_key)
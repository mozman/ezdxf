# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..entityspace import LayoutSpaces
from .abstract import AbstractSection


class EntitySection(AbstractSection):
    name = 'ENTITIES'

    def __init__(self, tags, drawing):
        layout_spaces = LayoutSpaces(drawing.entitydb, drawing.dxfversion)
        super(EntitySection, self).__init__(layout_spaces, tags, drawing)

    def get_layout_space(self, key):
        return self._entity_space.get_entity_space(key)

    def set_layout_space(self, key, entity_space):
        return self._entity_space.set_entity_space(key, entity_space)

    # start of public interface

    def __iter__(self):
        wrap = self.dxffactory.wrap_handle
        for handle in self._entity_space.handles():
            yield wrap(handle)

    # end of public interface

    def write(self, tagwriter):
        tagwriter.write_str("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        # Just write *Model_Space and the active *Paper_Space into the ENTITIES section.
        layout_keys = self.drawing.get_active_entity_space_layout_keys()
        self._entity_space.write(tagwriter, layout_keys)
        tagwriter.write_tag2(0, "ENDSEC")

    def repair_owner_tags(self, model_space_layout_key, paper_space_key):
        self._entity_space.repair_owner_tags(model_space_layout_key, paper_space_key)

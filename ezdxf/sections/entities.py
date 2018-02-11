# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from itertools import chain
from ..entityspace import LayoutSpaces, EntitySpace
from .abstract import AbstractSection


class SetupEntitySection(AbstractSection):
    name = 'ENTITIES'

    def __init__(self, tags, drawing):
        super(SetupEntitySection, self).__init__(EntitySpace(drawing.entitydb), tags, drawing)

    def __iter__(self):
        layouts = self.drawing.layouts
        for entity in chain(layouts.modelspace(), layouts.active_layout()):
            yield entity

    def __len__(self):
        layouts = self.drawing.layouts
        return len(layouts.modelspace())+len(layouts.active_layout())

    def clear(self):
        del self._entity_space

    def _setup_entities(self):
        wrap = self.dxffactory.wrap_handle
        for handle in self._entity_space:
            yield wrap(handle)

    def model_space_entities(self):
        es = EntitySpace(self.entitydb)
        es.extend(self._filter_entities(paper_space=0))
        return es

    def active_layout_entities(self):
        es = EntitySpace(self.entitydb)
        es.extend(self._filter_entities(paper_space=1))
        return es

    def _filter_entities(self, paper_space=0):
        return (entity.dxf.handle for entity in self._setup_entities() if entity.get_dxf_attrib('paperspace', 0) == paper_space)

    def delete_all_entities(self):
        layouts = self.drawing.layouts
        layouts.modelspace().delete_all_entities()
        layouts.active_layout().delete_all_entities()

    def write(self, tagwriter):
        tagwriter.write_str("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        # Just write *Model_Space and the active *Paper_Space into the ENTITIES section.
        self.drawing.layouts.write_entities_section(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")


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

    def iter_layout_entities(self):
        layouts = self.drawing.layouts
        for entity in chain(layouts.modelspace(), layouts.active_layout()):
            yield entity

    # end of public interface

    def write(self, tagwriter):
        tagwriter.write_str("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        # Just write *Model_Space and the active *Paper_Space into the ENTITIES section.
        self.drawing.layouts.write_entities_section(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    def repair_owner_tags(self, model_space_layout_key, paper_space_key):
        self._entity_space.repair_owner_tags(model_space_layout_key, paper_space_key)

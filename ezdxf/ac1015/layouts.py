# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

# The ModelSpace is a special Layout called 'Model'

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .creator import EntityCreator
from ..ac1009.layouts import DXF12Layout, DXF12BlockLayout
from ..classifiedtags import ClassifiedTags

class Layouts(object):
    #TODO: user defined new layouts
    def __init__(self, drawing):
        self._layouts = {}
        self._layout_table = None
        self._setup(drawing)

    def _setup(self, drawing):
        dxffactory = drawing.dxffactory
        layout_table_handle = drawing.rootdict['ACAD_LAYOUT']
        self._layout_table = dxffactory.wrap_handle(layout_table_handle)
        # name ... layout name
        # handle ...  handle to DXF object Layout
        for name, handle in self._layout_table.items():
            self._layouts[name] = Layout(drawing, handle)

    def __contains__(self, name):
        return name in self._layouts

    def modelspace(self):
        return self.get('Model')

    def names(self):
        return self._layouts.keys()

    def get(self, name):
        if name is None:
            first_layout_name = self.names_in_taborder()[1]
            return self._layouts[first_layout_name]
        else:
            return self._layouts[name]

    def names_in_taborder(self):
        names = []
        for name, layout in self._layouts.items():
            names.append((layout.taborder, name))
        return [name for order, name in sorted(names)]


class Layout(DXF12Layout, EntityCreator):
    """ Layout representation
    """
    def __init__(self, drawing, layout_handle):
        entity_space = drawing.sections.entities.get_entityspace()
        dxf_factory = drawing.dxffactory
        super(Layout, self).__init__(entity_space, dxf_factory, 0)
        self._layout_handle = layout_handle
        self._block_record = self.dxflayout.dxf.block_record
        self._paperspace = 0 if self.name == 'Model' else 1

    # start of public interface

    def __iter__(self):
        """ Iterate over all layout entities, yielding class GraphicEntity() or inherited.
        """
        for entity in self._iter_all_entities():
            if entity.get_dxf_attrib('owner') == self._block_record:
                yield entity

    def __contains__(self, entity):
        if not hasattr(entity, 'dxf'):  # entity is a handle and not a wrapper class
            entity = self._dxffactory.wrap_handle(entity)
        return True if entity.get_dxf_attrib('owner') == self._block_record else False

    # end of public interface

    @property
    def dxflayout(self):
        return self._dxffactory.wrap_handle(self._layout_handle)

    @property
    def name(self):
        return self.dxflayout.dxf.name

    @property
    def taborder(self):
        return self.dxflayout.dxf.taborder

    def _set_paperspace(self, entity):
        entity.dxf.paperspace = self._paperspace
        entity.dxf.owner = self._block_record


class BlockLayout(DXF12BlockLayout, EntityCreator):
    def add_entity(self, entity):
        """ Add entity to the block entity space.
        """
        # entity can be ClassifiedTags() or a Wrapper() class
        if isinstance(entity, ClassifiedTags):
            entity = self._dxffactory.wrap_entity(entity)
        entity.dxf.owner = self.get_block_record_handle()
        self._entityspace.add(entity)

    def get_block_record_handle(self):
        return self.block.dxf.owner

    def set_block_record_handle(self, block_record_handle):
        self.block.dxf.owner = block_record_handle
        self.endblk.dxf.owner = block_record_handle
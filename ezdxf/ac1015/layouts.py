# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

# The ModelSpace is a special Layout called 'Model'

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .graphicsfactory import GraphicsFactoryAC1015
from ..ac1009.layouts import DXF12Layout, DXF12BlockLayout
from ..classifiedtags import ClassifiedTags


class Layouts(object):
    #TODO: user defined new layouts
    def __init__(self, drawing):
        self.drawing = drawing
        self._layouts_by_name = {}
        self._layouts_by_owner_id = {}
        self._layout_table = None
        self._setup()

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    def _setup(self):
        layout_table_handle = self.drawing.rootdict['ACAD_LAYOUT']
        self._layout_table = self.dxffactory.wrap_handle(layout_table_handle)
        # name ... layout name
        # handle ...  handle to DXF object Layout
        for name, handle in self._layout_table.items():
            layout = Layout(self.drawing, handle)
            self._add_layout(name, layout)

    def _add_layout(self, name, layout):
        self._layouts_by_name[name] = layout
        self._layouts_by_owner_id[layout.layout_key] = layout

    def __contains__(self, name):
        return name in self._layouts_by_name

    def __iter__(self):
        return iter(self._layouts_by_name.values())

    def modelspace(self):
        return self.get('Model')

    def names(self):
        return self._layouts_by_name.keys()

    def get(self, name):
        if name is None:
            first_layout_name = self.names_in_taborder()[1]
            return self._layouts_by_name[first_layout_name]
        else:
            return self._layouts_by_name[name]

    def names_in_taborder(self):
        names = []
        for name, layout in self._layouts_by_name.items():
            names.append((layout.taborder, name))
        return [name for order, name in sorted(names)]

    def get_layout_for_entity(self, entity):
        return self._layouts_by_owner_id[entity.dxf.owner]

    def create(self, name, dxfattribs=None):
        """ Create a new Layout.
        """
        if dxfattribs is None:
            dxfattribs = {}

        if name in self._layouts_by_name:
            raise ValueError("Layout '{}' already exists".format(name))

        def create_db_entry():
            dxfattribs['name'] = name
            dxfattribs['owner'] = self._layout_table.dxf.handle
            dxfattribs.setdefault('taborder', len(self._layouts_by_name) + 1)
            dxfattribs['block_record'] = block_record_handle
            return self.dxffactory.create_db_entry('LAYOUT', dxfattribs)

        def set_block_record_layout():
            block_record = self.dxffactory.wrap_handle(block_record_handle)
            block_record.dxf.layout = layout_handle

        def create_dxf_layout_entity():
            dxf_entity = create_db_entry()
            layout_handle = dxf_entity.dxf.handle
            # the DXF layout entity resides in the objects section
            self.drawing.sections.objects.add_handle(layout_handle)
            return layout_handle

        block_record_handle = self.drawing.blocks.new_paper_space_block()
        layout_handle = create_dxf_layout_entity()
        set_block_record_layout()
        layout = Layout(self.drawing, layout_handle)
        # set DXF layout management table
        self._layout_table[name] = layout_handle
        self._add_layout(name, layout)
        return layout

    def delete(self, name):
        """ Delete Layout and all entities on it.
        """
        pass


class Layout(DXF12Layout, GraphicsFactoryAC1015):
    """ Layout representation
    """
    def __init__(self, drawing, layout_handle):
        def _get_layout_key():
            dxflayout = drawing.dxffactory.wrap_handle(layout_handle)
            return dxflayout.dxf.block_record

        layout_key = _get_layout_key()  # == block_record handle
        entitities_section = drawing.sections.entities
        layout_space = entitities_section.get_layout_space(layout_key)
        dxffactory = drawing.dxffactory
        super(Layout, self).__init__(layout_space, dxffactory, 0)
        self._layout_handle = layout_handle
        self._block_record_handle = self.dxflayout.dxf.block_record
        self._paperspace = 0 if self.name == 'Model' else 1

    # start of public interface

    def __contains__(self, entity):
        if not hasattr(entity, 'dxf'):  # entity is a handle and not a wrapper class
            entity = self.get_entity_by_handle(entity)
        return True if entity.dxf.owner == self.layout_key else False

    # end of public interface

    @property
    def layout_key(self):
        return self._block_record_handle

    @property
    def dxflayout(self):
        return self.get_entity_by_handle(self._layout_handle)

    @property
    def name(self):
        return self.dxflayout.dxf.name

    @property
    def taborder(self):
        return self.dxflayout.dxf.taborder

    def _set_paperspace(self, entity):
        entity.dxf.paperspace = self._paperspace
        entity.dxf.owner = self.layout_key


class BlockLayout(DXF12BlockLayout, GraphicsFactoryAC1015):
    def add_entity(self, entity):
        """ Add entity to the block entity space.
        """
        # entity can be ClassifiedTags() or a Wrapper() class
        if isinstance(entity, ClassifiedTags):
            entity = self._dxffactory.wrap_entity(entity)
        entity.dxf.owner = self.get_block_record_handle()
        self._entity_space.append(entity.dxf.handle)

    def get_block_record_handle(self):
        return self.block.dxf.owner

    def set_block_record_handle(self, block_record_handle):
        self.block.dxf.owner = block_record_handle
        self.endblk.dxf.owner = block_record_handle
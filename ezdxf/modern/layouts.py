# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

# The ModelSpace is a special Layout called 'Model'

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .graphicsfactory import ModernGraphicsFactory
from ..legacy.layouts import DXF12Layout, DXF12BlockLayout
from ..lldxf.classifiedtags import ClassifiedTags
from ..entityspace import EntitySpace


class Layouts(object):
    def __init__(self, drawing):
        self.drawing = drawing
        self._layouts = {}  # stores Layout() objects
        self._dxf_layout_management_table = None  # stores DXF layout handles key=layout_name; value=layout_handle
        self._setup()

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    def _setup(self):
        layout_table_handle = self.drawing.rootdict['ACAD_LAYOUT']
        self._dxf_layout_management_table = self.dxffactory.wrap_handle(layout_table_handle)
        # name ... layout name
        # handle ...  handle to DXF object Layout
        for name, handle in self._dxf_layout_management_table.items():
            layout = Layout(self.drawing, handle)
            self._layouts[name] = layout

    def move_entities_from_blocks_into_layout_entity_space(self):
        layout_spaces = self.drawing.entities.get_entity_space()
        entitydb = self.drawing.entitydb
        for layout in self:
            if not layout.is_active():
                block = layout.block
                # copy block entity space to layout entity space
                layout_spaces.set_entity_space(layout.layout_key, block.get_entity_space())
                # replace block entity space with an empty entity space
                block.set_entity_space(EntitySpace(entitydb))

    def link_block_entities_into_layouts(self):  # not used yet
        layout_spaces = self.drawing.entities.get_entity_space()
        for layout in self:
            if not layout.is_active():
                # copy block entity space to layout entity space
                layout_spaces.set_entity_space(layout.layout_key, layout.block.get_entity_space())
                # now the block entity space and layout entity space references the same EntitySpace() object

    def link_layout_entities_to_blocks(self):
        entities_section = self.drawing.entities
        for layout in self:
            if not layout.is_active():
                # link layout space into block
                layout.block.set_entity_space(entities_section.get_layout_space(layout.layout_key))

    def unlink_layout_entities_from_blocks(self):
        entitydb = self.drawing.entitydb
        for layout in self:
            # unlink layout entity space from block entity space
            layout.block.set_entity_space(EntitySpace(entitydb))

    def __contains__(self, name):
        return name in self._layouts

    def __iter__(self):
        return iter(self._layouts.values())

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

    def get_layout_for_entity(self, entity):
        owner_handle = entity.dxf.owner
        for layout in self._layouts.values():
            if owner_handle == layout.layout_key:
                return layout
        raise KeyError("Layout with key '{}' does not exist.".format(owner_handle))

    def create(self, name, dxfattribs=None):
        """ Create a new Layout.
        """
        if dxfattribs is None:
            dxfattribs = {}

        if name in self._layouts:
            raise ValueError("Layout '{}' already exists".format(name))

        def create_dxf_layout_entity():
            dxfattribs['name'] = name
            dxfattribs['owner'] = self._dxf_layout_management_table.dxf.handle
            dxfattribs.setdefault('taborder', len(self._layouts) + 1)
            dxfattribs['block_record'] = block_record_handle
            entity = self.drawing.objects.create_new_dxf_entity('LAYOUT', dxfattribs)
            return entity.dxf.handle

        def set_block_record_layout():
            block_record = self.dxffactory.wrap_handle(block_record_handle)
            block_record.dxf.layout = layout_handle

        def add_layout_to_management_tables():
            self._dxf_layout_management_table[name] = layout_handle
            self._layouts[name] = layout

        block_record_handle = self.drawing.blocks.new_paper_space_block()
        layout_handle = create_dxf_layout_entity()
        set_block_record_layout()
        layout = Layout(self.drawing, layout_handle)
        add_layout_to_management_tables()
        return layout

    def delete(self, name):
        """ Delete layout *name* and all entities on it. Raises *KeyError* if layout *name* not exists.
        Raises *ValueError* for deleting model space.
        """
        if name == 'Model':
            raise ValueError("can not delete model space layout")

        layout = self._layouts[name]
        self._dxf_layout_management_table.remove(layout.name)
        del self._layouts[layout.name]
        layout.destroy()
        # TODO: if active layout is deleted, set another layout as active


class Layout(ModernGraphicsFactory, DXF12Layout):
    """ Layout representation
    """
    def __init__(self, drawing, layout_handle):
        dxffactory = drawing.dxffactory
        self.dxf_layout = dxffactory.wrap_handle(layout_handle)
        self._block_record_handle = self.dxf_layout.dxf.block_record
        entitities_section = drawing.sections.entities
        layout_space = entitities_section.get_layout_space(self.layout_key)
        super(Layout, self).__init__(layout_space, dxffactory, 0)
        self._layout_handle = layout_handle
        self._paperspace = 0 if self.name == 'Model' else 1

    # start of public interface

    def __contains__(self, entity):
        if not hasattr(entity, 'dxf'):  # entity is a handle and not a wrapper class
            entity = self.get_entity_by_handle(entity)
        return True if entity.dxf.owner == self.layout_key else False

    @property
    def dxf(self):
        return self.dxf_layout.dxf

    # end of public interface

    @property
    def layout_key(self):
        return self._block_record_handle

    @property
    def block_record(self):
        return self.drawing.dxffactory.wrap_handle(self._block_record_handle)

    @property
    def block_record_name(self):
        return self.block_record.dxf.name

    @property
    def block(self):
        return self.drawing.blocks.get(self.block_record_name)

    @property
    def name(self):
        return self.dxf_layout.dxf.name

    @property
    def taborder(self):
        return self.dxf_layout.dxf.taborder

    def is_active(self):
        return self.block_record_name in ('*Model_Space', '*Paper_Space')

    def _set_paperspace(self, entity):
        entity.dxf.paperspace = self._paperspace
        entity.dxf.owner = self.layout_key

    def destroy(self):
        def delete_layout_definition_block():
            for block in self.drawing.blocks:
                if block.get_block_record_handle() == self.layout_key:
                    break
            else:
                return
            self.drawing.blocks.delete_block(block.name)

        self.delete_all_entities()
        delete_layout_definition_block()
        self.drawing.objects.remove_handle(self._layout_handle)
        self.drawing.entitydb.delete_handle(self._layout_handle)


class BlockLayout(ModernGraphicsFactory, DXF12BlockLayout):
    def add_entity(self, entity):
        """ Add entity to the block entity space.
        """
        # entity can be ClassifiedTags() or a GraphicEntity() or inherited wrapper class
        if isinstance(entity, ClassifiedTags):
            entity = self._dxffactory.wrap_entity(entity)
        entity.dxf.owner = self.get_block_record_handle()
        self._entity_space.append(entity.dxf.handle)

    def get_block_record_handle(self):
        return self.block.dxf.owner

    def set_block_record_handle(self, block_record_handle):
        self.block.dxf.owner = block_record_handle
        self.endblk.dxf.owner = block_record_handle

    def get_entity_space(self):
        return self._entity_space

    def set_entity_space(self, entity_space):
        self._entity_space = entity_space

    def destroy(self):
        self.drawing.sections.tables.block_records.remove_handle(self.get_block_record_handle())
        super(BlockLayout, self).destroy()

# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

# The ModelSpace is a special Layout called 'Model'

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"
import warnings

from ..legacy.layouts import DXF12Layout, DXF12BlockLayout
from ..lldxf.classifiedtags import ClassifiedTags


PAPER_SPACE = '*Paper_Space'
TMP_PAPER_SPACE_NAME = '*Paper_Space999999'


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

    def link_block_entities_into_layouts(self):
        # layout entity spaces are always linked to the block definition
        layout_spaces = self.drawing.entities.get_entity_space()
        for layout in self:
            if not layout.is_active():
                # copy block entity space to layout entity space
                layout_spaces.set_entity_space(layout.layout_key, layout.block.get_entity_space())
                # now the block entity space and layout entity space references the same EntitySpace() object

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
        return self.get_layout_by_key(entity.dxf.owner)

    def get_layout_by_key(self, layout_key):
        for layout in self._layouts.values():
            if layout_key == layout.layout_key:
                return layout
        raise KeyError("Layout with key '{}' does not exist.".format(layout_key))

    def new(self, name, dxfattribs=None):
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

        block_layout = self.drawing.blocks.new_layout_block()
        block_record_handle = block_layout.block_record_handle
        block_record = block_layout.block_record
        layout_handle = create_dxf_layout_entity()
        block_record.dxf.layout = layout_handle

        # set block entity space as layout entity space
        self.drawing.entities.set_layout_space(layout_handle, block_layout.get_entity_space())

        # create valid layout entity
        layout = Layout(self.drawing, layout_handle)

        # add layout to management tables
        self._dxf_layout_management_table[name] = layout_handle
        self._layouts[name] = layout

        return layout

    def set_active_layout(self, name):
        if name == 'Model':  # reserved layout name
            raise ValueError("Can not set model space as active layout")
        new_active_layout = self.get(name)  # raises KeyError if no layout 'name' exists
        old_active_layout_key = self.drawing.get_active_layout_key()
        if old_active_layout_key == new_active_layout.layout_key:
            return  # layout 'name' is already the active layout

        blocks = self.drawing.blocks
        new_active_paper_space_name = new_active_layout.block_record_name

        blocks.rename_block(PAPER_SPACE, TMP_PAPER_SPACE_NAME)
        blocks.rename_block(new_active_paper_space_name, PAPER_SPACE)
        blocks.rename_block(TMP_PAPER_SPACE_NAME, new_active_paper_space_name)
        # Layout spaces stored by layout key, no exchange necessary

    def delete(self, name):
        """ Delete layout *name* and all entities on it. Raises *KeyError* if layout *name* not exists.
        Raises *ValueError* for deleting model space.
        """
        if name == 'Model':
            raise ValueError("can not delete model space layout")

        layout = self._layouts[name]
        if layout.layout_key == self.drawing.get_active_layout_key():  # name is the active layout
            for layout_name in self.names():
                if layout_name not in (name, 'Model'):  # set any other layout as active layout
                    self.set_active_layout(layout_name)
                    break
        self._dxf_layout_management_table.remove(layout.name)
        del self._layouts[layout.name]
        layout.destroy()


class Layout(DXF12Layout):
    """ Layout representation

    Every layout consist of a LAYOUT entity in the OBJECTS section, an associated BLOCK in the BLOCKS section and a
    BLOCK_RECORD_TABLE entry.

    layout_key: handle of the BLOCK_RECORD, every layout entity has this handle as owner attribute (entity.dxf.owner)

    There are 3 different layout types:

    1. Model Space - not deletable, all entities of this layout are stored in the DXF file in the ENTITIES section, the
    associated '*Model_Space' block is empty, block name '*Model_Space' is mandatory, the layout name is 'Model' and it
    is mandatory.

    2. Active Layout - all entities of this layout are stored in the DXF file also in the ENTITIES section, the
    associated '*Paper_Space' block is empty, block name '*Paper_Space' is mandatory and also marks the active
    layout, the layout name can be an arbitrary string.

    3. Inactive Layout - all entities of this layouts are stored in the DXF file in the associated BLOCK
    called '*Paper_SpaceN', where N is an arbitrary number, I don't know if the block name schema '*Paper_SpaceN' is
    mandatory, the layout name can be an arbitrary string.

    There is no different handling for active layouts and inactive layouts in ezdxf, this differentiation is just
    for AutoCAD important and it is not described in the DXF standard.

    Internal Structure:

    For EVERY layout exists a BlockLayout() object in the blocks section and an EntitySpace() object in the entities
    sections. the block layout entity section and the layout entity section are the SAME object.
    See Layouts.create() line after comment 'set block entity space as layout entity space'.

    ALL layouts entity spaces (also Model Space) are managed in a LayoutSpaces() object in the EntitySection() object.
    Which allows full access to all entities on all layouts at every time.

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
        return self.block_record_name.upper() in ('*PAPER_SPACE', '*MODEL_SPACE')

    def _set_paperspace(self, entity):
        entity.dxf.paperspace = self._paperspace
        entity.dxf.owner = self.layout_key

    def destroy(self):
        self.delete_all_entities()
        self.drawing.blocks.delete_block(self.block.name)
        self.drawing.objects.remove_handle(self._layout_handle)
        self.drawing.entitydb.delete_handle(self._layout_handle)


class BlockLayout(DXF12BlockLayout):
    def add_entity(self, entity):
        """ Add entity to the block entity space.
        """
        # entity can be ClassifiedTags() or a GraphicEntity() or inherited wrapper class
        if isinstance(entity, ClassifiedTags):
            entity = self._dxffactory.wrap_entity(entity)
        entity.dxf.owner = self.block_record_handle
        self._entity_space.append(entity.dxf.handle)

    @property
    def block_record_handle(self):
        return self.block.dxf.owner

    def set_block_record_handle(self, block_record_handle):
        self.block.dxf.owner = block_record_handle
        self.endblk.dxf.owner = block_record_handle

    @property
    def block_record(self):
        return self.drawing.dxffactory.wrap_handle(self.block_record_handle)

    def get_entity_space(self):
        return self._entity_space

    def set_entity_space(self, entity_space):
        self._entity_space = entity_space

    def destroy(self):
        self.drawing.sections.tables.block_records.remove_handle(self.block_record_handle)
        super(BlockLayout, self).destroy()


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

        def add_layout_to_management_tables():
            self._dxf_layout_management_table[name] = layout_handle
            self._layouts[name] = layout

        block_layout = self.drawing.blocks.new_layout_block()
        block_record_handle = block_layout.block_record_handle
        block_record = block_layout.block_record
        block = block_layout.block
        layout_handle = create_dxf_layout_entity()
        block_record.dxf.layout = layout_handle

        # set block entity space as layout entity space
        self.drawing.entities.set_layout_space(layout_handle, block_layout.get_entity_space())

        layout = Layout(self.drawing, layout_handle)
        add_layout_to_management_tables()
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


class Layout(ModernGraphicsFactory, DXF12Layout):
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
        return self.block_record_name in ('*Model_Space', '*Paper_Space')

    def _set_paperspace(self, entity):
        entity.dxf.paperspace = self._paperspace
        entity.dxf.owner = self.layout_key

    def destroy(self):
        self.delete_all_entities()
        self.drawing.blocks.delete_block(self.block.name)
        self.drawing.objects.remove_handle(self._layout_handle)
        self.drawing.entitydb.delete_handle(self._layout_handle)


class BlockLayout(ModernGraphicsFactory, DXF12BlockLayout):
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

_MODEL_SPACE_LAYOUT_TPL = """  0
LAYOUT
  5
0
330
0
100
AcDbPlotSettings
  1

  2
DWFx ePlot (XPS Compatible).pc3
  4
ANSI_A_(8.50_x_11.00_Inches)
  6

 40
5.793749809265136
 41
17.79375076293945
 42
5.793746948242187
 43
17.79376220703125
 44
215.8999938964844
 45
279.3999938964844
 46
0.0
 47
0.0
 48
0.0
 49
0.0
140
0.0
141
0.0
142
1.0
143
14.5331733075991
 70
11952
 72
0
 73
1
 74
0
  7

 75
0
147
0.068808097091715
148
114.9814160680965
149
300.291024640228
100
AcDbLayout
  1
Model
 70
1
 71
0
 10
0.0
 20
0.0
 11
12.0
 21
9.0
 12
0.0
 22
0.0
 32
0.0
 14
0.0
 24
0.0
 34
0.0
 15
0.0
 25
0.0
 35
0.0
146
0.0
 13
0.0
 23
0.0
 33
0.0
 16
1.0
 26
0.0
 36
0.0
 17
0.0
 27
1.0
 37
0.0
 76
0
330
0
"""


def create_model_space_layout(object_section, block_record_handle):
    # Problem: ezdxf was not designed to handle the absence of model space layout

    dwg = object_section.drawing
    entitydb = dwg.entitydb

    tags = ClassifiedTags.from_text(_MODEL_SPACE_LAYOUT_TPL)
    layout_handle = entitydb.handles.next()  # create new unique handle
    tags.replace_handle(layout_handle)  # set entity handle

    entitydb.add_tags(tags)  # add layout entity to entity database
    object_section.add_handle(layout_handle)  # add layout entity to objects section

    acdblayout = tags.get_subclass('AcDbLayout')
    acdblayout.set_first(330, block_record_handle)  # link to block record
    return Layout(dwg, layout_handle)

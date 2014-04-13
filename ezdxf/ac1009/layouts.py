# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .graphicsfactory import GraphicsFactory
from ..entityspace import EntitySpace
from ..query import EntityQuery


class DXF12Layouts(object):
    """ The Layout container.
    """
    def __init__(self, drawing):
        entityspace = drawing.sections.entities.get_entityspace()
        self._modelspace = DXF12Layout(entityspace, drawing.dxffactory, 0)
        self._paperspace = DXF12Layout(entityspace, drawing.dxffactory, 1)

    def modelspace(self):
        return self._modelspace

    def get(self, name=""):
        # AC1009 supports only one paperspace/layout
        return self._paperspace

    def names(self):
        return []

    def get_layout_for_entity(self, entity):
        # paperspace attribute defaults to 0 if not present
        return self._paperspace if entity.dxf.paperspace else self._modelspace


class BaseLayout(GraphicsFactory):
    """ Base class for DXF12Layout() and DXF12BlockLayout()

    Entities are wrapped into class GraphicEntity() or inherited.
    """
    def __init__(self, dxffactory, entityspace):
        super(BaseLayout, self).__init__(dxffactory)
        self._entityspace = entityspace

    @property
    def entitydb(self):
        return self._dxffactory.entitydb

    def build_and_add_entity(self, type_, dxfattribs):
        """ Create entity in drawing database and add entity to the entity space.

        :param str type_: DXF type string, like 'LINE', 'CIRCLE' or 'LWPOLYLINE'
        :param dict dxfattribs: DXF attributes for the new entity
        """
        entity = self.build_entity(type_, dxfattribs)
        self.add_entity(entity)
        return entity

    def build_entity(self, type_, dxfattribs):
        """ Create entity in drawing database, returns a wrapper class inherited from GraphicEntity().

        :param str type_: DXF type string, like 'LINE', 'CIRCLE' or 'LWPOLYLINE'
        :param dict dxfattribs: DXF attributes for the new entity
        """
        entity = self._dxffactory.create_db_entry(type_, dxfattribs)
        self._set_paperspace(entity)
        return entity

    def add_entity(self, entity):
        """ Add entity to entity space.
        """
        self._entityspace.append(entity.dxf.handle)
        entity.set_layout(self)
        self._set_paperspace(entity)

    def delete_entity(self, entity, database=True):
        """ Delete entity from entity space and if *database* is *True* also from the entity database.
        """
        handle = entity.dxf.handle
        self._entityspace.remove(handle)
        if database:
            del self.entitydb[handle]
        entity.dxf.paperspace = -1  # set invalid paper space

    def _set_paperspace(self, entity):
        pass

    def get_entity_by_handle(self, handle):
        """ Get entity by handle as GraphicEntity() or inherited.
        """
        return self._dxffactory.wrap_handle(handle)

    def get_entity_by_handle_with_layout(self, handle):
        """ Get entity by handle as GraphicEntity() or inherited.
        """
        entity = self.get_entity_by_handle(handle)
        entity.set_layout(self)
        return entity

    def get_entity_at_index(self, index):
        """ Get entity at position index as GraphicEntity() or inherited.
        """
        return self.get_entity_by_handle(self._entityspace[index])

    def get_index_of_entity(self, entity):
        """ Get position/index of entity in entity space.
        """
        return self._entityspace.index(entity.dxf.handle)

    def insert_entities(self, index, entities):
        """ Insert entities to entity space.
        """
        handles = [entity.dxf.handle for entity in entities]
        self._entityspace[index:index] = handles

    def remove_entities(self, index, count=1):
        """ Remove entities from entity space.
        """
        self._entityspace[index:index + count] = []

    def get_cursor(self, entity=None):
        cursor = LayoutCursor(self)
        if entity is not None:
            cursor.goto_entity(entity)
        return cursor

    # noinspection PyTypeChecker
    def query(self, query='*'):
        return EntityQuery(iter(self), query)


class LayoutCursor(object):
    def __init__(self, layout):
        self.layout = layout
        self.pos = 0

    def entity(self):
        return self.layout.get_entity_at_index(self.pos)

    def next_entity(self):
        self.pos += 1
        return self.entity()

    def goto_entity(self, entity):
        self.pos = self.layout.get_index_of_entity(entity)

    def skip(self, distance=1):
        self.pos += distance


class DXF12Layout(BaseLayout):
    """ Layout representation
    """

    def __init__(self, entityspace, dxffactory, paperspace=0):
        super(DXF12Layout, self).__init__(dxffactory, entityspace)
        self._paperspace = paperspace

    # start of public interface

    def __iter__(self):
        """ Iterate over all layout entities, yielding class GraphicEntity() or inherited.
        """
        for entity in self._iter_all_entities():
            if entity.dxf.paperspace == self._paperspace:
                entity.set_layout(self)
                yield entity

    def __contains__(self, entity):
        """ Returns True if layout contains entity else False. entity can be an entity handle as string or a wrapped
        dxf entity.
        """
        if not hasattr(entity, 'dxf'):  # entity is a handle and not a wrapper class
            entity = self.get_entity_by_handle(entity)
        return entity.dxf.paperspace == self._paperspace

    # end of public interface

    def _iter_all_entities(self):
        """Iterate over all entities in the drawing entity space as wrapped entities.
        """
        for handle in self._entityspace:
            yield self.get_entity_by_handle(handle)

    def _set_paperspace(self, entity):
        entity.dxf.paperspace = self._paperspace


class DXF12BlockLayout(BaseLayout):
    """ BlockLayout has the same factory-function as Layout, but is managed
    in the BlocksSection() class. It represents a DXF Block definition.

    _block_handle: db handle to BLOCK entity
    _endblk_handle: db handle to ENDBLK entity
    _entityspace is the block content
    """
    def __init__(self, entitydb, dxffactory, block_handle, endblk_handle):
        super(DXF12BlockLayout, self).__init__(dxffactory, EntitySpace(entitydb))
        self._block_handle = block_handle
        self._endblk_handle = endblk_handle

    # start of public interface

    def __iter__(self):
        """ Iterate over all block entities, yielding class GraphicEntity() or inherited.
        """
        for handle in self._entityspace:
            yield self.get_entity_by_handle_with_layout(handle)

    def __contains__(self, entity):
        """ Returns True if block contains entity else False. *entity* can be a handle-string, Tags(),
        ClassifiedTags() or a wrapped entity.
        """
        if hasattr('get_handle', entity):
            handle = entity.get_handle()
        elif hasattr('dxf', entity):  # it's a wrapped entity
            handle = entity.dxf.handle
        else:
            handle = entity
        return handle in self._entityspace

    @property
    def block(self):
        return self.get_entity_by_handle_with_layout(self._block_handle)

    @property
    def endblk(self):
        return self.get_entity_by_handle_with_layout(self._endblk_handle)

    @property
    def name(self):
        return self.block.dxf.name

    @name.setter
    def name(self, new_name):
        block = self.block
        block.dxf.name = new_name
        block.dxf.name2 = new_name

    def add_attdef(self, tag, insert, dxfattribs=None):
        """ Create an ATTDEF entity in the drawing database and add it to the block entity space.
        """
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['tag'] = tag
        dxfattribs['insert'] = insert
        return self.build_and_add_entity('ATTDEF', dxfattribs)

    # end of public interface

    def add_entity(self, entity):
        """ Add entity to the block entity space.
        """
        self.add_handle(entity.dxf.handle)
        entity.set_layout(self)

    def add_handle(self, handle):
        """ Add entity by handle to the block entity space.
        """
        self._entityspace.append(handle)

    def write(self, stream):
        def write_tags(handle):
            tags = self._entityspace.get_tags_by_handle(handle)
            tags.write(stream)

        write_tags(self._block_handle)
        self._entityspace.write(stream)
        write_tags(self._endblk_handle)

    def attdefs(self):
        """ Iterate over all ATTDEF entities.
        """
        return (entity for entity in self if entity.dxftype() == 'ATTDEF')



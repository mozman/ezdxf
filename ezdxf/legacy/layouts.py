# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..graphicsfactory import GraphicsFactory
from ..entityspace import EntitySpace
from ..query import EntityQuery
from ..groupby import groupby


class DXF12Layouts(object):
    """
    The Layout container.
    """
    def __init__(self, drawing):
        entities = drawing.sections.entities
        model_space = entities.get_layout_space(0)
        self._modelspace = DXF12Layout(model_space, drawing.dxffactory, 0)
        paper_space = entities.get_layout_space(1)
        self._paperspace = DXF12Layout(paper_space, drawing.dxffactory, 1)

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
    """
    Base class for DXF12Layout() and DXF12BlockLayout()

    Entities are wrapped into class GraphicEntity() or inherited.
    """
    def __init__(self, dxffactory, entity_space):
        super(BaseLayout, self).__init__(dxffactory)
        self._entity_space = entity_space

    def __len__(self):
        return len(self._entity_space)

    def __iter__(self):
        """
        Iterate over all block entities, yielding class GraphicEntity() or inherited.
        """
        wrap = self._dxffactory.wrap_handle
        for handle in self._entity_space:
            yield wrap(handle)

    @property
    def entitydb(self):
        return self._dxffactory.entitydb

    @property
    def drawing(self):
        return self._dxffactory.drawing

    def build_and_add_entity(self, type_, dxfattribs):
        """
        Create entity in drawing database and add entity to the entity space.

        Args:
            type_ (str): DXF type string, like 'LINE', 'CIRCLE' or 'LWPOLYLINE'
            dxfattribs (dict): DXF attributes for the new entity

        """
        entity = self.build_entity(type_, dxfattribs)
        self.add_entity(entity)
        return entity

    def build_entity(self, type_, dxfattribs):
        """
        Create entity in drawing database, returns a wrapper class inherited from GraphicEntity().

        Adds entity to the drawing database.

        Args:
            type_ (str): DXF type string, like 'LINE', 'CIRCLE' or 'LWPOLYLINE'
            dxfattribs(dict): DXF attributes for the new entity

        """
        entity = self._dxffactory.create_db_entry(type_, dxfattribs)
        self._set_paperspace(entity)
        return entity

    def add_entity(self, entity):
        """
        Add entity to entity space but not to the drawing database.
        """
        self._entity_space.append(entity.dxf.handle)
        self._set_paperspace(entity)

    def unlink_entity(self, entity):
        """
        Delete entity from entity space but not from the drawing database.
        """
        self._entity_space.delete_entity(entity)
        entity.dxf.paperspace = -1  # set invalid paper space

    def delete_entity(self, entity):
        """
        Delete entity from entity space and drawing database.
        """
        self.entitydb.delete_entity(entity)  # 1. delete from drawing database
        self.unlink_entity(entity)  # 2. unlink from entity space

    def delete_all_entities(self):
        """
        Delete all entities of this layout from entity space and from drawing database.

        Deletes only entities from this layout. Important because ALL layout entities are stored in just one entity
        space.
        """
        # noinspection PyTypeChecker
        for entity in list(self):  # temp list, because delete modifies the base data structure of the iterator
            self.delete_entity(entity)

    def _set_paperspace(self, entity):
        pass

    def get_entity_by_handle(self, handle):
        """
        Get entity by handle as GraphicEntity() or inherited.
        """
        return self._dxffactory.wrap_handle(handle)

    # noinspection PyTypeChecker
    def query(self, query='*'):
        return EntityQuery(iter(self), query)

    def groupby(self, dxfattrib="", key=None):
        return groupby(iter(self), dxfattrib, key)


class DXF12Layout(BaseLayout):
    """
    Layout representation
    """
    def __init__(self, entityspace, dxffactory, paperspace=0):
        super(DXF12Layout, self).__init__(dxffactory, entityspace)
        self._paperspace = paperspace

    # start of public interface

    def __contains__(self, entity):
        """
        Returns True if layout contains entity else False. entity can be an entity handle as string or a wrapped
        dxf entity.

        """
        if not hasattr(entity, 'dxf'):  # entity is a handle and not a wrapper class
            entity = self.get_entity_by_handle(entity)
        return entity.dxf.paperspace == self._paperspace

    # end of public interface

    def _set_paperspace(self, entity):
        entity.dxf.paperspace = self._paperspace

    @property
    def layout_key(self):
        return self._paperspace


class DXF12BlockLayout(BaseLayout):
    """
    BlockLayout has the same factory-function as Layout, but is managed
    in the BlocksSection() class. It represents a DXF Block definition.

    Attributes:
        _block_handle: db handle to BLOCK entity
        _endblk_handle: db handle to ENDBLK entity
        _entityspace: is the block content

    """
    def __init__(self, entitydb, dxffactory, block_handle, endblk_handle):
        super(DXF12BlockLayout, self).__init__(dxffactory, EntitySpace(entitydb))
        self._block_handle = block_handle
        self._endblk_handle = endblk_handle

    # start of public interface

    def __contains__(self, entity):
        """
        Returns True if block contains entity else False. *entity* can be a handle-string, Tags(),
        ExtendedTags() or a wrapped entity.

        """
        if hasattr('get_handle', entity):
            handle = entity.get_handle()
        elif hasattr('dxf', entity):  # it's a wrapped entity
            handle = entity.dxf.handle
        else:
            handle = entity
        return handle in self._entity_space

    @property
    def block(self):
        """ Get associated BLOCK entity. """
        return self.get_entity_by_handle(self._block_handle)

    @property
    def endblk(self):
        """ Get associated ENDBLK entity. """
        return self.get_entity_by_handle(self._endblk_handle)

    @property
    def name(self):
        """ Get block name """
        return self.block.dxf.name

    @name.setter
    def name(self, new_name):
        """ Set block name """
        block = self.block
        block.dxf.name = new_name
        block.dxf.name2 = new_name

    def add_attdef(self, tag, insert=(0, 0), text='', dxfattribs=None):
        """
        Create an ATTDEF entity in the drawing database and add it to the block entity space.

        Args:
            tag (str): attribute name as string without spaces
            insert: attribute insert point relative to blcok origin (0, 0, 0)
            text (str): preset text for attribute

        """
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['tag'] = tag
        dxfattribs['insert'] = insert
        dxfattribs['text'] = text
        return self.build_and_add_entity('ATTDEF', dxfattribs)

    def attdefs(self):
        """
        Iterate over all ATTDEF entities.
        """
        return (entity for entity in self if entity.dxftype() == 'ATTDEF')

    def has_attdef(self, tag):
        """
        Check if ATTDEF for *tag* exists.

        Args:
            tag (str): tag name
        """
        return self.get_attdef(tag) is not None

    def get_attdef(self, tag):
        """
        Get attached ATTDEF entity by *tag*.

        Args:
            tag (str): tag name

        Returns:
            Attdef() object

        """
        for attdef in self.attdefs():
            if tag == attdef.dxf.tag:
                return attdef

    def get_attdef_text(self, tag, default=None):
        """
        Get content text of attached ATTDEF entity *tag*.

        Args:
            tag (str): tag name
            default (str): default value if tag is absent

        Returns:
            content text as str

        """
        attdef = self.get_attdef(tag)
        if attdef is None:
            return default
        return attdef.dxf.text

    # end of public interface

    def add_entity(self, entity):
        """
        Add entity to the block entity space.
        """
        self.add_handle(entity.dxf.handle)

    def add_handle(self, handle):
        """
        Add entity by handle to the block entity space.
        """
        self._entity_space.append(handle)

    def write(self, tagwriter):
        def write_tags(handle):
            tags = self._entity_space.get_tags_by_handle(handle)
            tagwriter.write_tags(tags)

        write_tags(self._block_handle)
        self._entity_space.write(tagwriter)
        write_tags(self._endblk_handle)

    def delete_all_entities(self):
        # 1. delete from database
        for handle in self._entity_space:
            del self.entitydb[handle]
        # 2. delete from entity space
        self._entity_space.delete_all_entities()

    def destroy(self):
        self.delete_all_entities()
        del self.entitydb[self._block_handle]
        del self.entitydb[self._endblk_handle]

    def get_const_attdefs(self):
        """
        Returns a generator for constant ATTDEF entities.
        """
        return (attdef for attdef in self.attdefs() if attdef.is_const)


# Created: 2019-02-18
# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, cast
from ezdxf.lldxf.const import DXFValueError, DXFStructureError
from ezdxf.query import EntityQuery
from ezdxf.groupby import groupby
from ezdxf.entitydb import EntityDB
from ezdxf.graphicsfactory import CreatorInterface

if TYPE_CHECKING:
    from ezdxf.eztypes import BlockRecord, DXFGraphic, Dictionary, KeyFunc, Polyline

SUPPORTED_FOREIGN_ENTITY_TYPES = {
    'ARC', 'LINE', 'CIRCLE', 'ELLIPSE', 'POINT', 'LWPOLYLINE', 'SPLINE', '3DFACE', 'SOLID', 'TRACE', 'SHAPE',
    'POLYLINE', 'MESH', 'TEXT', 'MTEXT', 'HATCH', 'ATTRIB', 'ATTDEF',
}


class BaseLayout(CreatorInterface):
    def __init__(self, block_record: 'BlockRecord'):
        super().__init__(block_record.doc)
        self.entity_space = block_record.entity_space
        self.block_record = block_record  # is the central management structure

    @property
    def block_record_handle(self):
        """ Returns block record handle. (internal API) """
        return self.block_record.dxf.handle

    @property
    def layout_key(self) -> str:
        """ Returns the layout key as hex string.

        The layout key is the handle of the associated BLOCK_RECORD entry in the BLOCK_RECORDS table.

        (internal API)
        """
        return self.block_record.dxf.handle

    @property
    def entitydb(self) -> 'EntityDB':
        """ Returns drawing entity database. (internal API) """
        return self.doc.entitydb

    @property
    def is_alive(self):
        """ ``False`` if layout is deleted. """
        return self.block_record.is_alive

    @property
    def is_active_paperspace(self) -> bool:
        """ ``True`` if is active layout. """
        return self.block_record.is_active_paperspace

    @property
    def is_any_paperspace(self) -> bool:
        """ ``True`` if is any kind of paperspace layout. """
        return self.block_record.is_any_paperspace

    @property
    def is_modelspace(self) -> bool:
        """ ``True`` if is modelspace layout. """
        return self.block_record.is_modelspace

    @property
    def is_any_layout(self) -> bool:
        """ ``True`` if is any kind of modelspace or paperspace layout. """
        return self.block_record.is_any_layout

    @property
    def is_block_layout(self) -> bool:
        """ ``True`` if not any kind of modelspace or paperspace layout, just a regular block definition. """
        return self.block_record.is_block_layout

    def get_extension_dict(self) -> 'Dictionary':
        """
        Returns the associated extension dictionary, creates a new one if necessary.

        """
        return self.block_record.get_extension_dict()

    def __len__(self) -> int:
        """ Returns count of entities owned by the layout. """
        return len(self.entity_space)

    def __iter__(self) -> Iterable['DXFGraphic']:
        """ Returns iterable of all drawing entities in this layout. """
        return iter(self.entity_space)

    def __getitem__(self, index):
        """ Get entity at `index`.

        The underlying data structure for storing entities is organized like a standard Python list, therefore `index`
        can be any valid list indexing or slicing term, like a single index ``layout[-1]`` to get the last entity, or
        an index slice ``layout[:10]`` to get the first 10 or less entities as ``List[DXFGraphic]``.

        """
        return self.entity_space[index]

    def rename(self, name) -> None:
        pass

    def add_entity(self, entity: 'DXFGraphic') -> None:
        """
        Add an existing :class:`DXFGraphic` entity to a layout, but be sure to unlink (:meth:`~BaseLayout.unlink_entity`)
        entity from the previous owner layout. Adding entities from a different DXF drawing is not supported.

        """
        if entity.doc != self.doc:
            raise DXFStructureError('Adding entities from a different DXF drawing is not supported.')

        self.block_record.add_entity(entity)

    def add_foreign_entity(self, entity: 'DXFGraphic', copy=True) -> None:
        """
        Add a foreign DXF entity to a layout, this foreign entity could be from another DXF document or an entity
        without an assigned DXF document. The intention of this method is to add **simple** entities from other
        DXF documents or from DXF iterator add-ons, for more complex operations use the
        :mod:`~ezdxf.addons.importer` add-on. Especially objects with BLOCK section (INSERT, DIMENSION,
        MLEADER) or OBJECTS section dependencies (IMAGE, UNDERLAY) can not be supported by
        this simple method.

        Not all DXF types are supported and every dependency or resource reference from another DXF document will be
        removed. If the entity is part of another DXF document, it will be unlinked from this document and its
        entity database if argument `copy` is ``False``, else the entity will be copied. Unassigned entities will just
        be added.

        Supported DXF types:

            - POINT
            - LINE
            - CIRCLE
            - ARC
            - ELLIPSE
            - LWPOLYLINE
            - SPLINE
            - POLYLINE
            - 3DFACE
            - SOLID
            - TRACE
            - SHAPE
            - MESH
            - ATTRIB
            - ATTDEF
            - TEXT
            - MTEXT
            - HATCH

        Args:
            entity: DXF entity to copy or move
            copy: if ``True`` copy entity from other document else unlink from other document

        .. versionadded:: 0.11.1

        """
        foreign_doc = entity.doc
        dxftype = entity.dxftype()
        if dxftype not in SUPPORTED_FOREIGN_ENTITY_TYPES:
            raise DXFValueError(f'Unsupported entity type: {dxftype}.')
        if foreign_doc is self.doc:
            raise DXFValueError('Entity from same DXF document.')

        if foreign_doc is not None:
            if copy:
                entity = entity.copy()
            else:
                # unlink entity from other database without destroying
                del foreign_doc.entitydb[entity.dxf.handle]
                for e in entity.linked_entities():
                    del foreign_doc.entitydb[e.dxf.handle]

                # unlink from layout
                layout = entity.get_layout()
                if layout is not None:
                    layout.unlink_entity(entity)

        def remove_dependencies(e):
            if e is None:
                return
            e.dxf.owner = None
            e.dxf.handle = None
            e.reactors = None
            e.extension_dict = None
            e.appdata = None
            e.xdata = None
            e.embedded_objects = None

        remove_dependencies(entity)
        if dxftype == 'POLYLINE':
            entity = cast('Polyline', entity)
            for v in entity.vertices:
                remove_dependencies(v)
            remove_dependencies(entity.seqend)

        # remove resources
        if entity.dxf.layer not in self.doc.layers:
            entity.dxf.layer = '0'

        if entity.dxf.linetype not in self.doc.linetypes:
            entity.dxf.linetype = 'BYLAYER'

        entity.dxf.discard('material_handle')
        entity.dxf.discard('visualstyle_handle')
        entity.dxf.discard('plotstyle_enum')
        entity.dxf.discard('plotstyle_handle')

        # TEXT, ATTRIB, ATTDEF  and MTEXT
        if entity.dxf.hasattr('style') and  entity.dxf.style not in self.doc.styles:
            entity.dxf.style = 'Standard'

        if dxftype == 'HATCH':
            entity.unassociate()

        # add to this document
        self.entitydb.add(entity)
        entity.doc = self.doc
        # add to this layout
        self.add_entity(entity)

    def unlink_entity(self, entity: 'DXFGraphic') -> None:
        """
        Unlink `entity` from layout but does not delete entity from the drawing database, this removes `entity` just
        from the layout entity space.

        """
        self.block_record.unlink_entity(entity)

    def delete_entity(self, entity: 'DXFGraphic') -> None:
        """ Delete `entity` from layout entity space and the drawing database, this destroys the `entity`. """
        self.block_record.delete_entity(entity)

    def delete_all_entities(self) -> None:
        """
        Delete all entities from layout entity space and from drawing database, this destroys all entities in this
        layout.
        """
        # noinspection PyTypeChecker
        for entity in list(self):  # temp list, because delete modifies the base data structure of the iterator
            self.delete_entity(entity)

    def get_entity_by_handle(self, handle: str) -> 'DXFGraphic':
        """
        Get entity by handle as GraphicEntity() or inherited.

        (internal API)
        """
        return self.entitydb[handle]

    def query(self, query: str = '*') -> EntityQuery:
        """
        Get all DXF entities matching the :ref:`entity query string`.

        """
        return EntityQuery(iter(self), query)

    def groupby(self, dxfattrib: str = "", key: 'KeyFunc' = None) -> dict:
        """
        Returns a ``dict`` of entity lists, where entities are grouped by a `dxfattrib` or a `key` function.

        Args:
            dxfattrib: grouping by DXF attribute like ``'layer'``
            key: key function, which accepts a :class:`DXFGraphic` entity as argument and returns the grouping key of an
                 entity or ``None`` to ignore the entity. Reason for ignoring: a queried DXF attribute is not
                 supported by entity.

        """
        return groupby(iter(self), dxfattrib, key)

    def move_to_layout(self, entity: 'DXFGraphic', layout: 'BaseLayout') -> None:
        """
        Move entity to another layout.

        Args:
            entity: DXF entity to move
            layout: any layout (modelspace, paperspace, block) from **same** drawing

        """
        if entity.doc != layout.doc:
            raise DXFStructureError('Moving between different DXF drawings is not supported.')

        try:
            self.unlink_entity(entity)
        except ValueError:
            raise DXFValueError('Layout does not contain entity.')
        else:
            layout.add_entity(entity)

    def destroy(self) -> None:
        """ Delete all linked resources. (internal API) """
        # block_records table is owner of block_record has to delete it
        # the block_record is the owner of the entities and deletes them all
        self.doc.block_records.remove(self.block_record.dxf.name)

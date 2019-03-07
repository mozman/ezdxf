# Created: 2019-02-18
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, Iterable, List, Hashable
from ezdxf.lldxf.const import DXFValueError
from ezdxf.query import EntityQuery
from ezdxf.groupby import groupby
from ezdxf.entitydb import EntityDB
from ezdxf.graphicsfactory2 import CreatorInterface

if TYPE_CHECKING:
    from ezdxf.eztypes2 import BlockRecord, DXFGraphic


class BaseLayout(CreatorInterface):
    def __init__(self, block_record: 'BlockRecord'):
        super().__init__(block_record.doc)
        self.entity_space = block_record.entity_space
        self.block_record = block_record  # is the central management structure

    @property
    def block_record_handle(self):
        return self.block_record.dxf.handle

    @property
    def layout_key(self) -> str:
        """
        Returns the layout key as string.

        The layout key is the handle of the associated ``BLOCK_RECORD`` entry in the ``BLOCK_RECORDS`` table.

        """
        return self.block_record.dxf.handle

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    @property
    def is_alive(self):
        return self.block_record.is_alive

    @property
    def is_active_paperspace(self) -> bool:
        """ True if is "active" layout. """
        return self.block_record.is_active_paperspace

    @property
    def is_any_paperspace(self) -> bool:
        """ True if is any kind of paperspace layout. """
        return self.block_record.is_any_paperspace

    @property
    def is_modelspace(self)->bool:
        """ True if is modelspace layout. """
        return self.block_record.is_modelspace

    @property
    def is_any_layout(self)->bool:
        """ True if is any kind of modelspace or paperspace layout. """
        return self.block_record.is_any_layout

    @property
    def is_block_layout(self)->bool:
        """ True if not any kind of modelspace or paperspace layout, just a regular block definition. """
        return self.block_record.is_block_layout

    def __len__(self) -> int:
        """
        Entities count.

        """
        return len(self.entity_space)

    def __iter__(self) -> Iterable['DXFGraphic']:
        """
        Iterate over all drawing entities in this layout.

        Returns: :class:`DXFGraphic`

        """
        return iter(self.entity_space)

    def __getitem__(self, item):
        return self.entity_space[item]

    def rename(self, name) -> None:
        pass

    def add_entity(self, entity: 'DXFGraphic') -> None:
        """
        Add an existing :class:`DXFGraphic` to a layout, but be sure to unlink (:meth:`~Layout.unlink_entity()`) first the entity
        from the previous owner layout.

        """
        self.block_record.add_entity(entity)

    def unlink_entity(self, entity: 'DXFGraphic') -> None:
        """
        Unlink `entity` from layout but does not delete entity from the drawing database.

        Removes `entity` just from  entity space but not from the drawing database.

        Args:
            entity: :class:`DXFGraphic`

        """
        self.block_record.unlink_entity(entity)

    def delete_entity(self, entity: 'DXFGraphic') -> None:
        """
        Delete `entity` from layout (entity space) and drawing database.

        Args:
            entity: :class:`DXFGraphic`

        """
        self.block_record.delete_entity(entity)

    def delete_all_entities(self) -> None:
        """
        Delete all entities from Layout (entity space) and from drawing database.

        """
        # noinspection PyTypeChecker
        for entity in list(self):  # temp list, because delete modifies the base data structure of the iterator
            self.delete_entity(entity)

    def get_entity_by_handle(self, handle: str) -> 'DXFGraphic':
        """
        Get entity by handle as GraphicEntity() or inherited.

        """
        return self.entitydb[handle]

    def query(self, query='*') -> EntityQuery:
        """
        Get all DXF entities matching the :ref:`entity query string`.

        Args:
            query: eintity query string

        Returns: :class:`EntityQuery`

        """
        return EntityQuery(iter(self), query)

    def groupby(self, dxfattrib: str = "", key: 'KeyFunc' = None) -> Dict[Hashable, List['DXFGraphic']]:
        """
        Returns a dict of entity lists, where entities are grouped by a `dxfattrib` or a `key` function.

        Args:
            dxfattrib: grouping by DXF attribute like "layer"
            key: key function, which accepts a :class:`DXFGraphic` as argument, returns grouping key of this entity or
                 None to ignore this object. Reason for ignoring: a queried DXF attribute is not supported by this
                 entity.

        """
        return groupby(iter(self), dxfattrib, key)

    def move_to_layout(self, entity: 'DXFGraphic', layout: 'BaseLayout') -> None:
        """
        Move entity from block layout to another layout.

        Args:
            entity: DXF entity to move
            layout: any layout (model space, paper space, block)

        """
        try:
            self.unlink_entity(entity)
        except ValueError:
            raise DXFValueError('Layout does not contain entity.')
        else:
            layout.add_entity(entity)

    def destroy(self) -> None:
        # block_records table is owner of block_record has to delete it
        # the block_record is the owner of the entities and deletes them all
        self.doc.block_records.remove(self.block_record.dxf.name)

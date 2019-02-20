# Created: 2019-02-18
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, Iterable, List, Hashable
from ezdxf.lldxf.const import DXFValueError, MODEL_SPACE, PAPER_SPACE
from ezdxf.query import EntityQuery
from ezdxf.groupby import groupby
from ezdxf.entitydb import EntitySpace, EntityDB
from ezdxf.graphicsfactory2 import CreatorInterface

if TYPE_CHECKING:
    from ezdxf.drawing2 import Drawing
    from ezdxf.entities.blockrecord import BlockRecord
    from ezdxf.entities.block import Block, EndBlk
    from ezdxf.entities.dxfentity import DXFEntity


class BaseLayout(CreatorInterface):
    def __init__(self,
                 block_record: 'BlockRecord',
                 doc: 'Drawing' = None,
                 entity_space: EntitySpace = None,
                 ):
        super().__init__(doc)
        self.entity_space = entity_space or EntitySpace()
        self.block_record = block_record

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
    def is_active_paperspace(self):
        return self.block_record.dxf.name.lower() in PAPER_SPACE

    @property
    def is_modelspace(self):
        return self.block_record.dxf.name.lower() in MODEL_SPACE

    def __len__(self) -> int:
        """
        Entities count.

        """
        return len(self.entity_space)

    def __iter__(self) -> Iterable['DXFEntity']:
        """
        Iterate over all drawing entities in this layout.

        Returns: :class:`DXFEntity`

        """
        return iter(self.entity_space)

    def rename(self, name) -> None:
        pass

    def add_entity(self, entity: 'DXFEntity') -> None:
        """
        Add an existing :class:`DXFEntity` to a layout, but be sure to unlink (:meth:`~Layout.unlink_entity()`) first the entity
        from the previous owner layout.

        """
        self.entity_space.add(entity)
        entity.assign_layout(self)

    def unlink_entity(self, entity: 'DXFEntity') -> None:
        """
        Unlink `entity` from layout but does not delete entity from the drawing database.

        Removes `entity` just from  entity space but not from the drawing database.

        Args:
            entity: :class:`DXFEntity`

        """
        self.entity_space.remove(entity)
        entity.dxf.paperspace = -1  # set invalid paper space
        entity.dxf.owner = '0'

    def delete_entity(self, entity: 'DXFEntity') -> None:
        """
        Delete `entity` from layout (entity space) and drawing database.

        Args:
            entity: :class:`DXFEntity`

        """
        self.unlink_entity(entity)  # 1. unlink from entity space
        self.entitydb.delete_entity(entity)  # 2. delete from drawing database


    def delete_all_entities(self) -> None:
        """
        Delete all entities from Layout (entity space) and from drawing database.

        """
        # noinspection PyTypeChecker
        for entity in list(self):  # temp list, because delete modifies the base data structure of the iterator
            self.delete_entity(entity)

    def get_entity_by_handle(self, handle: str) -> 'DXFEntity':
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

    def groupby(self, dxfattrib: str = "", key: 'KeyFunc' = None) -> Dict[Hashable, List['DXFEntity']]:
        """
        Returns a dict of entity lists, where entities are grouped by a `dxfattrib` or a `key` function.

        Args:
            dxfattrib: grouping by DXF attribute like "layer"
            key: key function, which accepts a :class:`DXFEntity` as argument, returns grouping key of this entity or
                 None to ignore this object. Reason for ignoring: a queried DXF attribute is not supported by this
                 entity.

        """
        return groupby(iter(self), dxfattrib, key)

    def move_to_layout(self, entity: 'DXFEntity', layout: 'BaseLayout') -> None:
        """
        Move entity from block layout to another layout.

        Args:
            entity: DXF entity to move
            layout: any layout (model space, paper space, block)

        """
        if entity in self.entity_space:
            self.unlink_entity(entity)
            layout.add_entity(entity)
        else:
            raise DXFValueError('Layout does not contain entity.')

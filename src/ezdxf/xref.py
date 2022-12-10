#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

"""
Resource management module for transferring DXF resources between documents.

Planning state!!!

"""
from __future__ import annotations
from typing import Optional, Sequence
from typing_extensions import Protocol

from ezdxf.lldxf.const import DXFError, DXFTableEntryError
from ezdxf.document import Drawing
from ezdxf.layouts import BaseLayout
from ezdxf.sections.table import Table

from ezdxf.entities import (
    is_graphic_entity,
    is_dxf_object,
    DXFEntity,
    DXFClass,
    factory,
    BlockRecord,
)


__all__ = ["ResourceTransfer"]


class ResourceTransfer(Protocol):
    def add_entity(self, entity: DXFEntity, block_id: int = 0):
        ...

    def add_block(self, entities: Sequence[DXFEntity], block_id: int) -> None:
        ...

    def get_entity_copy(self, entity_id: int, block_id: int = 0) -> Optional[DXFEntity]:
        ...

    def get_block_copy(self, block_id: int) -> Sequence[DXFEntity]:
        ...

    def register_handle(self, entity: DXFEntity, name: str) -> None:
        ...

    def register_layer(self, entity: DXFEntity) -> None:
        ...

    def register_linetype(self, entity: DXFEntity) -> None:
        ...

    def register_style(self, entity: DXFEntity) -> None:
        ...

    def register_dimstyle(self, entity: DXFEntity) -> None:
        ...

    def transfer_handle(self, source: DXFEntity, copy: DXFEntity, name: str):
        ...

    def transfer_layer(self, source: DXFEntity, copy: DXFEntity) -> None:
        ...

    def transfer_linetype(self, source: DXFEntity, copy: DXFEntity) -> None:
        ...

    def transfer_style(self, source: DXFEntity, copy: DXFEntity) -> None:
        ...

    def transfer_dimstyle(self, source: DXFEntity, copy: DXFEntity) -> None:
        ...


def import_entities(entities: Sequence[DXFEntity], target: BaseLayout):
    if len(entities) == 0:
        return

    doc: Drawing = target.doc
    assert doc is not None, "a valid target document is mandatory"
    objects = doc.objects
    transfer = Transfer()
    for e in entities:
        transfer.add_entity(e, block_id=0)

    cpm = CopyMachine()
    transfer.copied_blocks = cpm.copy_blocks(transfer.source_blocks)
    if cpm.classes:
        doc.classes.register(cpm.classes)

    replace: list[tuple[DXFEntity, DXFEntity]] = []

    def add_table_entry(table: Table):
        existing_entry = table.get(entity)  # type: ignore
        if existing_entry is None:
            table.add_entry(entity)
        else:
            replace.append((entity, existing_entry))

    # process resource objects and entities without assigned layout: block_id == 0
    for entity_id, entity in cpm.copies.get(0).items():
        if entity.dxf.owner is not None:
            continue  # already processed!

        # 1. assign entity to document
        factory.bind(entity, doc)

        # 2. add copied resources to tables and collections
        dxftype = entity.dxftype()
        if dxftype == "LAYER":
            add_table_entry(doc.layers)
        elif dxftype == "LINETYPE":
            add_table_entry(doc.linetypes)
        elif dxftype == "STYLE":
            add_table_entry(doc.styles)
        elif dxftype == "DIMSTYLE":
            add_table_entry(doc.dimstyles)
        elif dxftype == "APPID":
            try:
                doc.appids.add_entry(entity)  # type: ignore
            except DXFTableEntryError:
                pass
        elif dxftype == "UCS":
            add_table_entry(doc.ucs)
        elif dxftype == "BLOCK_RECORD":
            assert isinstance(entity, BlockRecord)
            if doc.block_records.has_entry(entity.dxf.name):
                # resolve resource conflicts
                count = 0
                new_name = entity.dxf.name
                while doc.block_records.has_entry(new_name):
                    # todo: arrow block need special names?
                    new_name = entity.dxf.name + f"_{count}"
                    count += 1
                entity.rename(new_name)
            doc.block_records.add_entry(entity)
            doc.blocks.add(entity)  # create BlockLayout
        elif dxftype == "MATERIAL":
            add_collection_entry(doc.materials, entity)
        elif dxftype == "MLINESTYLE":
            add_collection_entry(doc.mline_styles, entity)
        elif dxftype == "MLEADERSTYLE":
            add_collection_entry(doc.mleader_styles, entity)

    for old, new in replace:
        transfer.replace(old, new)
        old.destroy()

    # 3. copy resources
    for block_id, block in transfer.copied_blocks.items():
        for entity_id, entity in block.items():
            copy = transfer.get_entity_copy(entity_id, block_id)
            entity.transfer_resources(copy, transfer)

    # 4. add entities to layout and objects section
    for block_id, block in transfer.copied_blocks.items():
        layout: BaseLayout
        if block_id == 0:
            layout = target
        else:
            layout = doc.blocks.get(transfer.get_block_name(block_id))
        if layout is None:
            continue
        for entity_id, entity in block.items():
            if entity.dxf.owner is not None:
                continue  # already processed!
            if is_graphic_entity(entity):
                layout.add_entity(entity)  # type: ignore
            elif is_dxf_object(entity):
                objects.add_object(entity)  # type: ignore


def add_collection_entry(collection, entry: DXFEntity):
    name = entry.dxf.name
    if name not in collection:
        collection.object_dict.add(name, entry)


class Transfer:
    # The block_id 0 contains resource objects and entities without assigned layout:
    def __init__(self):
        self.source_blocks: dict[int, dict[int, DXFEntity]] = {0: {}}
        self.copied_blocks: dict[int, dict[int, DXFEntity]] = {0: {}}

    def add_entity(self, entity: DXFEntity, block_id: int = 0):
        block = self.source_blocks.setdefault(block_id, {})
        block[id(entity)] = entity
        entity.register_resources(self)

    def add_block(self, entities: Sequence[DXFEntity], block_id: int) -> None:
        self.source_blocks[block_id] = {id(e): e for e in entities}
        for entity in entities:
            entity.register_resources(self)

    def get_entity_copy(self, entity_id: int, block_id: int = 0) -> Optional[DXFEntity]:
        block = self.copied_blocks.get(block_id)
        if isinstance(block, dict):
            return block.get(entity_id)

    def get_block_copy(self, block_id: int) -> Sequence[DXFEntity]:
        block = self.copied_blocks.get(block_id)
        if isinstance(block, dict):
            return list(block.values())

    def replace(self, old: DXFEntity, new: DXFEntity):
        self.copied_blocks[0][id(old)] = new

    def get_block_name(self, block_id: int) -> str:
        block_record = self.copied_blocks[0].get(block_id)
        if block_record:
            return block_record.dxf.name
        return "*ERROR"  # block record was not copied

    def register_handle(self, entity: DXFEntity, name: str) -> None:
        handle = entity.dxf.get(name)
        if handle:
            source = entity.doc.entitydb.get(handle)
            if source:
                self.add_entity(source)

    def register_layer(self, entity: DXFEntity) -> None:
        layer_name = entity.dxf.layer
        if layer_name == "0":
            # Layer name "0" gets never mangled and always exist in the target document.
            return
        layer = entity.doc.layers.get(layer_name)
        # the layer table entry is optional
        if layer:
            self.add_entity(layer)

    def register_linetype(self, entity: DXFEntity) -> None:
        linetype_name = entity.dxf.linetype.lower()
        # These linetype names get never mangled and always exist in the target document.
        if linetype_name not in {"continuous", "bylayer", "byblock"}:
            self.add_entity(entity.doc.linetypes.get(linetype_name))

    def register_style(self, entity: DXFEntity) -> None:
        pass

    def register_dimstyle(self, entity: DXFEntity) -> None:
        pass

    def transfer_handle(self, source: DXFEntity, copy: DXFEntity, name: str) -> None:
        handle = source.dxf.get(name)
        if handle:
            source_object = source.doc.entitydb.get(handle)
            if source_object:
                copy_object = self.get_entity_copy(id(source_object))
                if copy_object:
                    copy.dxf.set(name, copy_object.dxf.handle)

    def transfer_layer(self, source: DXFEntity, copy: DXFEntity) -> None:
        layer_name = source.dxf.layer
        if layer_name == "0":   # Layer name "0" gets never mangled
            return

        layer = source.doc.layers.get(layer_name)
        # the layer table entry is optional
        if layer:
            # the layer name was maybe mangled at import: LayerA -> xref$0$LayerA
            layer_copy = self.get_entity_copy(id(layer))
            if layer_copy:
                copy.dxf.layer = layer_copy.dxf.name

    def transfer_linetype(self, source: DXFEntity, copy: DXFEntity) -> None:
        linetype_name = source.dxf.linetype.lower()
        # These linetype names get never mangled and always exist in the target document.
        if linetype_name not in {"continuous", "bylayer", "byblock"}:
            linetype = source.doc.linetypes.get(linetype_name)
            linetype_copy = self.get_entity_copy(id(linetype))
            if linetype_copy:
                copy.dxf.linetype = linetype_copy.dxf.linetype

    def transfer_style(self, source: DXFEntity, copy: DXFEntity) -> None:
        pass

    def transfer_dimstyle(self, source: DXFEntity, copy: DXFEntity) -> None:
        pass


class CopyMachine:
    def __init__(self) -> None:
        self.copies: dict[int, dict[int, DXFEntity]] = {}
        self.classes: list[DXFClass] = []
        self.log: list[str] = []

    def copy_block(self, block: dict[int, DXFEntity]) -> dict[int, DXFEntity]:
        copies: dict[int, DXFEntity] = {}
        for entity_id, entity in block.items():
            if isinstance(entity, DXFClass):
                self._copy_dxf_class(entity)
                continue
            if entity_id in self.copies:
                continue

            try:
                copies[entity_id] = entity.copy()
            except DXFError:
                self.log.append(f"cannot copy {str(entity)}")
        return copies

    def copy_blocks(
        self, blocks: dict[int, dict[int, DXFEntity]]
    ) -> dict[int, dict[int, DXFEntity]]:
        for block_id, block in blocks.items():
            self.copies[block_id] = self.copy_block(block)
        return self.copies

    def _copy_dxf_class(self, cls: DXFClass) -> None:
        self.classes.append(cls.copy())

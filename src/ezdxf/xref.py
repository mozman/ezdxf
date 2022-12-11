#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

"""
Resource management module for transferring DXF resources between documents.

Planning state!!!

"""
from __future__ import annotations
from typing import Optional, Sequence
from typing_extensions import Protocol
import enum
from ezdxf.lldxf.const import DXFError, DXFTableEntryError
from ezdxf.document import Drawing
from ezdxf.layouts import BaseLayout


from ezdxf.entities import (
    is_graphic_entity,
    is_dxf_object,
    DXFEntity,
    DXFClass,
    factory,
    BlockRecord,
    Layer,
    Linetype,
    Textstyle,
    DimStyle,
    AppID,
)


__all__ = ["Registry", "ResourceMapper", "RenamePolicy"]

NONE_HANDLE = "0"
DEFAULT_LINETYPES = {"CONTINUOUS", "BYLAYER", "BYBLOCK"}
DEFAULT_LAYER = "0"
STANDARD = "STANDARD"


class RenamePolicy(enum.Enum):
    # keep <name> and existing table entry - ignores imported table settings
    KEEP = enum.auto()
    # rename to <xref>$0$<name> if <name> exists
    XREF = enum.auto()
    # rename to $0$<name> if <name> exists
    NUMBERED = enum.auto()


class Registry(Protocol):
    def add_entity(self, entity: DXFEntity, block_handle: str = NONE_HANDLE):
        ...

    def add_block(
        self, entities: Sequence[DXFEntity], block_handle: NONE_HANDLE
    ) -> None:
        ...

    def add_handle(self, handle: Optional[str]) -> None:
        ...

    def add_layer(self, name: str) -> None:
        ...

    def add_linetype(self, name: str) -> None:
        ...

    def add_text_style(self, name: str) -> None:
        ...

    def add_dim_style(self, name: str) -> None:
        ...

    def add_block_name(self, name: str) -> None:
        ...

    def add_appid(self, name: str) -> None:
        ...


class ResourceMapper(Protocol):
    def get_handle(self, handle: str) -> str:
        ...

    def get_layer(self, name: str) -> str:
        ...

    def get_linetype(self, name: str) -> str:
        ...

    def get_text_style(self, name: str) -> str:
        ...

    def get_dim_style(self, name: str) -> str:
        ...

    def get_block_name(self, name: str) -> str:
        ...


def find_source_doc(entities: Sequence[DXFEntity]) -> Optional[Drawing]:
    for entity in entities:
        if entity.doc is not None:
            return entity.doc
    return None


def import_entities(
    entities: Sequence[DXFEntity], target: BaseLayout, rename_policy=RenamePolicy.KEEP
):
    if len(entities) == 0:
        return
    sdoc = entities[0].doc
    assert sdoc is not None, "a valid source document is mandatory"
    tdoc: Drawing = target.doc
    assert tdoc is not None, "a valid target document is mandatory"

    objects = tdoc.objects
    registry = _Registry(sdoc, tdoc)
    for e in entities:
        registry.add_entity(e)

    cpm = CopyMachine(tdoc)
    copies = cpm.copy_blocks(registry.source_blocks)
    cpm.register_classes()

    transfer = _Transfer(registry, copies, rename_policy=rename_policy)
    transfer.create_target_resources()
    transfer.map_resources()

    # 4. add entities to layout and objects section
    for block_handle, block in transfer.copied_blocks.items():
        layout: BaseLayout
        if block_handle == NONE_HANDLE:
            layout = target
        else:
            source_block_record = sdoc.entitydb.get(block_handle)
            new_block_name = transfer.get_block_name(source_block_record.dxf.name)
            layout = tdoc.blocks.get(new_block_name)
        if layout is None:
            continue
        for entity in block.values():
            if entity.dxf.owner is not None:
                continue  # already processed!
            if is_graphic_entity(entity):
                layout.add_entity(entity)  # type: ignore
            elif is_dxf_object(entity):
                objects.add_object(entity)  # type: ignore

    tdoc.entitydb.purge()


class _Registry:
    # The block_id 0 contains resource objects and entities without assigned layout:
    def __init__(self, sdoc: Drawing, tdoc: Drawing):
        self.source_doc = sdoc
        self.target_doc = tdoc
        self.source_blocks: dict[str, dict[str, DXFEntity]] = {NONE_HANDLE: {}}
        self.appids: set[str] = set()

    def add_entity(self, entity: DXFEntity, block_handle: str = NONE_HANDLE):
        block = self.source_blocks.setdefault(block_handle, {})
        block[entity.dxf.handle] = entity
        entity.register_resources(self)

    def add_block(self, entities: Sequence[DXFEntity], block_handle: str) -> None:
        for entity in entities:
            self.add_entity(entity, block_handle)

    def add_handle(self, handle: Optional[str]) -> None:
        if handle is None or handle == NONE_HANDLE:
            return
        entity = self.source_doc.entitydb.get(handle)
        if entity is None:
            return
        self.add_entity(entity)

    def add_layer(self, name: str) -> None:
        if name == DEFAULT_LAYER:
            # Layer name "0" gets never mangled and always exist in the target document.
            return
        layer = self.source_doc.layers.get(name)
        if layer:
            self.add_entity(layer)

    def add_linetype(self, name: str) -> None:
        # These linetype names get never mangled and always exist in the target document.
        if name.upper() in DEFAULT_LINETYPES:
            return
        linetype = self.source_doc.linetypes.get(name)
        if linetype:
            self.add_entity(linetype)

    def add_text_style(self, name) -> None:
        # Text style name "STANDARD" gets never mangled and always exist in the target
        # document.
        if name.upper() == STANDARD:
            return
        text_style = self.source_doc.styles.get(name)
        if text_style:
            self.add_entity(text_style)

    def add_dim_style(self, name: str) -> None:
        # Dimension style name "STANDARD" gets never mangled and always exist in the
        # target document.
        if name.upper() == STANDARD:
            return

        dim_style = self.source_doc.dimstyles.get(name)
        if dim_style:
            self.add_entity(dim_style)

    def add_block_name(self, name: str) -> None:
        block_record = self.source_doc.block_records.get(name)
        if block_record:
            self.add_entity(block_record)

    def add_appid(self, name: str) -> None:
        self.appids.add(name.upper())


class _Transfer:
    # The block with handle "0" contains resource objects and entities without an
    # assigned layout.
    def __init__(
        self,
        registry: _Registry,
        copies: dict[str, dict[str, DXFEntity]],
        *,
        rename_policy=RenamePolicy.KEEP,
    ):
        self.registry = registry
        self.copied_blocks = copies
        self.rename_policy = rename_policy
        self.layer_mapping: dict[str, str] = {}
        self.linetype_mapping: dict[str, str] = {}
        self.text_style_mapping: dict[str, str] = {}
        self.dim_style_mapping: dict[str, str] = {}
        self.block_name_mapping: dict[str, str] = {}
        self.handle_mapping: dict[str, str] = {}

    def get_entity_copy(
        self, entity_handle: str, block_handle: str = NONE_HANDLE
    ) -> Optional[DXFEntity]:
        block = self.copied_blocks.get(block_handle)
        if isinstance(block, dict):
            return block.get(entity_handle)
        return None

    def get_block_copy(self, block_handle: str) -> Sequence[DXFEntity]:
        block = self.copied_blocks.get(block_handle)
        if isinstance(block, dict):
            return list(block.values())

    def get_handle(self, handle: str) -> str:
        return self.handle_mapping.get(handle, NONE_HANDLE)

    def get_layer(self, name: str) -> str:
        return self.layer_mapping.get(name, name)

    def get_linetype(self, name: str) -> str:
        return self.linetype_mapping.get(name, name)

    def get_text_style(self, name: str) -> str:
        return self.text_style_mapping.get(name, name)

    def get_dim_style(self, name: str) -> str:
        return self.dim_style_mapping.get(name, name)

    def get_block_name(self, name: str) -> str:
        return self.block_name_mapping.get(name, name)

    def create_target_resources(self) -> None:
        tdoc = self.registry.target_doc
        rename_policy = self.rename_policy
        self.create_appids()

        # process resource objects and entities without assigned layout: block_id == 0
        for handle, entity in self.copied_blocks.get(NONE_HANDLE).items():
            if entity.dxf.owner is not None:
                continue  # already processed!

            # 1. assign entity to document
            factory.bind(entity, tdoc)
            self.handle_mapping[handle] = entity.dxf.handle

            # 2. add copied resources to tables and collections
            dxftype = entity.dxftype()
            if isinstance(entity, Layer):
                old_name = entity.dxf.name
                add_layer_entry(entity, tdoc, rename_policy)
                if entity.is_alive:
                    self.layer_mapping[old_name] = entity.dxf.name
            elif isinstance(entity, Linetype):
                old_name = entity.dxf.name
                add_linetype_entry(entity, tdoc, rename_policy)
                if entity.is_alive:
                    self.linetype_mapping[old_name] = entity.dxf.name
            elif isinstance(entity, Textstyle):
                old_name = entity.dxf.name
                add_text_style_entry(entity, tdoc, rename_policy)
                if entity.is_alive:
                    self.text_style_mapping[old_name] = entity.dxf.name
            elif isinstance(entity, DimStyle):
                old_name = entity.dxf.name
                add_dim_style_entry(entity, tdoc, rename_policy)
                if entity.is_alive:
                    self.dim_style_mapping[old_name] = entity.dxf.name
            elif isinstance(entity, BlockRecord):
                old_name = entity.dxf.name
                add_block_record_entry(entity, tdoc, rename_policy)
                if entity.is_alive:
                    self.block_name_mapping[old_name] = entity.dxf.name
                    tdoc.blocks.add(entity)  # create BlockLayout
            elif dxftype == "MATERIAL":
                add_collection_entry(tdoc.materials, entity, rename_policy)
            elif dxftype == "MLINESTYLE":
                add_collection_entry(tdoc.mline_styles, entity, rename_policy)
            elif dxftype == "MLEADERSTYLE":
                add_collection_entry(tdoc.mleader_styles, entity, rename_policy)

    def create_appids(self):
        tdoc = self.registry.target_doc
        for appid in self.registry.appids:
            try:
                tdoc.appids.new(appid)
            except DXFTableEntryError:
                pass

    def map_resources(self):
        for block_handle, block in self.copied_blocks.items():
            for entity_handle, entity in block.items():
                copy = self.get_entity_copy(entity_handle, block_handle)
                entity.map_resources(copy, self)


def add_layer_entry(layer: Layer, tdoc: Drawing, rename_policy: RenamePolicy):
    layer_name = layer.dxf.name.upper()
    if layer_name == "0":
        layer.destroy()
        return
    # todo: mangle name
    tdoc.layers.add_entry(layer)


def add_linetype_entry(linetype: Linetype, tdoc: Drawing, rename_policy: RenamePolicy):
    linetype_name = linetype.dxf.name.upper()
    if linetype_name in DEFAULT_LINETYPES:
        linetype.destroy()
        return
    # todo: mangle name
    tdoc.linetypes.add_entry(linetype)


def add_text_style_entry(
    text_style: Textstyle, tdoc: Drawing, rename_policy: RenamePolicy
):
    text_style_name = text_style.dxf.name.upper()
    if text_style_name == STANDARD:
        text_style.destroy()
        return
    # todo: mangle name
    tdoc.styles.add_entry(text_style)


def add_dim_style_entry(
    dim_style: DimStyle, tdoc: Drawing, rename_policy: RenamePolicy
):
    dim_style_name = dim_style.dxf.name.upper()
    if dim_style_name == STANDARD:
        dim_style.destroy()
        return
    # todo: mangle name
    tdoc.dimstyles.add_entry(dim_style)


def is_special_block_name(name: str) -> bool:
    return False


def add_block_record_entry(
    block_record: BlockRecord, tdoc: Drawing, rename_policy: RenamePolicy
):
    block_name = block_record.dxf.name.upper()
    if is_special_block_name(block_name):
        block_record.destroy()
        return
    # todo: mangle name
    tdoc.block_records.add_entry(block_record)


def add_collection_entry(collection, entry: DXFEntity, rename_policy: RenamePolicy):
    name = entry.dxf.name
    if name not in collection:
        collection.object_dict.add(name, entry)


class CopyMachine:
    def __init__(self, tdoc: Drawing) -> None:
        self.target_doc = tdoc
        self.copies: dict[str, dict[str, DXFEntity]] = {}
        self.classes: list[DXFClass] = []
        self.log: list[str] = []

    def copy_block(self, block: dict[str, DXFEntity]) -> dict[str, DXFEntity]:
        copies: dict[str, DXFEntity] = {}
        tdoc = self.target_doc
        for handle, entity in block.items():
            if isinstance(entity, DXFClass):
                self._copy_dxf_class(entity)
                continue
            if handle in self.copies:
                continue
            try:
                new_entity = entity.copy()
            except DXFError:
                self.log.append(f"cannot copy entity {str(entity)}")
                continue
            copies[handle] = new_entity
            factory.bind(new_entity, tdoc)
        return copies

    def copy_blocks(
        self, blocks: dict[str, dict[str, DXFEntity]]
    ) -> dict[str, dict[str, DXFEntity]]:
        for handle, block in blocks.items():
            self.copies[handle] = self.copy_block(block)
        return self.copies

    def register_classes(self):
        self.target_doc.classes.register(self.classes)

    def _copy_dxf_class(self, cls: DXFClass) -> None:
        self.classes.append(cls.copy())

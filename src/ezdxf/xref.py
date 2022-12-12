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
import pathlib
import logging
from ezdxf.lldxf import const
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
    Material,
    MLineStyle,
    MLeaderStyle,
    Block,
    EndBlk,
)


__all__ = ["Registry", "ResourceMapper", "ConflictPolicy"]

logger = logging.getLogger("ezdxf")
NO_BLOCK = "0"
DEFAULT_LINETYPES = {"CONTINUOUS", "BYLAYER", "BYBLOCK"}
DEFAULT_LAYER = "0"
STANDARD = "STANDARD"


class ConflictPolicy(enum.Enum):
    # what to do when a name conflict of existing and imported resources occur:
    # keep existing resource <name> and ignore imported resource
    KEEP = enum.auto()
    # replace existing resource <name> by imported resource
    REPLACE = enum.auto()
    # rename imported resource to <xref>$0$<name>
    XREF_NUM_PREFIX = enum.auto()
    # rename imported resource to $0$<name>
    NUM_PREFIX = enum.auto()


class Registry(Protocol):
    def add_entity(self, entity: DXFEntity, block_handle: str = NO_BLOCK) -> None:
        ...

    def add_block(self, block_record: BlockRecord) -> None:
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


def import_entities(
    entities: Sequence[DXFEntity], target: BaseLayout, rename_policy=ConflictPolicy.KEEP
):
    if len(entities) == 0:
        return
    sdoc = entities[0].doc
    assert sdoc is not None, "a valid source document is mandatory"
    tdoc: Drawing = target.doc
    assert tdoc is not None, "a valid target document is mandatory"
    assert sdoc is not tdoc, "source and target document cannot be the same"

    registry = _Registry(sdoc, tdoc)
    for e in entities:
        registry.add_entity(e)

    cpm = CopyMachine(tdoc)
    cpm.copy_blocks(registry.source_blocks)

    transfer = _Transfer(registry, cpm.copies, cpm.objects, rename_policy=rename_policy)
    transfer.create_appids()
    transfer.register_classes(cpm.classes)
    transfer.add_target_objects()
    transfer.create_table_resources()  # restores also BLOCK content
    transfer.create_object_resources()
    transfer.update_handle_mapping()
    transfer.map_resources()
    transfer.add_entities_to_layout(target)
    transfer.finalize()


class _Registry:
    # The block "0" contains resource objects and entities without assigned layout:
    def __init__(self, sdoc: Drawing, tdoc: Drawing):
        self.source_doc = sdoc
        self.target_doc = tdoc
        self.source_blocks: dict[str, dict[str, DXFEntity]] = {NO_BLOCK: {}}
        self.appids: set[str] = set()

    def add_entity(self, entity: DXFEntity, block_handle: str = NO_BLOCK):
        block = self.source_blocks.setdefault(block_handle, {})
        block[entity.dxf.handle] = entity
        entity.register_resources(self)

    def add_block(self, block_record: BlockRecord) -> None:
        # add resource entity BLOCK_RECORD to NO_BLOCK
        self.add_entity(block_record)
        # block content in block <block_handle>
        block_handle = block_record.dxf.handle
        self.add_entity(block_record.block, block_handle)  # type: ignore
        for entity in block_record.entity_space:
            self.add_entity(entity, block_handle)
        self.add_entity(block_record.endblk, block_handle)  # type: ignore

    def add_handle(self, handle: Optional[str]) -> None:
        if handle is None or handle == NO_BLOCK:
            return
        entity = self.source_doc.entitydb.get(handle)
        if entity is None:
            logger.debug(f"source entity #{handle} does not exist")
            return
        self.add_entity(entity)

    def add_layer(self, name: str) -> None:
        if name == DEFAULT_LAYER:
            # Layer name "0" gets never mangled and always exist in the target document.
            return
        layer = self.source_doc.layers.get(name)
        if layer:
            self.add_entity(layer)
        else:
            logger.debug(f"source layer '{name}' does not exist")

    def add_linetype(self, name: str) -> None:
        # These linetype names get never mangled and always exist in the target document.
        if name.upper() in DEFAULT_LINETYPES:
            return
        linetype = self.source_doc.linetypes.get(name)
        if linetype:
            self.add_entity(linetype)
        else:
            logger.debug(f"source linetype '{name}' does not exist")

    def add_text_style(self, name) -> None:
        # Text style name "STANDARD" gets never mangled and always exist in the target
        # document.
        if name.upper() == STANDARD:
            return
        text_style = self.source_doc.styles.get(name)
        if text_style:
            self.add_entity(text_style)
        else:
            logger.debug(f"source text style '{name}' does not exist")

    def add_dim_style(self, name: str) -> None:
        # Dimension style name "STANDARD" gets never mangled and always exist in the
        # target document.
        if name.upper() == STANDARD:
            return

        dim_style = self.source_doc.dimstyles.get(name)
        if dim_style:
            self.add_entity(dim_style)
        else:
            logger.debug(f"source dimension style '{name}' does not exist")

    def add_block_name(self, name: str) -> None:
        block_record = self.source_doc.block_records.get(name)
        if block_record:
            self.add_entity(block_record)
        else:
            logger.debug(f"source block '{name}' does not exist")

    def add_appid(self, name: str) -> None:
        self.appids.add(name.upper())


class _Transfer:
    # The block with handle "0" contains resource objects and entities without an
    # assigned layout.
    def __init__(
        self,
        registry: _Registry,
        blocks: dict[str, dict[str, DXFEntity]],
        objects: Sequence[DXFEntity],
        *,
        rename_policy=ConflictPolicy.KEEP,
    ):
        self.registry = registry
        self.copied_blocks = blocks
        self.copied_objects = objects
        self.rename_policy = rename_policy
        self.xref_name = get_xref_name(registry.source_doc)
        self.layer_mapping: dict[str, str] = {}
        self.linetype_mapping: dict[str, str] = {}
        self.text_style_mapping: dict[str, str] = {}
        self.dim_style_mapping: dict[str, str] = {}
        self.block_name_mapping: dict[str, str] = {}
        self.handle_mapping: dict[str, str] = {}
        self._replace_handles: dict[str, str] = {}

    def get_entity_copy(
        self, entity_handle: str, block_handle: str = NO_BLOCK
    ) -> Optional[DXFEntity]:
        block = self.copied_blocks.get(block_handle)
        if isinstance(block, dict):
            return block.get(entity_handle)
        return None

    def get_handle(self, handle: str) -> str:
        return self.handle_mapping.get(handle, NO_BLOCK)

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

    def create_table_resources(self) -> None:
        self.create_appids()

        # process resource objects and entities without assigned layout:
        for handle, entity in self.copied_blocks[NO_BLOCK].items():
            if entity.dxf.owner is not None:
                continue  # already processed!

            # add copied resources to tables and collections of the target document
            if isinstance(entity, Layer):
                self.add_layer_entry(entity)
            elif isinstance(entity, Linetype):
                self.add_linetype_entry(entity)
            elif isinstance(entity, Textstyle):
                self.add_text_style_entry(entity)
            elif isinstance(entity, DimStyle):
                self.add_dim_style_entry(entity)
            elif isinstance(entity, BlockRecord):
                self.add_block_record_entry(entity, handle)

    def create_object_resources(self):
        tdoc = self.registry.target_doc
        for entity in self.copied_objects:
            if isinstance(entity, Material):
                self.add_collection_entry(tdoc.materials, entity)
            elif isinstance(entity, MLineStyle):
                self.add_collection_entry(tdoc.mline_styles, entity)
            elif isinstance(entity, MLeaderStyle):
                self.add_collection_entry(tdoc.mleader_styles, entity)

    def replace_handle_mapping(self, old_target, new_target) -> None:
        self._replace_handles[old_target] = new_target

    def update_handle_mapping(self) -> None:
        temp_mapping: dict[str, str] = {}
        replace_handles = self._replace_handles
        # redirect source entity -> new target entity
        for source_handle, target_handle in self.handle_mapping.items():
            if target_handle in replace_handles:
                # build temp mapping, while iterating dict
                temp_mapping[source_handle] = replace_handles[target_handle]

        for source_handle, new_target_handle in temp_mapping.items():
            self.handle_mapping[source_handle] = new_target_handle

    def create_appids(self) -> None:
        tdoc = self.registry.target_doc
        for appid in self.registry.appids:
            try:
                tdoc.appids.new(appid)
            except const.DXFTableEntryError:
                pass

    def register_classes(self, classes: Sequence[DXFClass]):
        self.registry.target_doc.classes.register(classes)

    def map_resources(self) -> None:
        for block_handle, block in self.copied_blocks.items():
            for entity_handle, entity in block.items():
                copy = self.get_entity_copy(entity_handle, block_handle)
                if copy is not None and copy.is_alive:
                    entity.map_resources(copy, self)

    def add_layer_entry(self, layer: Layer) -> None:
        tdoc = self.registry.target_doc
        layer_name = layer.dxf.name.upper()
        if layer_name == "0":
            standard = tdoc.layers.get("0")
            self.replace_handle_mapping(layer.dxf.handle, standard.dxf.handle)
            layer.destroy()
            return
        old_name = layer.dxf.name
        self.add_table_entry(tdoc.layers, layer)
        if layer.is_alive:
            self.layer_mapping[old_name] = layer.dxf.name

    def add_linetype_entry(self, linetype: Linetype) -> None:
        tdoc = self.registry.target_doc
        if linetype.dxf.name.upper() in DEFAULT_LINETYPES:
            standard = tdoc.linetypes.get(linetype.dxf.name)
            self.replace_handle_mapping(linetype.dxf.handle, standard.dxf.handle)
            linetype.destroy()
            return
        old_name = linetype.dxf.name
        self.add_table_entry(tdoc.linetypes, linetype)
        if linetype.is_alive:
            self.linetype_mapping[old_name] = linetype.dxf.name

    def add_text_style_entry(self, text_style: Textstyle) -> None:
        tdoc = self.registry.target_doc
        text_style_name = text_style.dxf.name.upper()
        if text_style_name == STANDARD:
            standard = tdoc.styles.get(STANDARD)
            self.replace_handle_mapping(text_style.dxf.handle, standard.dxf.handle)
            text_style.destroy()
            return
        old_name = text_style.dxf.name
        self.add_table_entry(tdoc.styles, text_style)
        if text_style.is_alive:
            self.text_style_mapping[old_name] = text_style.dxf.name

    def add_dim_style_entry(self, dim_style: DimStyle) -> None:
        tdoc = self.registry.target_doc
        dim_style_name = dim_style.dxf.name.upper()
        if dim_style_name == STANDARD:
            standard = tdoc.dimstyles.get(STANDARD)
            self.replace_handle_mapping(dim_style.dxf.handle, standard.dxf.handle)
            dim_style.destroy()
            return
        old_name = dim_style.dxf.name
        self.add_table_entry(tdoc.dimstyles, dim_style)
        if dim_style.is_alive:
            self.dim_style_mapping[old_name] = dim_style.dxf.name

    def add_block_record_entry(self, block_record: BlockRecord, handle: str) -> None:
        tdoc = self.registry.target_doc
        block_name = block_record.dxf.name.upper()
        if is_special_block_name(block_name):
            standard = tdoc.block_records.get(block_name)
            self.replace_handle_mapping(block_record.dxf.handle, standard.dxf.handle)
            block_record.destroy()
            return
        old_name = block_record.dxf.name
        self.add_table_entry(tdoc.block_records, block_record)
        if block_record.is_alive:
            self.block_name_mapping[old_name] = block_record.dxf.name
            self.restore_block_content(block_record, handle)
            tdoc.blocks.add(block_record)  # create BlockLayout

    def restore_block_content(self, block_record: BlockRecord, handle: str):
        content = self.copied_blocks.get(handle, dict())
        block: Optional[Block] = None
        endblk: Optional[EndBlk] = None
        for entity in content.values():
            if isinstance(entity, (Block, EndBlk)):
                if isinstance(entity, Block):
                    block = block
                else:
                    endblk = endblk
            elif is_graphic_entity(entity):
                block_record.add_entity(entity)  # type: ignore
            else:
                name = block_record.dxf.name
                logging.warning(
                    f"skipping non-graphic DXF entity in BLOCK_RECORD('{name}', #{handle}): {str(entity)}"
                )
        if isinstance(block, Block) and isinstance(endblk, EndBlk):
            block_record.set_block(block, endblk)
        else:
            raise const.DXFInternalEzdxfError("invalid BLOCK_RECORD copy")

    def add_table_entry(self, table, entity: DXFEntity) -> None:
        name = entity.dxf.name
        if self.rename_policy == ConflictPolicy.KEEP:
            if table.has_entry(name):
                existing_entry = table.get(name)
                self.replace_handle_mapping(
                    entity.dxf.handle, existing_entry.dxf.handle
                )
                entity.destroy()
                return
        elif self.rename_policy == ConflictPolicy.XREF_NUM_PREFIX:
            entity.dxf.name = find_table_name(
                "{xref}${index}${name}", name, self.xref_name, table
            )
        elif self.rename_policy == ConflictPolicy.NUM_PREFIX:
            entity.dxf.name = find_table_name(
                "${index}${name}", name, self.xref_name, table
            )
        table.add_entry(entity)

    def add_collection_entry(self, collection, entry: DXFEntity) -> None:
        name = entry.dxf.name
        if name.upper() == STANDARD:
            standard = collection.object_dict.get(name)
            self.replace_handle_mapping(entry.dxf.handle, standard.dxf.handle)
            entry.destroy()
            return

        if name not in collection:
            collection.object_dict.add(name, entry)

    def add_entities_to_layout(self, layout: BaseLayout):
        for entity in self.copied_blocks[NO_BLOCK].values():
            if entity.dxf.owner is not None:
                continue  # already processed!
            elif is_graphic_entity(entity):
                layout.add_entity(entity)  # type: ignore

    def add_target_objects(self):
        objects = self.registry.target_doc.objects
        for obj in self.copied_objects:
            objects.add_object(obj)  # type: ignore

    def finalize(self):
        # remove replaced entities:
        self.registry.target_doc.entitydb.purge()


def get_xref_name(doc: Drawing) -> str:
    if doc.filename:
        return pathlib.Path(doc.filename).stem
    return ""


def is_special_block_name(name: str) -> bool:
    return False


def find_table_name(fmt: str, name: str, xref: str, table) -> str:
    index = 0
    while True:
        new_name = fmt.format(name=name, xref=xref, index=index)
        if not table.has_entry(new_name):
            return new_name
        index += 1


class CopyMachine:
    def __init__(self, tdoc: Drawing) -> None:
        self.target_doc = tdoc
        self.copies: dict[str, dict[str, DXFEntity]] = {}
        self.classes: list[DXFClass] = []
        self.objects: list[DXFEntity] = []
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
            except const.DXFError:
                self.log.append(f"cannot copy entity {str(entity)}")
                continue
            factory.bind(new_entity, tdoc)
            if is_dxf_object(new_entity):
                self.objects.append(new_entity)
            else:
                copies[handle] = new_entity
        return copies

    def copy_blocks(self, blocks: dict[str, dict[str, DXFEntity]]):
        for handle, block in blocks.items():
            self.copies[handle] = self.copy_block(block)
        return self.copies

    def _copy_dxf_class(self, cls: DXFClass) -> None:
        self.classes.append(cls.copy())

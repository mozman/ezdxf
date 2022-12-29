#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
"""
Resource management module for transferring DXF resources between documents.

Planning state!!!

"""
from __future__ import annotations
from typing import Optional, Sequence, Callable
from typing_extensions import Protocol, TypeAlias
import enum
import pathlib
import logging
from ezdxf.lldxf import const
from ezdxf.document import Drawing
from ezdxf.layouts import BaseLayout, Paperspace, BlockLayout
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


__all__ = [
    "Registry",
    "ResourceMapper",
    "ConflictPolicy",
    "Loader",
]

logger = logging.getLogger("ezdxf")
NO_BLOCK = "0"
DEFAULT_LINETYPES = {"CONTINUOUS", "BYLAYER", "BYBLOCK"}
DEFAULT_LAYER = "0"
STANDARD = "STANDARD"
FilterFunction: TypeAlias = Callable[[DXFEntity], bool]


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

    def add_shape_file(self, name: str) -> None:
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


class LoadingCommand:
    def register_resources(self, registry: Registry) -> None:
        pass

    def execute(self, transfer: _Transfer) -> None:
        pass


class LoadEntities(LoadingCommand):
    def __init__(
        self, entities: Sequence[DXFEntity], target_layout: BaseLayout
    ) -> None:
        self.entities = entities
        self.target_layout = target_layout


class LoadPaperspaceLayout(LoadingCommand):
    def __init__(self, psp: Paperspace, filter_fn: Optional[FilterFunction]) -> None:
        self.paperspace_layout = psp
        self.filter_fn = filter_fn


class LoadBlockLayout(LoadingCommand):
    def __init__(self, block: BlockLayout) -> None:
        self.block_layout = block


class LoadResources(LoadingCommand):
    def __init__(self, entities: Sequence[DXFEntity]) -> None:
        self.entities = entities

    def register_resources(self, registry: Registry) -> None:
        for e in self.entities:
            registry.add_entity(e, block_handle=NO_BLOCK)


class Loader:
    """Load entities and resources from the source DXF document `sdoc` into a
    target DXF document.
    """

    def __init__(
        self, sdoc: Drawing, tdoc: Drawing, conflict_policy=ConflictPolicy.KEEP
    ) -> None:
        assert sdoc is not None, "a valid source document is mandatory"
        assert tdoc is not None, "a valid target document is mandatory"
        assert sdoc is not tdoc, "source and target document cannot be the same"
        if tdoc.dxfversion < sdoc.dxfversion:
            logger.warning(
                "target document has older DXF version than the source document"
            )
        self.sdoc: Drawing = sdoc
        self.tdoc: Drawing = tdoc
        self.conflict_policy = conflict_policy
        self._commands: list[LoadingCommand] = []

    def add_command(self, command: LoadingCommand) -> None:
        self._commands.append(command)

    def load_modelspace(
        self,
        target_layout: Optional[BaseLayout] = None,
        filter_fn: Optional[FilterFunction] = None,
    ):
        """Loads the content of the modelspace of the source document into a layout of
        the target document the modelspace of the target document is the default target
        layout.  The target layout can be any layout: modelspace, paperspace layout or
        block layout.
        """
        if target_layout is None:
            target_layout = self.tdoc.modelspace()
        if filter_fn is None:
            entities = list(self.sdoc.modelspace())
        else:
            entities = [e for e in self.sdoc.modelspace() if filter_fn(e)]
        self.add_command(LoadEntities(entities, target_layout))

    def load_paperspace_layout(
        self,
        psp: Paperspace,
        filter_fn: Optional[FilterFunction] = None,
    ):
        """Loads a paperspace layout as a new paperspace layout into the target document.
        If a paperspace layout with same name already exists the layout will be renamed
        to  "<layout name> (2)" or "<layout name> (3)" and so on. The content of the
        modelspace which may be displayed through a VIEWPORT entity will **not** be
        loaded!
        """
        self.add_command(LoadPaperspaceLayout(psp, filter_fn))

    def load_paperspace_layout_into(
        self,
        psp: Paperspace,
        target_layout: BaseLayout,
        filter_fn: Optional[FilterFunction] = None,
    ):
        """Loads the content of a paperspace layout into an existing layout of the target
        document. The target layout can be any layout: modelspace, paperspace layout
        or block layout.  The content of the modelspace which may be displayed through a
        VIEWPORT entity will **not** be loaded!
        """
        if filter_fn is None:
            entities = list(psp)
        else:
            entities = [e for e in psp if filter_fn(e)]
        self.add_command(LoadEntities(entities, target_layout))

    def load_block_layout(
        self,
        block_layout: BlockLayout,
    ):
        """Loads a block layout (block definition) as a new block layout into the target
        document. If a block layout with the same name exists the conflict policy will
        be applied.
        """
        self.add_command(LoadBlockLayout(block_layout))

    def load_block_layout_into(
        self,
        block_layout: BlockLayout,
        target_layout: BaseLayout,
    ):
        """Loads the content of a block layout (block definition) into an existing layout
        of the target document. The target layout can be any layout: modelspace,
        paperspace layout or block layout.
        """
        self.add_command(LoadEntities(list(block_layout), target_layout))

    def load_layers(self, names: Sequence[str]):
        """Loads the layers defined by the argument `names` into the target document.
        In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.layers)
        self.add_command(LoadResources(entities))

    def load_linetypes(self, names: Sequence[str]):
        """Loads the linetypes defined by the argument `names` into the target document.
        In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.linetypes)
        self.add_command(LoadResources(entities))

    def load_text_styles(self, names: Sequence[str]):
        """Loads the TEXT styles defined by the argument `names` into the target document.
        In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.styles)
        self.add_command(LoadResources(entities))

    def load_dim_styles(self, names: Sequence[str]):
        """Loads the DIMENSION styles defined by the argument `names` into the target
        document. In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.dimstyles)
        self.add_command(LoadResources(entities))

    def load_mline_styles(self, names: Sequence[str]):
        """Loads the MLINE styles defined by the argument `names` into the target
        document. In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.mline_styles)
        self.add_command(LoadResources(entities))

    def load_mleader_styles(self, names: Sequence[str]):
        """Loads the MULTILEADER styles defined by the argument `names` into the target
        document. In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.mleader_styles)
        self.add_command(LoadResources(entities))

    def load_materials(self, names: Sequence[str]):
        """Loads the MATERIALS defined by the argument `names` into the target
        document. In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.materials)
        self.add_command(LoadResources(entities))

    def execute(self):
        registry = _Registry(self.sdoc, self.tdoc)
        for cmd in self._commands:
            cmd.register_resources(registry)

        cpm = CopyMachine(self.tdoc)
        cpm.copy_blocks(registry.source_blocks)
        transfer = _Transfer(
            registry, cpm.copies, cpm.objects, conflict_policy=self.conflict_policy
        )
        transfer.register_classes(cpm.classes)
        transfer.create_appids()
        transfer.add_target_objects()
        transfer.create_table_resources()
        transfer.create_object_resources()
        transfer.update_handle_mapping()
        transfer.map_resources()

        for cmd in self._commands:
            cmd.execute(transfer)
        transfer.finalize()


def _get_table_entries(names, table) -> list[DXFEntity]:
    entities: list[DXFEntity] = []
    for name in names:
        try:
            entities.append(table.get(name))  # type: ignore
        except const.DXFTableEntryError:
            pass
    return entities


class _Registry:
    # The block "0" contains resource objects and entities without assigned layout:
    def __init__(self, sdoc: Drawing, tdoc: Drawing):
        self.source_doc = sdoc
        self.target_doc = tdoc
        self.source_blocks: dict[str, dict[str, DXFEntity]] = {NO_BLOCK: {}}
        self.appids: set[str] = set()

    def add_entity(self, entity: DXFEntity, block_handle: str = NO_BLOCK):
        assert entity is not None, "internal error: entity is None"
        block = self.source_blocks.setdefault(block_handle, {})
        entity_handle = entity.dxf.handle
        if entity_handle in block:
            return
        block[entity_handle] = entity
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

    def add_shape_file(self, name) -> None:
        shape_file = self.source_doc.styles.get_shx(name)
        if shape_file:
            self.add_entity(shape_file)
        else:
            logger.debug(f"source shape file '{name}' does not exist")

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
        conflict_policy=ConflictPolicy.KEEP,
    ):
        self.registry = registry
        self.copied_blocks = blocks
        self.copied_objects = objects
        self.conflict_policy = conflict_policy
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
                if entity.is_shape_file:
                    self.add_shape_file_entry(entity)
                else:
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
        # TODO: special cases - do not copy, but create if doesn't exist
        #   DEFPOINTS
        #   *ADSK_... layers
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

    def add_shape_file_entry(self, text_style: Textstyle) -> None:
        # A shape file (SHX file) entry is a special text style entry which name is "".
        shape_file_name = text_style.dxf.font
        if not shape_file_name:
            return
        tdoc = self.registry.target_doc
        shape_file = tdoc.styles.find_shx(shape_file_name)
        if shape_file is None:
            shape_file = tdoc.styles.add_shx(shape_file_name)
        self.replace_handle_mapping(text_style.dxf.handle, shape_file.dxf.handle)

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
        # TODO: special case arrow blocks: do not rename!
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
        if self.conflict_policy == ConflictPolicy.KEEP:
            if table.has_entry(name):
                existing_entry = table.get(name)
                self.replace_handle_mapping(
                    entity.dxf.handle, existing_entry.dxf.handle
                )
                entity.destroy()
                return
        elif self.conflict_policy == ConflictPolicy.XREF_NUM_PREFIX:
            entity.dxf.name = create_valid_table_name(
                "{xref}${index}${name}", name, self.xref_name, table
            )
        elif self.conflict_policy == ConflictPolicy.NUM_PREFIX:
            entity.dxf.name = create_valid_table_name(
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
        """Add copied graphical DXF entities from NO_BLOCK to the given layout.
        """
        for entity in self.copied_blocks[NO_BLOCK].values():
            if entity.dxf.owner is not None:
                continue  # already processed!
            elif is_graphic_entity(entity):
                layout.add_entity(entity)  # type: ignore

    def add_target_objects(self):
        """Add copied DXF objects to the OBJECTS section of the target document.
        """
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


def create_valid_table_name(fmt: str, name: str, xref: str, table) -> str:
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

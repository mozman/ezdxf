#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
"""
Resource management module for transferring DXF resources between documents.

Planning state!!!

"""
from __future__ import annotations
from typing import Optional, Sequence, Callable, Iterable
from typing_extensions import Protocol, TypeAlias
import enum
import pathlib
import logging

import ezdxf
from ezdxf.lldxf import const, validator, types
from ezdxf.lldxf.tags import Tags
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
    Insert,
)
from ezdxf.math import UVec, Vec3

__all__ = [
    "embed",
    "attach",
    "detach",
    "write_block",
    "load_modelspace",
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
LoadFunction: TypeAlias = Callable[[str], Drawing]


# I prefer to see the debug messages stored in the object, because I mostly debug test
# code and pytest does not show logging or print messages by default.
def _log_debug_messages(messages: Iterable[str]) -> None:
    for msg in messages:
        logger.debug(msg)


class ConflictPolicy(enum.Enum):
    # What to do when a name conflict of existing and loaded resources occur:
    # keep existing resource <name> and ignore loaded resource
    KEEP = enum.auto()

    # ALWAYS rename imported resources to <xref>$0$<name>
    # This is the default behavior of BricsCAD when binding an external reference.
    XREF_PREFIX = enum.auto()

    # rename loaded resource to $0$<name> if the loaded resource <name> already exist
    NUM_PREFIX = enum.auto()
    # REPLACE policy was removed, adds too much complexity!


# Exceptions from the ConflictPolicy
# ----------------------------------
# Resources named "STANDARD" will be preserved (KEEP).
# Materials "GLOBAL", "BYLAYER" and "BYBLOCK" will be preserved (KEEP).
# Plot style "NORMAL" will be preserved (KEEP).
# Layers "0", "DEFPOINTS" and special Autodesk layers starting with "*" will be preserved (KEEP).
# Linetypes "CONTINUOUS", "BYLAYER" and "BYBLOCK" will be preserved (KEEP)
# Special blocks like arrow heads will be preserved (KEEP).
# Anonymous blocks get a new arbitrary name following the rules of anonymous block names.


def embed(
    xref: BlockLayout,
    *,
    load_fn: Optional[LoadFunction] = None,
    conflict_policy=ConflictPolicy.XREF_PREFIX,
) -> None:
    """Loads the modelspace of the XREF as content of the block definition.

    The loader function loads the XREF as `Drawing` object, by default the
    function :func:`ezdxf.readfile` is used to load DXF files. To load DWG files use the
    :func:`~ezdxf.addons.odafc.readfile` function from the :mod:`ezdxf.addons.odafc`
    add-on. The :func:`ezdxf.recover.readfile` function is very robust for reading DXF
    files with errors.

    Args:
        xref: :class:`BlockLayout` of the XREF document
        load_fn: function to load the content of the XREF as `Drawing` object
        conflict_policy: how to resolve name conflicts

    Raises:
        ValueError: argument `xref` is not a XREF definition
        FileNotFoundError: XREF file not found
        DXFVersionError: cannot load a XREF with a newer DXF version than the host
            document, try the :mod:`~ezdxf.addons.odafc` add-on to downgrade the XREF
            document or upgrade the host document

    .. versionadded:: 1.1

    """
    assert isinstance(xref, BlockLayout), "expected BLOCK definition of XREF"
    target_doc = xref.doc
    assert target_doc is not None, "valid DXF document required"
    block = xref.block
    assert isinstance(block, Block)
    if not block.is_xref:
        raise ValueError("argument 'xref' is not a XREF definition")
    filepath = pathlib.Path(block.dxf.get("xref_path", ""))
    if not filepath.exists():
        raise FileNotFoundError(f"file not found: '{filepath}'")

    if load_fn:
        source_doc = load_fn(str(filepath))
    else:
        source_doc = ezdxf.readfile(filepath)
    if source_doc.dxfversion > target_doc.dxfversion:
        raise const.DXFVersionError(
            "cannot embed a XREF with a newer DXF version into the host document"
        )
    loader = Loader(source_doc, target_doc, conflict_policy=conflict_policy)
    loader.load_modelspace(xref)
    loader.execute()
    # reset XREF flags:
    block.set_flag_state(const.BLK_XREF | const.BLK_EXTERNAL, state=False)
    # update BLOCK origin:
    origin = source_doc.header.get("$INSBASE")
    if origin:
        block.dxf.origin = Vec3(origin)


def attach(
    doc: Drawing, *, block_name: str, filename: str, insert: UVec = (0, 0, 0)
) -> Insert:
    """Attach the file `filename` to the host document as external reference (XREF).

    This function creates the required XREF block definition and a default block
    reference at location `insert`.

    .. important::

        If the XREF has different drawing units than the host document, the scale
        factor between these units must be applied as a uniform scale factor to the
        block reference!  Unfortunately the XREF drawing units can only be detected by
        loading the whole document and is therefore not done automatically by this
        function. Advice: always use the same units for all drawings of a project!

    Args:
        doc: host DXF document
        block_name: name of the XREF definition block
        filename: file name of the XREF
        insert: location of the default block reference

    Returns:
        Insert: default block reference for the XREF at location `insert`

    Raises:
        ValueError: block with same name exist

    .. versionadded:: 1.1

    """
    if block_name in doc.blocks:
        raise ValueError(f"block '{block_name}' already exist")
    flags = const.BLK_XREF | const.BLK_EXTERNAL
    doc.blocks.new(name=block_name, dxfattribs={"flags": flags, "xref_path": filename})
    location = Vec3(insert)
    msp = doc.modelspace()
    return msp.add_blockref(block_name, insert=location)


def detach(block: BlockLayout, *, xref_filename: str) -> Drawing:
    """Write the content of `block` into the modelspace of a new DXF document and
    convert `block` to an external reference (XREF).  The new DXF document has to be
    written by the caller: :code:`xref_doc.saveas(xref_filename)`.
    This way it is possible to convert the DXF document to DWG by the
    :mod:`~ezdxf.addons.odafc` add-on if necessary::

        xref_doc = xref.detach(my_block, "my_block.dwg")
        odafc.export_dwg(xref_doc, "my_block.dwg")

    Args:
        block: block definition to detach
        xref_filename: name of the external referenced file

    .. versionadded:: 1.1

    """
    raise NotImplementedError()


def write_block(entities: Sequence[DXFEntity], *, origin: UVec = (0, 0, 0)) -> Drawing:
    """Write `entities` into the modelspace of a new DXF document.

    This function is called "write_block" because the new DXF document can be used as
    an external referenced block.  This function is similar to the WBLOCK command of CAD
    applications.

    Virtual entities are not supported, because each entity needs a real database- and
    owner handle.

    Args:
        entities: DXF entities to write
        origin: block origin, defines the point in the modelspace which will be inserted
            at the insert location of the block reference

    Raises:
        ValueError: virtual entities are not supported

    .. versionadded:: 1.1

    """
    if len(entities) == 0:
        return ezdxf.new()
    if any(e.dxf.owner is None for e in entities):
        raise ValueError("virtual entities are not supported")
    source_doc = entities[0].doc
    assert source_doc is not None, "expected a valid source document"
    target_doc = ezdxf.new(dxfversion=source_doc.dxfversion, units=source_doc.units)
    loader = Loader(source_doc, target_doc)
    loader.add_command(LoadEntities(entities, target_doc.modelspace()))
    loader.execute()
    target_doc.header["$INSBASE"] = Vec3(origin)
    return target_doc


def load_modelspace(
    sdoc: Drawing,
    tdoc: Drawing,
    filter_fn: Optional[FilterFunction] = None,
    conflict_policy=ConflictPolicy.KEEP,
) -> None:
    """Loads the modelspace content of the source document into the modelspace
    of the target document.  The filter function `filter_fn` gets every source entity as
    input and returns ``True`` to load the entity or ``False`` otherwise.

    Args:
        sdoc: source document
        tdoc: target document
        filter_fn: optional function to filter entities from the source modelspace
        conflict_policy: how to resolve name conflicts

    """
    loader = Loader(sdoc, tdoc, conflict_policy=conflict_policy)
    loader.load_modelspace(filter_fn=filter_fn)
    loader.execute()


class Registry(Protocol):
    def add_entity(self, entity: DXFEntity, block_key: str = NO_BLOCK) -> None:
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
    def get_handle(self, handle: str, default="0") -> str:
        ...

    def get_reference_of_copy(self, handle: str) -> Optional[DXFEntity]:
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

    def map_resources_of_copy(self, entity: DXFEntity) -> None:
        ...

    def map_pointers(self, tags: Tags, new_owner_handle: str = "") -> None:
        ...


class LoadingCommand:
    def register_resources(self, registry: Registry) -> None:
        pass

    def execute(self, transfer: _Transfer) -> None:
        pass


class LoadEntities(LoadingCommand):
    """Loads all given entities into the target layout."""

    def __init__(
        self, entities: Sequence[DXFEntity], target_layout: BaseLayout
    ) -> None:
        self.entities = entities
        if not isinstance(target_layout, BaseLayout):
            raise const.DXFTypeError(
                f"invalid target layout type: {type(target_layout)}"
            )
        self.target_layout = target_layout

    def register_resources(self, registry: Registry) -> None:
        for e in self.entities:
            registry.add_entity(e, block_key=e.dxf.owner)

    def execute(self, transfer: _Transfer) -> None:
        for entity in self.entities:
            copy = transfer.get_entity_copy(entity)
            if copy:
                self.target_layout.add_entity(copy)  # type: ignore


class LoadPaperspaceLayout(LoadingCommand):
    """Loads a paperspace layout as a new paperspace layout into the target document.
    If a paperspace layout with same name already exists the layout will be renamed
    to  "<layout name> (x)" where x is the next free number.
    """

    def __init__(self, psp: Paperspace, filter_fn: Optional[FilterFunction]) -> None:
        if not isinstance(psp, Paperspace):
            raise const.DXFTypeError(f"invalid paperspace layout type: {type(psp)}")
        self.paperspace_layout = psp
        self.filter_fn = filter_fn

    def source_entities(self) -> list[DXFEntity]:
        filter_fn = self.filter_fn
        if filter_fn:
            return [e for e in self.paperspace_layout if filter_fn(e)]
        else:
            return list(self.paperspace_layout)

    def register_resources(self, registry: Registry) -> None:
        for e in self.source_entities():
            registry.add_entity(e, block_key=e.dxf.owner)


class LoadBlockLayout(LoadingCommand):
    """Loads a block layout as a new block layout into the target document. If a block
    layout with the same name exists the conflict policy will be applied.
    """

    def __init__(self, block: BlockLayout) -> None:
        if not isinstance(block, BlockLayout):
            raise const.DXFTypeError(f"invalid block layout type: {type(block)}")
        self.block_layout = block

    def register_resources(self, registry: Registry) -> None:
        block_record = self.block_layout.block_record
        if isinstance(block_record, BlockRecord):
            registry.add_entity(block_record)


class LoadResources(LoadingCommand):
    """Loads table entries into the target document. If a table entry with the same name
    exists the conflict policy will be applied.
    """

    def __init__(self, entities: Sequence[DXFEntity]) -> None:
        self.entities = entities

    def register_resources(self, registry: Registry) -> None:
        for e in self.entities:
            registry.add_entity(e, block_key=NO_BLOCK)


class Loader:
    """Load entities and resources from the source DXF document `sdoc` into a
    target DXF document.
    """

    def __init__(
        self, sdoc: Drawing, tdoc: Drawing, conflict_policy=ConflictPolicy.KEEP
    ) -> None:
        assert isinstance(sdoc, Drawing), "a valid source document is mandatory"
        assert isinstance(tdoc, Drawing), "a valid target document is mandatory"
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
    ) -> None:
        """Loads the content of the modelspace of the source document into a layout of
        the target document, the modelspace of the target document is the default target
        layout.  The target layout can be any layout: modelspace, paperspace layout or
        block layout.
        """
        if target_layout is None:
            target_layout = self.tdoc.modelspace()
        elif not isinstance(target_layout, BaseLayout):
            raise const.DXFTypeError(
                f"invalid target layout type: {type(target_layout)}"
            )
        if target_layout.doc is not self.tdoc:
            raise const.DXFValueError(
                f"given target layout does not belong to the target document"
            )
        if filter_fn is None:
            entities = list(self.sdoc.modelspace())
        else:
            entities = [e for e in self.sdoc.modelspace() if filter_fn(e)]
        self.add_command(LoadEntities(entities, target_layout))

    def load_paperspace_layout(
        self,
        psp: Paperspace,
        filter_fn: Optional[FilterFunction] = None,
    ) -> None:
        """Loads a paperspace layout as a new paperspace layout into the target document.
        If a paperspace layout with same name already exists the layout will be renamed
        to  "<layout name> (2)" or "<layout name> (3)" and so on. The content of the
        modelspace which may be displayed through a VIEWPORT entity will **not** be
        loaded!
        """
        if not isinstance(psp, Paperspace):
            raise const.DXFTypeError(f"invalid paperspace layout type: {type(psp)}")
        if psp.doc is not self.sdoc:
            raise const.DXFValueError(
                f"given paperspace layout does not belong to the source document"
            )
        self.add_command(LoadPaperspaceLayout(psp, filter_fn))

    def load_paperspace_layout_into(
        self,
        psp: Paperspace,
        target_layout: BaseLayout,
        filter_fn: Optional[FilterFunction] = None,
    ) -> None:
        """Loads the content of a paperspace layout into an existing layout of the target
        document. The target layout can be any layout: modelspace, paperspace layout
        or block layout.  The content of the modelspace which may be displayed through a
        VIEWPORT entity will **not** be loaded!
        """
        if not isinstance(psp, Paperspace):
            raise const.DXFTypeError(f"invalid paperspace layout type: {type(psp)}")
        if not isinstance(target_layout, BaseLayout):
            raise const.DXFTypeError(
                f"invalid target layout type: {type(target_layout)}"
            )
        if psp.doc is not self.sdoc:
            raise const.DXFValueError(
                f"given paperspace layout does not belong to the source document"
            )
        if target_layout.doc is not self.tdoc:
            raise const.DXFValueError(
                f"given target layout does not belong to the target document"
            )
        if filter_fn is None:
            entities = list(psp)
        else:
            entities = [e for e in psp if filter_fn(e)]
        self.add_command(LoadEntities(entities, target_layout))

    def load_block_layout(
        self,
        block_layout: BlockLayout,
    ) -> None:
        """Loads a block layout (block definition) as a new block layout into the target
        document. If a block layout with the same name exists the conflict policy will
        be applied.  This method cannot load modelspace or paperspace layouts.
        """
        if not isinstance(block_layout, BlockLayout):
            raise const.DXFTypeError(f"invalid block layout type: {type(block_layout)}")
        if block_layout.doc is not self.sdoc:
            raise const.DXFValueError(
                f"given block layout does not belong to the source document"
            )
        self.add_command(LoadBlockLayout(block_layout))

    def load_block_layout_into(
        self,
        block_layout: BlockLayout,
        target_layout: BaseLayout,
    ) -> None:
        """Loads the content of a block layout (block definition) into an existing layout
        of the target document. The target layout can be any layout: modelspace,
        paperspace layout or block layout.  This method cannot load the content of
        modelspace or paperspace layouts.
        """
        if not isinstance(block_layout, BlockLayout):
            raise const.DXFTypeError(f"invalid block layout type: {type(block_layout)}")
        if not isinstance(target_layout, BaseLayout):
            raise const.DXFTypeError(
                f"invalid target layout type: {type(target_layout)}"
            )
        if block_layout.doc is not self.sdoc:
            raise const.DXFValueError(
                f"given block layout does not belong to the source document"
            )
        if target_layout.doc is not self.tdoc:
            raise const.DXFValueError(
                f"given target layout does not belong to the target document"
            )
        self.add_command(LoadEntities(list(block_layout), target_layout))

    def load_layers(self, names: Sequence[str]) -> None:
        """Loads the layers defined by the argument `names` into the target document.
        In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.layers)
        self.add_command(LoadResources(entities))

    def load_linetypes(self, names: Sequence[str]) -> None:
        """Loads the linetypes defined by the argument `names` into the target document.
        In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.linetypes)
        self.add_command(LoadResources(entities))

    def load_text_styles(self, names: Sequence[str]) -> None:
        """Loads the TEXT styles defined by the argument `names` into the target document.
        In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.styles)
        self.add_command(LoadResources(entities))

    def load_dim_styles(self, names: Sequence[str]) -> None:
        """Loads the DIMENSION styles defined by the argument `names` into the target
        document. In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.dimstyles)
        self.add_command(LoadResources(entities))

    def load_mline_styles(self, names: Sequence[str]) -> None:
        """Loads the MLINE styles defined by the argument `names` into the target
        document. In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.mline_styles)
        self.add_command(LoadResources(entities))

    def load_mleader_styles(self, names: Sequence[str]) -> None:
        """Loads the MULTILEADER styles defined by the argument `names` into the target
        document. In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.mleader_styles)
        self.add_command(LoadResources(entities))

    def load_materials(self, names: Sequence[str]) -> None:
        """Loads the MATERIALS defined by the argument `names` into the target
        document. In the case of a name conflict the conflict policy will be applied.
        """
        entities = _get_table_entries(names, self.sdoc.materials)
        self.add_command(LoadResources(entities))

    def execute(self) -> None:
        registry = _Registry(self.sdoc, self.tdoc)
        debug = ezdxf.options.debug

        for cmd in self._commands:
            cmd.register_resources(registry)

        if debug:
            _log_debug_messages(registry.debug_messages)

        cpm = CopyMachine(self.tdoc)

        if debug:
            _log_debug_messages(cpm.debug_messages)

        cpm.copy_blocks(registry.source_blocks)
        transfer = _Transfer(
            registry=registry,
            copies=cpm.copies,
            handle_mapping=cpm.handle_mapping,
            conflict_policy=self.conflict_policy,
        )
        transfer.add_object_copies(cpm.objects)
        transfer.register_classes(cpm.classes)
        transfer.register_table_resources()
        transfer.register_object_resources(cpm.objects)
        transfer.redirect_handle_mapping()
        transfer.map_resources()

        for cmd in self._commands:
            cmd.execute(transfer)
        transfer.finalize()


def _get_table_entries(names: Iterable[str], table) -> list[DXFEntity]:
    entities: list[DXFEntity] = []
    for name in names:
        try:
            entry = table.get(name)
            if entry:
                entities.append(entry)  # type: ignore
        except const.DXFTableEntryError:
            pass
    return entities


class _Registry:
    def __init__(self, sdoc: Drawing, tdoc: Drawing) -> None:
        self.source_doc = sdoc
        self.target_doc = tdoc

        # source_blocks:
        # - key is the owner handle (layout key)
        # - value is a dict(): key is source-entity-handle, value is source-entity
        #   Storing the entities to copy in a dict() guarantees that each entity is only
        #   copied once and a dict() preserves the order which a set() doesn't and
        #   that is nice for testing.
        # - entry NO_BLOCK (layout key "0") contains table entries and DXF objects
        self.source_blocks: dict[str, dict[str, DXFEntity]] = {NO_BLOCK: {}}
        self.appids: set[str] = set()
        self.debug_messages: list[str] = []

    def debug(self, msg: str) -> None:
        self.debug_messages.append(msg)

    def add_entity(self, entity: DXFEntity, block_key: str = NO_BLOCK) -> None:
        assert entity is not None, "internal error: entity is None"
        block = self.source_blocks.setdefault(block_key, {})
        entity_handle = entity.dxf.handle
        if entity_handle in block:
            return
        block[entity_handle] = entity
        entity.register_resources(self)

    def add_block(self, block_record: BlockRecord) -> None:
        # add resource entity BLOCK_RECORD to NO_BLOCK
        self.add_entity(block_record)
        # block content in block <block_key>
        block_handle = block_record.dxf.handle
        self.add_entity(block_record.block, block_handle)  # type: ignore
        for entity in block_record.entity_space:
            self.add_entity(entity, block_handle)
        self.add_entity(block_record.endblk, block_handle)  # type: ignore

    def add_handle(self, handle: Optional[str]) -> None:
        """Add resource by handle (table entry or object), cannot add graphic entities.

        Raises:
            TypeError: cannot add graphic entity

        """
        if handle is None or handle == "0":
            return
        entity = self.source_doc.entitydb.get(handle)
        if entity is None:
            self.debug(f"source entity #{handle} does not exist")
            return
        if is_graphic_entity(entity):
            raise TypeError(f"cannot add graphic entity: {str(entity)}")
        self.add_entity(entity)

    def add_layer(self, name: str) -> None:
        if name == DEFAULT_LAYER:
            # Layer name "0" gets never mangled and always exist in the target document.
            return
        layer = self.source_doc.layers.get(name)
        if layer:
            self.add_entity(layer)
        else:
            self.debug(f"source layer '{name}' does not exist")

    def add_linetype(self, name: str) -> None:
        # These linetype names get never mangled and always exist in the target document.
        if name.upper() in DEFAULT_LINETYPES:
            return
        linetype = self.source_doc.linetypes.get(name)
        if linetype:
            self.add_entity(linetype)
        else:
            self.debug(f"source linetype '{name}' does not exist")

    def add_text_style(self, name) -> None:
        # Text style name "STANDARD" gets never mangled and always exist in the target
        # document.
        if name.upper() == STANDARD:
            return
        text_style = self.source_doc.styles.get(name)
        if text_style:
            self.add_entity(text_style)
        else:
            self.debug(f"source text style '{name}' does not exist")

    def add_dim_style(self, name: str) -> None:
        # Dimension style name "STANDARD" gets never mangled and always exist in the
        # target document.
        if name.upper() == STANDARD:
            return

        dim_style = self.source_doc.dimstyles.get(name)
        if dim_style:
            self.add_entity(dim_style)
        else:
            self.debug(f"source dimension style '{name}' does not exist")

    def add_block_name(self, name: str) -> None:
        block_record = self.source_doc.block_records.get(name)
        if block_record:
            self.add_entity(block_record)
        else:
            self.debug(f"source block '{name}' does not exist")

    def add_appid(self, name: str) -> None:
        self.appids.add(name.upper())


class _Transfer:
    def __init__(
        self,
        registry: _Registry,
        copies: dict[str, dict[str, DXFEntity]],
        handle_mapping: dict[str, str],
        *,
        conflict_policy=ConflictPolicy.KEEP,
    ) -> None:
        self.registry = registry
        # entry NO_BLOCK (layout key "0") contains table entries
        self.copied_blocks = copies
        self.conflict_policy = conflict_policy
        self.xref_name = get_xref_name(registry.source_doc)
        self.layer_mapping: dict[str, str] = {}
        self.linetype_mapping: dict[str, str] = {}
        self.text_style_mapping: dict[str, str] = {}
        self.dim_style_mapping: dict[str, str] = {}
        self.block_name_mapping: dict[str, str] = {}
        self.handle_mapping: dict[str, str] = handle_mapping
        self._replace_handles: dict[str, str] = {}
        self.debug_messages: list[str] = []

    def debug(self, msg: str) -> None:
        self.debug_messages.append(msg)

    def get_handle(self, handle: str, default="0") -> str:
        return self.handle_mapping.get(handle, default)

    def get_reference_of_copy(self, handle: str) -> Optional[DXFEntity]:
        handle_of_copy = self.handle_mapping.get(handle)
        if handle_of_copy:
            return self.registry.target_doc.entitydb.get(handle_of_copy)
        return None

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

    def get_entity_copy(self, entity: DXFEntity) -> Optional[DXFEntity]:
        """Returns the copy of graphic entities."""
        try:
            return self.copied_blocks[entity.dxf.owner][entity.dxf.handle]
        except KeyError:
            pass
        return None

    def map_resources_of_copy(self, entity: DXFEntity) -> None:
        clone = self.get_entity_copy(entity)
        if clone:
            entity.map_resources(clone, self)
        else:
            raise const.DXFInternalEzdxfError(f"copy of {entity} not found")

    def map_pointers(self, tags: Tags, new_owner_handle: str = "") -> None:
        for index, tag in enumerate(tags):
            if types.is_translatable_pointer(tag):
                handle = self.get_handle(tag.value, default="0")
                tags[index] = types.DXFTag(tag.code, handle)
                if new_owner_handle and types.is_hard_owner(tag):
                    copied_object = self.registry.target_doc.entitydb.get(handle)
                    if copied_object is None:
                        continue
                    copied_object.dxf.owner = new_owner_handle

    def register_table_resources(self) -> None:
        """Register copied table-entries in resource tables of the target document."""
        self.register_appids()
        # process copied table-entries, layout key is "0":
        for source_entity_handle, entity in self.copied_blocks[NO_BLOCK].items():
            if entity.dxf.owner is not None:
                continue  # already processed!

            # add copied table-entries to tables in the target document
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
                self.add_block_record_entry(entity, source_entity_handle)

    def register_object_resources(self, copies: Iterable[DXFEntity]) -> None:
        """Register copied objects in object collections of the target document."""
        tdoc = self.registry.target_doc
        for entity in copies:
            if isinstance(entity, Material):
                self.add_collection_entry(
                    tdoc.materials,
                    entity,
                    system_entries={"GLOBAL", "BYLAYER", "BYBLOCK"},
                )
            elif isinstance(entity, MLineStyle):
                self.add_collection_entry(
                    tdoc.mline_styles,
                    entity,
                    system_entries={
                        STANDARD,
                    },
                )
            elif isinstance(entity, MLeaderStyle):
                self.add_collection_entry(
                    tdoc.mleader_styles,
                    entity,
                    system_entries={
                        STANDARD,
                    },
                )

    def replace_handle_mapping(self, old_target, new_target) -> None:
        self._replace_handles[old_target] = new_target

    def redirect_handle_mapping(self) -> None:
        """Redirect handle mapping to copied entity to a handle of an existing entity in
        the target document.
        """
        temp_mapping: dict[str, str] = {}
        replace_handles = self._replace_handles
        # redirect source entity -> new target entity
        for source_handle, target_handle in self.handle_mapping.items():
            if target_handle in replace_handles:
                # build temp mapping, while iterating dict
                temp_mapping[source_handle] = replace_handles[target_handle]

        for source_handle, new_target_handle in temp_mapping.items():
            self.handle_mapping[source_handle] = new_target_handle

    def register_appids(self) -> None:
        tdoc = self.registry.target_doc
        for appid in self.registry.appids:
            try:
                tdoc.appids.new(appid)
            except const.DXFTableEntryError:
                pass

    def register_classes(self, classes: Sequence[DXFClass]) -> None:
        self.registry.target_doc.classes.register(classes)

    def map_resources(self) -> None:
        source_db = self.registry.source_doc.entitydb
        for block_key, block in self.copied_blocks.items():
            for source_entity_handle, copy in block.items():
                source_entity = source_db.get(source_entity_handle)
                if source_entity is None:
                    raise const.DXFInternalEzdxfError(
                        "database error, source entity not found"
                    )
                if copy is not None and copy.is_alive:
                    source_entity.map_resources(copy, self)

    def add_layer_entry(self, layer: Layer) -> None:
        tdoc = self.registry.target_doc
        layer_name = layer.dxf.name.upper()

        # special layers - only copy if not exist
        if layer_name in ("0", "DEFPOINTS") or validator.is_adsk_special_layer(
            layer_name
        ):
            try:
                special = tdoc.layers.get(layer_name)
            except const.DXFTableEntryError:
                special = None
            if special:
                # map copied layer handle to existing special layer
                self.replace_handle_mapping(layer.dxf.handle, special.dxf.handle)
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

    def restore_block_content(self, block_record: BlockRecord, handle: str) -> None:
        content = self.copied_blocks.get(handle, dict())
        block: Optional[Block] = None
        endblk: Optional[EndBlk] = None
        for entity in content.values():
            if isinstance(entity, (Block, EndBlk)):
                if isinstance(entity, Block):
                    block = entity
                else:
                    endblk = entity
            elif is_graphic_entity(entity):
                block_record.add_entity(entity)  # type: ignore
            else:
                name = block_record.dxf.name
                msg = f"skipping non-graphic DXF entity in BLOCK_RECORD('{name}', #{handle}): {str(entity)}"
                logging.warning(msg)  # this is a DXF structure error
                self.debug(msg)
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
        elif self.conflict_policy == ConflictPolicy.XREF_PREFIX:
            # always rename
            entity.dxf.name = get_unique_table_name(
                "{xref}${index}${name}", name, self.xref_name, table
            )
        elif self.conflict_policy == ConflictPolicy.NUM_PREFIX:
            if table.has_entry(name):  # rename only if exist
                entity.dxf.name = get_unique_table_name(
                    "${index}${name}", name, self.xref_name, table
                )
        table.add_entry(entity)

    def add_collection_entry(
        self, collection, entry: DXFEntity, system_entries: set[str]
    ) -> None:
        name = entry.dxf.name
        if name.upper() in system_entries:
            special = collection.object_dict.get(name)
            if special:
                self.replace_handle_mapping(entry.dxf.handle, special.dxf.handle)
                entry.destroy()
                return
        if self.conflict_policy == ConflictPolicy.KEEP:
            existing_entry = collection.get(name)
            if existing_entry:
                self.replace_handle_mapping(entry.dxf.handle, existing_entry.dxf.handle)
                entry.destroy()
                return
        elif self.conflict_policy == ConflictPolicy.XREF_PREFIX:
            # always rename
            entry.dxf.name = get_unique_table_name(
                "{xref}${index}${name}", name, self.xref_name, collection
            )

        elif self.conflict_policy == ConflictPolicy.NUM_PREFIX:
            if collection.has_entry(name):  # rename only if exist
                entry.dxf.name = get_unique_table_name(
                    "${index}${name}", name, self.xref_name, collection
                )
        collection.object_dict.add(entry.dxf.name, entry)

    def add_object_copies(self, copies: Iterable[DXFEntity]) -> None:
        """Add copied DXF objects to the OBJECTS section of the target document."""
        objects = self.registry.target_doc.objects
        for obj in copies:
            objects.add_object(obj)  # type: ignore

    def finalize(self) -> None:
        # remove replaced entities:
        self.registry.target_doc.entitydb.purge()


def get_xref_name(doc: Drawing) -> str:
    if doc.filename:
        return pathlib.Path(doc.filename).stem
    return ""


def is_special_block_name(name: str) -> bool:
    return False


def get_unique_table_name(fmt: str, name: str, xref: str, table) -> str:
    index: int = 0
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

        # mapping from the source entity handle to the handle of the copied entity
        self.handle_mapping: dict[str, str] = {}
        self.debug_messages: list[str] = []

    def debug(self, msg: str) -> None:
        self.debug_messages.append(msg)

    def copy_blocks(self, blocks: dict[str, dict[str, DXFEntity]]) -> None:
        for handle, block in blocks.items():
            self.copies[handle] = self.copy_block(block)

    def copy_block(self, block: dict[str, DXFEntity]) -> dict[str, DXFEntity]:
        copies: dict[str, DXFEntity] = {}
        tdoc = self.target_doc
        handle_mapping = self.handle_mapping

        for handle, entity in block.items():
            if isinstance(entity, DXFClass):
                self.copy_dxf_class(entity)
                continue
            clone = self.copy_entity(entity)
            if clone is None:
                continue
            factory.bind(clone, tdoc)
            handle_mapping[handle] = clone.dxf.handle
            # Get handle mapping for in-object copies: DICTIONARY
            if hasattr(entity, "get_handle_mapping"):
                self.handle_mapping.update(entity.get_handle_mapping(clone))

            if is_dxf_object(clone):
                self.objects.append(clone)
            else:
                copies[handle] = clone
        return copies

    def copy_entity(self, entity: DXFEntity) -> Optional[DXFEntity]:
        try:
            new_entity = entity.copy()
        except const.DXFError:
            self.debug(f"cannot copy entity {str(entity)}")
            return None
        # remove references for copy tracking, not valid in the target document
        new_entity.del_source_of_copy()
        new_entity.del_source_block_reference()
        return new_entity

    def copy_dxf_class(self, cls: DXFClass) -> None:
        self.classes.append(cls.copy())

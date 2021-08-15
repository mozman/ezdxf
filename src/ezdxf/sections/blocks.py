# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    Iterable,
    Iterator,
    Union,
    Sequence,
    List,
    cast,
)
from ezdxf.lldxf.const import (
    DXFStructureError,
    DXFBlockInUseError,
    DXFTableEntryError,
    DXFKeyError,
)
from ezdxf.lldxf import const
from ezdxf.entities import (
    factory,
    entity_linker,
    Block,
    EndBlk,
    BlockRecord,
    is_graphic_entity,
    Attrib,
)
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.render.arrows import ARROWS
from ezdxf.audit import Auditor, AuditError
from .table import table_key
import warnings
import logging

logger = logging.getLogger("ezdxf")

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter,
        Drawing,
        EntityDB,
        DXFEntity,
        DXFTagStorage,
        Table,
    )


def is_special_block(name: str) -> bool:
    name = name.upper()
    # Anonymous dimension, groups and table blocks do not have explicit
    # references by an INSERT entity:
    if is_anonymous_block(name):
        return True

    # Arrow blocks maybe used in DIMENSION or LEADER override without an
    # INSERT reference:
    if ARROWS.is_ezdxf_arrow(name):
        return True
    if name.startswith("_"):
        if ARROWS.is_acad_arrow(ARROWS.arrow_name(name)):
            return True

    return False


def is_anonymous_block(name: str) -> bool:
    # *U### = anonymous BLOCK, require an explicit INSERT to be in use
    # *E### = anonymous non-uniformly scaled BLOCK, requires INSERT?
    # *X### = anonymous HATCH graphic, requires INSERT?
    # *D### = anonymous DIMENSION graphic, has no explicit INSERT
    # *A### = anonymous GROUP, requires INSERT?
    # *T### = anonymous block for ACAD_TABLE, has no explicit INSERT
    return len(name) > 1 and name[0] == "*" and name[1] in "UEXDAT"


_MISSING_BLOCK_ = Block()


class BlocksSection:
    """
    Manages BLOCK definitions in a dict(), block names are case insensitive
    e.g. 'Test' == 'TEST'.

    """

    def __init__(
        self, doc: "Drawing" = None, entities: List["DXFEntity"] = None
    ):
        self.doc = doc
        if entities is not None:
            self.load(entities)
        self._reconstruct_orphaned_block_records()
        self._anonymous_block_counter = 0

    def __len__(self):
        return len(self.block_records)

    @staticmethod
    def key(entity: Union[str, "BlockLayout"]) -> str:
        if not isinstance(entity, str):
            entity = entity.name
        return entity.lower()  # block key is lower case

    @property
    def block_records(self) -> "Table":
        return self.doc.block_records  # type: ignore

    @property
    def entitydb(self) -> "EntityDB":
        return self.doc.entitydb  # type: ignore

    def load(self, entities: List["DXFEntity"]) -> None:
        """
        Load DXF entities into BlockLayouts. `entities` is a list of
        entity tags, separated by BLOCK and ENDBLK entities.

        """

        def load_block_record(
            block: Block,
            endblk: EndBlk,
            block_entities: List["DXFEntity"],
        ) -> "BlockRecord":
            try:
                block_record = cast(
                    "BlockRecord", block_records.get(block.dxf.name)
                )
            # Special case DXF R12 - has no BLOCK_RECORD table
            except DXFTableEntryError:
                block_record = cast(
                    "BlockRecord",
                    block_records.new(block.dxf.name, dxfattribs={"scale": 0}),
                )

            # The BLOCK_RECORD is the central object which stores all the
            # information about a BLOCK and also owns all the entities of
            # this block definition.
            block_record.set_block(block, endblk)
            for entity in block_entities:
                block_record.add_entity(entity)  # type: ignore
            return block_record

        def link_entities() -> Iterable["DXFEntity"]:
            linked = entity_linker()
            for entity in entities:
                # Do not store linked entities (VERTEX, ATTRIB, SEQEND) in
                # the block layout, linked entities ares stored in their
                # parent entity e.g. VERTEX -> POLYLINE:
                if not linked(entity):
                    yield entity

        block_records = self.block_records
        section_head = cast("DXFTagStorage", entities[0])
        if section_head.dxftype() != "SECTION" or section_head.base_class[
            1
        ] != (2, "BLOCKS"):
            raise DXFStructureError(
                "Critical structure error in BLOCKS section."
            )
        # Remove SECTION entity
        del entities[0]
        content: List["DXFEntity"] = []
        block: Block = _MISSING_BLOCK_
        for entity in link_entities():
            if isinstance(entity, Block):
                if block is not _MISSING_BLOCK_:
                    logger.warning("Missing required ENDBLK, ignoring content.")
                block = entity
                content.clear()
            elif isinstance(entity, EndBlk):
                if block is _MISSING_BLOCK_:
                    logger.warning(
                        "Found ENDBLK without a preceding BLOCK, ignoring content."
                    )
                else:
                    block_record = load_block_record(block, entity, content)
                    self.add(block_record)
                    block = _MISSING_BLOCK_
                content.clear()
            else:
                # No check for valid entities here:
                # Use the audit- or the recover module to fix invalid DXF files!
                content.append(entity)

    def _reconstruct_orphaned_block_records(self):
        """Find BLOCK_RECORD entries without block definition in the blocks
        section and create block definitions for this orphaned block records.

        """
        for block_record in self.block_records:
            if block_record.block is None:
                block = factory.create_db_entry(
                    "BLOCK",
                    dxfattribs={
                        "name": block_record.dxf.name,
                        "base_point": (0, 0, 0),
                    },
                    doc=self.doc,
                )
                endblk = factory.create_db_entry(
                    "ENDBLK",
                    dxfattribs={},
                    doc=self.doc,
                )
                block_record.set_block(block, endblk)
                self.add(block_record)

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        tagwriter.write_str("  0\nSECTION\n  2\nBLOCKS\n")
        for block_record in self.block_records:
            assert isinstance(block_record, BlockRecord)
            block_record.export_block_definition(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    def add(self, block_record: "BlockRecord") -> "BlockLayout":
        """Add or replace a block layout object defined by its block record.
        (internal API)
        """
        block_layout = BlockLayout(block_record)
        block_record.block_layout = block_layout
        assert self.block_records.has_entry(block_record.dxf.name)
        return block_layout

    def __iter__(self) -> Iterator["BlockLayout"]:
        """Iterable of all :class:`~ezdxf.layouts.BlockLayout` objects."""
        return (
            block_record.block_layout  # type: ignore
            for block_record in self.block_records
        )

    def __contains__(self, name: str) -> bool:
        """Returns ``True`` if :class:`~ezdxf.layouts.BlockLayout` `name`
        exist.
        """
        return self.block_records.has_entry(name)

    def __getitem__(self, name: str) -> "BlockLayout":
        """Returns :class:`~ezdxf.layouts.BlockLayout` `name`,
        raises :class:`DXFKeyError` if `name` not exist.
        """
        try:
            block_record = cast("BlockRecord", self.block_records.get(name))
            return block_record.block_layout  # type: ignore
        except DXFTableEntryError:
            raise DXFKeyError(name)

    def __delitem__(self, name: str) -> None:
        """Deletes :class:`~ezdxf.layouts.BlockLayout` `name` and all of
        its content, raises :class:`DXFKeyError` if `name` not exist.
        """
        if name in self:
            self.block_records.remove(name)
        else:
            raise DXFKeyError(name)

    def get(self, name: str, default=None) -> "BlockLayout":
        """Returns :class:`~ezdxf.layouts.BlockLayout` `name`, returns
        `default` if `name` not exist.
        """
        try:
            return self.__getitem__(name)
        except DXFKeyError:
            return default

    def get_block_layout_by_handle(
        self, block_record_handle: str
    ) -> "BlockLayout":
        """Returns a block layout by block record handle. (internal API)"""
        return self.doc.entitydb[block_record_handle].block_layout  # type: ignore

    def new(
        self,
        name: str,
        base_point: Sequence[float] = (0, 0),
        dxfattribs: dict = None,
    ) -> "BlockLayout":
        """Create and add a new :class:`~ezdxf.layouts.BlockLayout`, `name`
        is the BLOCK name, `base_point` is the insertion point of the BLOCK.
        """
        assert self.doc is not None
        block_record = cast(BlockRecord, self.doc.block_records.new(name))

        dxfattribs = dxfattribs or {}
        dxfattribs["owner"] = block_record.dxf.handle
        dxfattribs["name"] = name
        dxfattribs["base_point"] = base_point
        head = factory.create_db_entry("BLOCK", dxfattribs, self.doc)
        tail = factory.create_db_entry(
            "ENDBLK", {"owner": block_record.dxf.handle}, doc=self.doc
        )
        block_record.set_block(head, tail)  # type: ignore
        return self.add(block_record)

    def new_anonymous_block(
        self, type_char: str = "U", base_point: Sequence[float] = (0, 0)
    ) -> "BlockLayout":
        """Create and add a new anonymous :class:`~ezdxf.layouts.BlockLayout`,
        `type_char` is the BLOCK type, `base_point` is the insertion point of
        the BLOCK.

            ========= ==========
            type_char Anonymous Block Type
            ========= ==========
            ``'U'``   ``'*U###'`` anonymous BLOCK
            ``'E'``   ``'*E###'`` anonymous non-uniformly scaled BLOCK
            ``'X'``   ``'*X###'`` anonymous HATCH graphic
            ``'D'``   ``'*D###'`` anonymous DIMENSION graphic
            ``'A'``   ``'*A###'`` anonymous GROUP
            ``'T'``   ``'*T###'`` anonymous block for ACAD_TABLE content
            ========= ==========

        """
        blockname = self.anonymous_blockname(type_char)
        block = self.new(blockname, base_point, {"flags": const.BLK_ANONYMOUS})
        return block

    def anonymous_blockname(self, type_char: str) -> str:
        """Create name for an anonymous block. (internal API)

        Args:
            type_char: letter

                U = *U### anonymous blocks
                E = *E### anonymous non-uniformly scaled blocks
                X = *X### anonymous hatches
                D = *D### anonymous dimensions
                A = *A### anonymous groups
                T = *T### anonymous ACAD_TABLE content

        """
        while True:
            self._anonymous_block_counter += 1
            blockname = f"*{type_char}{self._anonymous_block_counter}"
            if not self.__contains__(blockname):
                return blockname

    def rename_block(self, old_name: str, new_name: str) -> None:
        """Rename :class:`~ezdxf.layouts.BlockLayout` `old_name` to `new_name`"""
        block_record = cast(BlockRecord, self.block_records.get(old_name))
        block_record.rename(new_name)
        self.block_records.replace(old_name, block_record)
        self.add(block_record)

    def delete_block(self, name: str, safe: bool = True) -> None:
        """
        Delete block. If `save` is ``True``, check if block is still referenced.

        Args:
            name: block name (case insensitive)
            safe: check if block is still referenced or special block without
                  explicit references

        Raises:
            DXFKeyError: if block not exists
            DXFBlockInUseError: if block is still referenced, and save is True

        """
        if safe:
            if is_special_block(name):
                raise DXFBlockInUseError(
                    f'Special block "{name}" maybe used without explicit INSERT entity.'
                )
            assert self.doc is not None
            block_refs = self.doc.query(
                f"INSERT[name=='{name}']i"
            )  # ignore case
            if len(block_refs):
                raise DXFBlockInUseError(f'Block "{name}" is still in use.')
        self.__delitem__(name)

    def delete_all_blocks(self) -> None:
        """Delete all blocks without references except modelspace- or
        paperspace layout blocks, special arrow- and anonymous blocks
        (DIMENSION, ACAD_TABLE).

        .. warning::

            There could exist undiscovered references to blocks which are
            not documented in the DXF reference, hidden in extended data
            sections or application defined data, which could produce invalid
            DXF documents if such referenced blocks will be deleted.

        .. versionchanged:: 0.14
            removed unsafe mode

        """
        assert self.doc is not None
        active_references = set(
            table_key(entity.dxf.name) for entity in self.doc.query("INSERT")
        )

        def is_safe(name: str) -> bool:
            if is_special_block(name):
                return False
            return name not in active_references

        trash = set()
        for block in self:
            name = table_key(block.name)
            if not block.is_any_layout and is_safe(name):
                trash.add(name)

        for name in trash:
            self.__delitem__(name)

    def purge(self):
        """Purge functionality removed! - it was just too dangerous!
        The method name suggests a functionality and quality similar
        to that of a CAD application, which can not be delivered!
        """
        warnings.warn(
            "Blocks.purge() deactivated, unsafe operation!", DeprecationWarning
        )

    def audit(self, auditor: Auditor) -> None:
        """Audit and repair BLOCKS section.

        .. important::

            Do not delete entities while auditing process, because this
            would alter the entity database while iterating, instead use::

                auditor.trash(entity)

            to delete invalid entities after auditing automatically.

        """
        assert self.doc is auditor.doc, "Auditor for different DXF document."

        for block_record in self.block_records:
            assert isinstance(block_record, BlockRecord)
            for entity in block_record.entity_space:
                if not is_graphic_entity(entity):
                    auditor.fixed_error(
                        code=AuditError.REMOVED_INVALID_GRAPHIC_ENTITY,
                        message=f"Removed invalid DXF entity {str(entity)} from"
                                f" BLOCK '{block_record.dxf.name}'.",
                    )
                    auditor.trash(entity)
                elif isinstance(entity, Attrib):
                    # ATTRIB can only exist as an attached entity of the INSERT
                    # entity!
                    auditor.fixed_error(
                        code=AuditError.REMOVED_STANDALONE_ATTRIB_ENTITY,
                        message=f"Removed standalone {str(entity)} entity from"
                                f" BLOCK '{block_record.dxf.name}'.",
                    )
                    auditor.trash(entity)


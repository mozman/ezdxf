#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

"""
Resource management module for transferring DXF resources between documents.

Planning state!!!

"""
from __future__ import annotations
from typing import Iterable, Optional, Sequence
from typing_extensions import Protocol

from ezdxf.lldxf.const import DXFError, DXFTableEntryError
from ezdxf.document import Drawing
from ezdxf.layouts import BaseLayout

from ezdxf.entities import (
    is_graphic_entity,
    is_dxf_object,
    DXFEntity,
    DXFClass,
    factory,
)


__all__ = ["ResourceTransfer"]


class ResourceTransfer(Protocol):
    def add_entity(self, entity: DXFEntity) -> None:
        ...

    def get_copy(self, uid: int) -> Optional[DXFEntity]:
        ...


def import_entities(entities: Sequence[DXFEntity], target: BaseLayout):
    doc: Drawing = target.doc
    assert doc is not None, "valid target document required"
    objects = doc.objects
    transfer = Transfer()
    for e in entities:
        e.register_resources(transfer)

    cpm = CopyMachine()
    cpm.copy(transfer.source_entities())
    transfer.set_copied_entities(cpm.copies)
    if cpm.classes:
        doc.classes.register(cpm.classes)

    new_entities: list[DXFEntity] = []
    replace: list[tuple[DXFEntity, DXFEntity]] = []

    for e in cpm.copies.values():
        if e.dxf.owner is not None:
            continue  # already processed!

        # 1. assign entity to document
        factory.bind(e, doc)

        # 2. add copied resources to tables and collections
        # TODO: resolve resource conflicts
        dxftype = e.dxftype()
        if dxftype == "LAYER":
            try:
                doc.layers.add_entry(e)  # type: ignore
            except DXFTableEntryError:
                # use existing layer
                replace.append((e, doc.layers.get(e.dxf.name)))
        elif dxftype == "LINETYPE":
            doc.linetypes.add_entry(e)  # type: ignore
        elif dxftype == "STYLE":
            doc.styles.add_entry(e)  # type: ignore
        elif dxftype == "DIMSTYLE":
            doc.dimstyles.add_entry(e)  # type: ignore
        elif dxftype == "APPID":
            try:
                doc.appids.add_entry(e)  # type: ignore
            except DXFTableEntryError:
                pass
        elif dxftype == "UCS":
            doc.ucs.add_entry(e)  # type: ignore
        elif dxftype == "BLOCK_RECORD":
            doc.block_records.add_entry(e)  # type: ignore
        elif dxftype == "MATERIAL":
            objects.add_object(e)  # type: ignore
            add_collection_entry(doc.materials, e)
        elif dxftype == "MLINESTYLE":
            objects.add_object(e)  # type: ignore
            add_collection_entry(doc.mline_styles, e)
        elif dxftype == "MLEADERSTYLE":
            objects.add_object(e)  # type: ignore
            add_collection_entry(doc.mleader_styles, e)
        else:
            new_entities.append(e)

    for old, new in replace:
        transfer.replace(old, new)
        old.destroy()

    # 3. copy resources
    for e in entities:
        copy = transfer.get_copy(id(e))
        e.copy_resources(copy, transfer)

    # 4. add entities to layout and objects section
    for e in new_entities:
        if e.dxf.owner is not None:
            continue  # already processed!
        if is_graphic_entity(e):
            target.add_entity(e)  # type: ignore
        elif is_dxf_object(e):
            objects.add_object(e)  # type: ignore


def add_collection_entry(collection, entry: DXFEntity):
    collection.object_dict.add(entry.dxf.name, entry)


class Transfer:
    def __init__(self):
        self._source_entities: list[DXFEntity] = []
        self._copied_entities: dict[int, DXFEntity] = {}

    def source_entities(self):
        return self._source_entities

    def set_copied_entities(self, entities: dict[int, DXFEntity]):
        self._copied_entities = entities

    def add_entity(self, entity: DXFEntity) -> None:
        self._source_entities.append(entity)

    def get_copy(self, uid: int) -> Optional[DXFEntity]:
        return self._copied_entities.get(uid)

    def replace(self, old: DXFEntity, new: DXFEntity) -> None:
        self._copied_entities[id(old)] = new


class CopyMachine:
    def __init__(self) -> None:
        self.copies: dict[int, DXFEntity] = dict()
        self.classes: list[DXFClass] = []
        self.log: list[str] = []

    def copy(self, entities: Iterable[DXFEntity]):
        for entity in entities:
            if isinstance(entity, DXFClass):
                self._copy_dxf_class(entity)
                continue
            if id(entity) in self.copies:
                continue

            try:
                self.copies[id(entity)] = entity.copy()
            except DXFError:
                self.log.append(f"cannot copy {str(entity)}")

    def _copy_dxf_class(self, cls: DXFClass) -> None:
        self.classes.append(cls.copy())

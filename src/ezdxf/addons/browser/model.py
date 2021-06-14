#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Any, List
from .typehints import SectionDict, EntityIndex
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import render_tag
from PyQt5.QtCore import QModelIndex, QAbstractTableModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

__all__ = [
    "DXFTagsModel",
    "DXFStructureModel",
    "EntityContainer",
    "Entity",
    "build_entity_index",
]

DXFTagsRole = Qt.UserRole + 1


def name_fmt(handle, name: str) -> str:
    return f"<{handle}> {name}"


def build_entity_index(sections: SectionDict) -> EntityIndex:
    entity_index = dict()
    for section in sections.values():
        for entity in section:
            try:
                handle = entity.get_handle()
                entity_index[handle] = entity
            except ValueError:
                pass
    return entity_index


class DXFTagsModel(QAbstractTableModel):
    def __init__(self, tags: Tags):
        super().__init__()
        self._tags = tags
        self._dxftype = ""
        if tags and tags[0].code == 0:
            self._dxftype = tags[0].value

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            tag = self._tags[row]
            return render_tag(tag, col)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._tags)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 3

    def dxftype(self) -> str:
        return self._dxftype


class Header(QStandardItem):
    def __init__(self, name: str, header_vars: Tags):
        super().__init__()
        self.setEditable(False)
        self._header_vars = header_vars
        self._section_name = name
        self.setText(self._section_name)

    def data(self, role: int = ...) -> Any:
        if role == DXFTagsRole:
            return self._header_vars
        else:
            return super().data(role)


class EntityContainer(QStandardItem):
    def __init__(self, name: str, entities: List[Tags]):
        super().__init__()
        self.setEditable(False)
        self.setText(name)
        self.setup_content(entities)

    def setup_content(self, entities):
        self.appendRows(Entity(e) for e in entities)


class Classes(EntityContainer):
    def setup_content(self, entities):
        self.appendRows(Class(e) for e in entities)


class AcDsData(EntityContainer):
    def setup_content(self, entities):
        self.appendRows(AcDsEntry(e) for e in entities)


class NamedEntityContainer(EntityContainer):
    def setup_content(self, entities):
        self.appendRows(NamedEntity(e) for e in entities)


class Tables(EntityContainer):
    def setup_content(self, entities):
        container = []
        name = ""
        for e in entities:
            dxftype = e.dxftype()
            if dxftype == "TABLE":
                try:
                    handle = e.get_handle()
                except ValueError:
                    handle = None
                name = e.get_first_value(2, default="UNDEFINED")
                name = name_fmt(handle, name)
            elif dxftype == "ENDTAB":
                if container:
                    self.appendRow(NamedEntityContainer(name, container))
                container.clear()
            else:
                container.append(e)


class Blocks(EntityContainer):
    def setup_content(self, entities):
        container = []
        name = "UNDEFINED"
        for e in entities:
            dxftype = e.dxftype()
            if dxftype == "BLOCK":
                try:
                    handle = e.get_handle()
                except ValueError:
                    handle = None
                name = e.get_first_value(2, default="UNDEFINED")
                name = name_fmt(handle, name)
            elif dxftype == "ENDBLK":
                if container:
                    self.appendRow(EntityContainer(name, container))
                container.clear()
            else:
                container.append(e)


def get_section_name(section: List[Tags]) -> str:
    if len(section) > 0:
        header = section[0]
        if len(header) > 1 and header[0].code == 0 and header[1].code == 2:
            return header[1].value
    return "INVALID SECTION HEADER!"


class Entity(QStandardItem):
    def __init__(self, tags: Tags):
        super().__init__()
        self.setEditable(False)
        self._tags = tags
        self._entity_name = "INVALID ENTITY!"
        try:
            self._handle = tags.get_handle()
        except ValueError:
            self._handle = None
        if tags and tags[0].code == 0:
            self._entity_name = name_fmt(str(self._handle), tags[0].value)
        self.setText(self._entity_name)

    def data(self, role: int = ...) -> Any:
        if role == DXFTagsRole:
            return self._tags
        else:
            return super().data(role)


class NamedEntity(Entity):
    def __init__(self, tags: Tags):
        super().__init__(tags)
        name = tags.get_first_value(2, "<noname>")
        self._entity_name = name_fmt(str(self._handle), name)
        self.setText(self._entity_name)


class Class(QStandardItem):
    def __init__(self, tags: Tags):
        super().__init__()
        self.setEditable(False)
        self._tags = tags
        self._class_name = "INVALID CLASS!"
        if len(tags) > 1 and tags[0].code == 0 and tags[1].code == 1:
            self._class_name = tags[1].value
        self.setText(self._class_name)

    def data(self, role: int = ...) -> Any:
        if role == DXFTagsRole:
            return self._tags
        else:
            return super().data(role)


class AcDsEntry(QStandardItem):
    def __init__(self, tags: Tags):
        super().__init__()
        self.setEditable(False)
        self._tags = tags
        self._name = tags[0].value
        self.setText(self._name)


class DXFStructureModel(QStandardItemModel):
    def __init__(self, filename: str, sections: SectionDict):
        super().__init__()
        root = QStandardItem(filename)
        root.setEditable(False)
        self.appendRow(root)
        self._sections = sections
        for section in self._sections.values():
            name = get_section_name(section)
            if name == "HEADER":
                header_vars = section[0]
                row = Header(name, header_vars)
            elif name == "CLASSES":
                row = Classes(name, section[1:])
            elif name == "TABLES":
                row = Tables(name, section[1:])
            elif name == "BLOCKS":
                row = Blocks(name, section[1:])
            elif name == "ACDSDATA":
                row = AcDsData(name, section[1:])
            else:
                row = EntityContainer(name, section[1:])
            root.appendRow(row)

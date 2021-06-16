#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Any, List
from ezdxf.lldxf.types import render_tag, DXFVertex
from PyQt5.QtCore import QModelIndex, QAbstractTableModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from .tags import compile_tags, Tags

__all__ = [
    "DXFTagsModel",
    "DXFStructureModel",
    "EntityContainer",
    "Entity",
    "DXFTagsRole",
]

DXFTagsRole = Qt.UserRole + 1


def name_fmt(handle, name: str) -> str:
    return f"<{handle}> {name}"


HEADER_LABELS = ["Group Code", "Data Type", "Content", "4", "5"]


def calc_line_numbers(start: int, tags: Tags) -> List[int]:
    numbers = [start]
    index = start
    for tag in tags:
        if isinstance(tag, DXFVertex):
            index += len(tag.value) * 2
        else:
            index += 2
        numbers.append(index)
    return numbers


class DXFTagsModel(QAbstractTableModel):
    def __init__(self, tags: Tags, start_line_number: int = 1):
        super().__init__()
        self._tags = compile_tags(tags)
        self._line_numbers = calc_line_numbers(start_line_number, self._tags)
        if tags and tags[0].code == 0:
            self._dxftype = tags[0].value

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            tag = self._tags[row]
            return render_tag(tag, col)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> Any:
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return HEADER_LABELS[section]
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        elif orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                return self._line_numbers[section]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._tags)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 3


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
            container.append(e)
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
                    container.pop()  # remove ENDTAB
                    self.appendRow(NamedEntityContainer(name, container))
                container.clear()


class Blocks(EntityContainer):
    def setup_content(self, entities):
        container = []
        name = "UNDEFINED"
        for e in entities:
            container.append(e)
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
        try:
            self._handle = tags.get_handle()
        except ValueError:
            self._handle = None
        self.setText(self.entity_name())

    def entity_name(self):
        name = "INVALID ENTITY!"
        tags = self._tags
        if tags and tags[0].code == 0:
            name = name_fmt(str(self._handle), tags[0].value)
        return name

    def data(self, role: int = ...) -> Any:
        if role == DXFTagsRole:
            return self._tags
        else:
            return super().data(role)


class Header(Entity):
    def entity_name(self):
        return "HEADER"


class NamedEntity(Entity):
    def entity_name(self):
        name = self._tags.get_first_value(2, "<noname>")
        return name_fmt(str(self._handle), name)


class Class(Entity):
    def entity_name(self):
        tags = self._tags
        name = "INVALID CLASS!"
        if len(tags) > 1 and tags[0].code == 0 and tags[1].code == 1:
            name = tags[1].value
        return name


class AcDsEntry(Entity):
    def entity_name(self):
        return self._tags[0].value


class DXFStructureModel(QStandardItemModel):
    def __init__(self, filename: str, doc):
        super().__init__()
        root = QStandardItem(filename)
        root.setEditable(False)
        self.appendRow(root)
        for section in doc.sections.values():
            name = get_section_name(section)
            if name == "HEADER":
                header_vars = section[0]
                row = Header(header_vars)
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

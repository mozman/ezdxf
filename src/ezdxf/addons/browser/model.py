#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Any, List
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import render_tag
from ezdxf.lldxf.loader import SectionDict
from PyQt5.QtCore import QModelIndex, QAbstractListModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

__all__ = [
    "DXFTagsModel",
    "DXFStructureModel",
    "Section",
    "Entity",
]


class DXFTagsModel(QAbstractListModel):
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
        self._header_vars = header_vars
        self._section_name = name
        self.setText(self._section_name)


class Section(QStandardItem):
    def __init__(self, name: str, entities: List[Tags]):
        super().__init__()
        self._section_name = name
        self.setText(self._section_name)
        self.setup_content(entities)

    def setup_content(self, entities):
        self.appendRows(Entity(e) for e in entities)


class Classes(Section):
    def setup_content(self, entities):
        self.appendRows(Class(e) for e in entities)


class Tables(Section):
    ...


class Blocks(Section):
    ...


def get_section_name(section: List[Tags]) -> str:
    if len(section) > 0:
        header = section[0]
        if len(header) > 1 and header[0].code == 0 and header[1].code == 2:
            return header[1].value
    return "INVALID SECTION HEADER!"


class Entity(QStandardItem):
    def __init__(self, tags: Tags):
        super().__init__()
        self._tags = tags
        self._entity_name = "INVALID ENTITY!"
        try:
            self._handle = tags.get_handle()
        except ValueError:
            self._handle = None
        if tags and tags[0].code == 0:
            self._entity_name = tags[0].value + f"(#{str(self._handle)})"
        self.setText(self._entity_name)


class Class(QStandardItem):
    def __init__(self, tags: Tags):
        super().__init__()
        self._tags = tags
        self._class_name = "INVALID CLASS!"
        if len(tags) > 1 and tags[0].code == 0 and tags[1].code == 1:
            self._class_name = tags[1].value
        self.setText(self._class_name)


class DXFStructureModel(QStandardItemModel):
    def __init__(self, filename: str, sections: SectionDict):
        super().__init__()
        root = QStandardItem(filename)
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
            else:
                row = Section(name, section[1:])
            root.appendRow(row)

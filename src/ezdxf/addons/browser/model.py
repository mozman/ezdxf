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


class Section(QStandardItem):
    def __init__(self, entities: List[Tags]):
        self._entities = entities
        self._section_name = "INVALID SECTION HEADER!"
        if len(entities) > 0:
            header = entities[0]
            if len(header) > 1 and header[0].code == 0 and header[1].code == 2:
                self._section_name = header[1].value
        super().__init__(self._section_name)
        if entities:
            self.appendRow([Entity(e) for e in self._entities])


class Entity(QStandardItem):
    def __init__(self, tags: Tags):
        self._tags = tags
        self._entity_name = "INVALID ENTITY!"
        try:
            self._handle = tags.get_handle()
        except ValueError:
            self._handle = None
        if tags and tags[0].code == 0:
            self._entity_name = tags[0].value + f"(#{str(self._handle)})"
        super().__init__(self._entity_name)


class DXFStructureModel(QStandardItemModel):
    def __init__(self, sections: SectionDict):
        super().__init__()
        self._sections = sections
        for section in self._sections.values():
            self.appendRow([Section(section)])

#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Any
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.lldxf.types import render_tag
from PyQt5.QtCore import QModelIndex, QAbstractListModel, Qt


__all__ = ["render_tag", "DXFTagsModel"]

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

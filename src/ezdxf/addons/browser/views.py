#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import typing
from PyQt5.QtWidgets import QTableView, QTreeView
from PyQt5.QtCore import QModelIndex

if typing.TYPE_CHECKING:
    from ezdxf.eztypes import Tags


class StructureTree(QTreeView):
    def set_structure(self, model):
        self.setModel(model)
        self.expand(model.index(0, 0, QModelIndex()))
        self.setHeaderHidden(True)

    def expand_to_entity(self, entity: "Tags"):
        model = self.model()
        index = model.index_of_entity(entity)
        self.setCurrentIndex(index)


class DXFTagsTable(QTableView):
    def __init__(self):
        super().__init__()
        col_header = self.horizontalHeader()
        col_header.setStretchLastSection(True)
        row_header = self.verticalHeader()
        row_header.setDefaultSectionSize(24)  # default row height in pixels
        self.setSelectionBehavior(QTableView.SelectRows)

    def first_selected_row(self) -> int:
        first_row: int = 0
        selection = self.selectedIndexes()
        if selection:
            first_row = selection[0].row()
        return first_row

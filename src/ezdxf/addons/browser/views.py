#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from PyQt5.QtWidgets import QTableView, QTreeView
from PyQt5.QtCore import QModelIndex


class StructureTree(QTreeView):
    def set_structure(self, model):
        self.setModel(model)
        self.expand(model.index(0, 0, QModelIndex()))
        self.setHeaderHidden(True)


class DXFTagsTable(QTableView):
    def __init__(self):
        super().__init__()
        col_header = self.horizontalHeader()
        col_header.setStretchLastSection(True)
        row_header = self.verticalHeader()
        row_header.setDefaultSectionSize(24)  # default row height in pixels
        self.setSelectionBehavior(QTableView.SelectRows)

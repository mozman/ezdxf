#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from PyQt5.QtWidgets import QTableView, QTreeView
from PyQt5.QtCore import QModelIndex, Qt


class StructureTree(QTreeView):
    def set_structure(self, model):
        self.setModel(model)
        self.expand(model.index(0, 0, QModelIndex()))
        self.setHeaderHidden(True)


class DXFTagsTable(QTableView):
    def __init__(self):
        super().__init__()
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        self.setSelectionBehavior(QTableView.SelectRows)

#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from PyQt5 import QtWidgets
from PyQt5.QtCore import QModelIndex


class StructureTree(QtWidgets.QTreeView):
    def set_structure(self, model):
        self.setModel(model)
        self.expand(model.index(0, 0, QModelIndex()))
        self.setHeaderHidden(True)


class DXFTagsTable(QtWidgets.QTableView):
    def __init__(self):
        super().__init__()
        self.verticalHeader().hide()
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
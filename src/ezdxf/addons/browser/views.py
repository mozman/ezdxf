#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from PyQt5 import QtWidgets
from PyQt5.QtCore import QModelIndex


class StructureTree(QtWidgets.QTreeView):
    def set_document(self, model):
        self.setModel(model)
        self.expand(model.index(0, 0, QModelIndex()))
        self.setHeaderHidden(True)

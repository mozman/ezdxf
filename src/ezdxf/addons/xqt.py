#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

# Qt compatibility layer: all Qt imports from ezdxf.addons.xqt
PYSIDE6 = False
TRY_PYSIDE6 = True  # set to False only for testing
PYQT5 = False
TRY_PYQT5 = True  # set to False only for testing

if TRY_PYSIDE6:
    try:
        from PySide6 import QtGui, QtCore, QtWidgets
        from PySide6.QtCore import Signal
        from PySide6.QtCore import Slot
        from PySide6.QtGui import QAction

        PYSIDE6 = True
        print("using PySide6")
    except ImportError:
        pass

# PyQt5 is just a fallback
if TRY_PYQT5 and not PYSIDE6:
    try:
        from PyQt5 import QtGui, QtCore, QtWidgets
        from PyQt5.QtCore import pyqtSignal as Signal
        from PyQt5.QtCore import pyqtSlot as Slot
        from PyQt5.QtWidgets import QAction

        PYQT5 = True
        print("using PyQt5")
    except ImportError:
        pass

if not (PYSIDE6 or PYQT5):
    raise ImportError("no Qt binding found, tried PySide6 and PyQt5")

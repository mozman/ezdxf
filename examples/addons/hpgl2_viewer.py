#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
try:
    from ezdxf.addons.xqt import QtWidgets
except ImportError as e:
    print(str(e))
    exit(1)
import sys
import pathlib
import signal
from ezdxf.addons.hpgl2.viewer import HPGL2Viewer

HPGL2_EXAMPLES = pathlib.Path(__file__).parent.parent.parent / "examples_hpgl2"


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # handle Ctrl+C properly
    app = QtWidgets.QApplication(sys.argv)
    viewer = HPGL2Viewer()
    # viewer.show()
    viewer.load_plot_file(HPGL2_EXAMPLES / "BF_ISO.plt")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

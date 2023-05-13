import argparse
import signal
import sys
from typing import Optional

import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing.qtviewer import (
    CADGraphicsViewWithOverlay,
    CADWidget,
    CADViewer,
)
from ezdxf.addons.xqt import QtCore as qc, QtGui as qg, QtWidgets as qw
from ezdxf.audit import Auditor
from ezdxf.document import Drawing
from ezdxf.entities import DXFGraphic


class ElementSelectorView(CADGraphicsViewWithOverlay):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected = None

    def keyPressEvent(self, event: qg.QKeyEvent) -> None:
        if event.key() == qc.Qt.Key_Return:
            element = self.current_hovered_element
            if element is not None:
                self.selected = element
                self.close()


def select_element(
    doc: Drawing, layout: str = "Model", show_controls: bool = False
) -> Optional[DXFGraphic]:
    app = qw.QApplication.instance()
    if app is None:
        signal.signal(signal.SIGINT, signal.SIG_DFL)  # handle Ctrl+C properly
        app = qw.QApplication([])

    view = ElementSelectorView()
    cad = CADWidget(view)
    if show_controls:
        viewer = CADViewer(cad=cad)
        view.closing.connect(viewer.close)
        viewer.set_document(doc, Auditor(doc), layout=layout)
        viewer.show()
    else:
        cad.set_document(doc, layout=layout)
        cad.show()
    app.exec()
    return view.selected


def main():
    parser = argparse.ArgumentParser(description="Press enter to select a CAD element")
    parser.add_argument("cad_file", nargs="?")
    parser.add_argument(
        "--show_controls",
        action="store_true",
        help="whether to show GUI controls or just the CAD view",
    )
    parser.add_argument("--layout", default="Model", help="the layout to select from")
    args = parser.parse_args()

    if args.cad_file is None:
        print("no CAD file specified")
        sys.exit(1)

    try:
        doc = ezdxf.readfile(args.cad_file)
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(2)
    except ezdxf.DXFError:
        try:
            doc, auditor = recover.readfile(args.cad_file)
        except ezdxf.DXFStructureError:
            print(f"Invalid or corrupted DXF file: {args.cad_file}")
            sys.exit(3)

    selected_element = select_element(
        doc, layout=args.layout, show_controls=args.show_controls
    )
    print(f"element selected: {selected_element}")


if __name__ == "__main__":
    main()

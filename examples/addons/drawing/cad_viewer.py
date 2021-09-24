#!/usr/bin/env python3
# Copyright (c) 2020-2021, Matthew Broadway
# License: MIT License
import argparse
import signal
import sys

from PyQt5 import QtWidgets as qw

import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing.qtviewer import CadViewer
from ezdxf.addons.drawing.config import Configuration, LinePolicy

# IMPORTANT: This example is just a remaining skeleton, the implementation
# details moved into module: ezdxf.addon.drawing.qtviewer
#
# The CAD viewer can be executed by the new ezdxf command line launcher:
# C:\> ezdxf view FILE

# Load and draw proxy graphic:
ezdxf.options.preserve_proxy_graphics()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cad_file")
    parser.add_argument("--layout", default="Model")
    parser.add_argument(
        "--ltype", default="internal", choices=["internal", "ezdxf"]
    )

    # disable lineweight at all by default:
    parser.add_argument("--lineweight_scaling", type=float, default=0)
    args = parser.parse_args()

    # setup drawing add-on configuration
    config = Configuration.defaults()
    config = config.with_changes(
        line_policy=LinePolicy.ACCURATE
        if args.ltype == "ezdxf"
        else config.line_policy,
        lineweight_scaling=args.lineweight_scaling,
    )

    signal.signal(signal.SIGINT, signal.SIG_DFL)  # handle Ctrl+C properly
    app = qw.QApplication(sys.argv)
    v = CadViewer(config=config)
    if args.cad_file is not None:
        try:
            doc, auditor = recover.readfile(args.cad_file)
        except IOError:
            print(f"Not a DXF file or a generic I/O error: {args.cad_file}")
            sys.exit(1)
        except ezdxf.DXFStructureError:
            print(f"Invalid or corrupted DXF file: {args.cad_file}")
            sys.exit(2)

        v.set_document(doc, auditor)
        try:
            v.draw_layout(args.layout)
        except KeyError:
            print(
                f'could not find layout "{args.layout}". Valid layouts: {[l.name for l in v.doc.layouts]}'
            )
            sys.exit(3)
    sys.exit(app.exec_())


if __name__ == "__main__":
    print(f"C-Extension: {ezdxf.options.use_c_ext}")
    _main()

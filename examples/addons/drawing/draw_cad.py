#!/usr/bin/env python3
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import argparse
import sys

import matplotlib.pyplot as plt

import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, LinePolicy

from ezdxf.tools import fonts

# The "draw_cad.py" viewer can be executed by the new ezdxf command line
# launcher:
#
# C:\> ezdxf draw FILE
#
# This file remains as an example for the usage of the Matplotlib backend.
#
# For the case automatic font loading is disabled:
fonts.load()


def _main():
    parser = argparse.ArgumentParser(
        description="draw the given CAD file and save it to a file or view it"
    )
    parser.add_argument("cad_file", nargs="?")
    parser.add_argument("--supported_formats", action="store_true")
    parser.add_argument("--layout", default="Model")
    parser.add_argument("--out", required=False)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--ltype", default="internal")
    args = parser.parse_args()

    if args.supported_formats:
        fig = plt.figure()
        for (
            extension,
            description,
        ) in fig.canvas.get_supported_filetypes().items():
            print(f"{extension}: {description}")
        sys.exit()

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
    else:
        auditor = doc.audit()

    if auditor.has_errors:
        # But is most likely good enough for rendering.
        print(f"Found {len(auditor.errors)} unrecoverable errors.")
    if auditor.has_fixes:
        print(f"Fixed {len(auditor.fixes)} errors.")

    try:
        layout = doc.layouts.get(args.layout)
    except KeyError:
        print(
            f'Could not find layout "{args.layout}". '
            f"Valid layouts: {[l.name for l in doc.layouts]}"
        )
        sys.exit(4)

    # setup drawing add-on configuration
    config = Configuration.defaults()
    config = config.with_changes(
        line_policy=LinePolicy.ACCURATE
        if args.ltype == "ezdxf"
        else config.line_policy
    )

    fig: plt.Figure = plt.figure(dpi=args.dpi)
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out, config=config).draw_layout(layout, finalize=True)
    if args.out is not None:
        print(f'saving to "{args.out}"')
        fig.savefig(args.out, dpi=args.dpi)
        plt.close(fig)
    else:
        plt.show()


if __name__ == "__main__":
    _main()

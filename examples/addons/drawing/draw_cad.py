#!/usr/bin/env python3
# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import argparse
import sys

import matplotlib.pyplot as plt

import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib_backend import MatplotlibBackend


def _main():
    parser = argparse.ArgumentParser(description='draw the given CAD file and save it to a file or view it')
    parser.add_argument('cad_file', nargs='?')
    parser.add_argument('--supported_formats', action='store_true')
    parser.add_argument('--layout', default='Model')
    parser.add_argument('--out', required=False)
    parser.add_argument('--dpi', type=int, default=300)
    args = parser.parse_args()

    if args.supported_formats:
        fig = plt.figure()
        for extension, description in fig.canvas.get_supported_filetypes().items():
            print(f'{extension}: {description}')
        sys.exit()

    if args.cad_file is None:
        print('no CAD file specified')
        sys.exit(1)

    doc = ezdxf.readfile(args.cad_file)
    try:
        layout = doc.layouts.get(args.layout)
    except KeyError:
        print(f'could not find layout "{args.layout}". Valid layouts: {[l.name for l in doc.layouts]}')
        sys.exit(1)

    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(layout, finalize=True)
    if args.out is not None:
        print(f'saving to "{args.out}"')
        fig.savefig(args.out, dpi=args.dpi)
        plt.close(fig)
    else:
        plt.show()


if __name__ == '__main__':
    _main()

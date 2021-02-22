#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import os
import glob
import signal
import logging
from pathlib import Path

import ezdxf
from ezdxf import recover
from ezdxf.lldxf import const
from ezdxf.lldxf.validator import is_dxf_file
from ezdxf.tools import fonts

# Load and draw proxy graphic:
ezdxf.options.load_proxy_graphics = True
logger = logging.getLogger('ezdxf')


def audit(args):
    """ Launcher sub-command: audit """

    def build_outname(name: str) -> str:
        p = Path(name)
        return p.parent / (p.stem + ".rec.dxf")

    def log_fixes(auditor):
        for error in auditor.fixes:
            logger.info('fixed:' + error.message)

    def log_errors(auditor):
        for error in auditor.errors:
            logger.error(error.message)

    def _audit(filename: str) -> None:
        msg = f"auditing file: {filename}"
        print(msg)
        logger.info(msg)
        try:
            doc, auditor = recover.readfile(filename)
        except IOError:
            msg = 'Not a DXF file or a generic I/O error.'
            print(msg)
            logger.error(msg)
            sys.exit(1)
        except const.DXFStructureError:
            msg = 'Invalid or corrupted DXF file.'
            print(msg)
            logger.error(msg)
            sys.exit(2)

        if auditor.has_errors:
            auditor.print_error_report()
            log_errors(auditor)
        if auditor.has_fixes:
            auditor.print_fixed_errors()
            log_fixes(auditor)

        if auditor.has_errors is False and auditor.has_fixes is False:
            print('No errors found.')
        else:
            print(f'Found {len(auditor.errors)} errors, '
                  f'applied {len(auditor.fixes)} fixes')

        if args.save:
            outname = build_outname(filename)
            doc.saveas(outname)
            print(f"Saved recovered file as: {outname}")

    for pattern in args.files:
        names = list(glob.glob(pattern))
        if len(names) == 0:
            msg = f"File(s) '{pattern}' not found."
            print(msg)
            logger.error(msg)
            continue
        for filename in names:
            if not os.path.exists(filename):
                msg = f"File '{filename}' not found."
                print(msg)
                logger.error(msg)
                continue
            if not is_dxf_file(filename):
                msg = f"File '{filename}' is not a DXF file."
                print(msg)
                logger.error(msg)
                continue
            _audit(filename)


def load_document(filename: str):
    try:
        doc, auditor = recover.readfile(filename)
    except IOError:
        msg = f'Not a DXF file or a generic I/O error: {filename}'
        print(msg)
        logger.error(msg)
        sys.exit(2)
    except ezdxf.DXFStructureError:
        msg = f'Invalid or corrupted DXF file: {filename}'
        print(msg)
        logger.error(msg)
        sys.exit(3)

    if auditor.has_errors:
        # But is most likely good enough for rendering.
        msg = f'Found {len(auditor.errors)} unrecoverable errors.'
        print(msg)
        logger.error(msg)
    if auditor.has_fixes:
        msg = f'Fixed {len(auditor.fixes)} errors.'
        print(msg)
        logger.info(msg)
    return doc, auditor


def draw(args):
    # Import on demand for a quicker startup:
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    ezdxf.options.load_proxy_graphics = True
    # For the case automatic font loading is disabled:
    fonts.load()

    # Print all supported export formats:
    if args.formats:
        fig = plt.figure()
        for extension, description in fig.canvas.get_supported_filetypes().items():
            print(f'{extension}: {description}')
        sys.exit()

    if args.file:
        filename = args.file
    else:
        print(f'argument FILE is required')
        sys.exit()

    doc, _ = load_document(filename)
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax, params={'linetype_renderer': args.ltype})
    Frontend(ctx, out).draw_layout(doc.modelspace(), finalize=True)
    if args.out is not None:
        print(f'exporting to "{args.out}"')
        fig.savefig(args.out, dpi=args.dpi)
        plt.close(fig)
    else:
        plt.show()


def view(args):
    # Import on demand for a quicker startup:
    from PyQt5 import QtWidgets
    from ezdxf.addons.drawing.qtviewer import CadViewer

    ezdxf.options.load_proxy_graphics = True
    # For the case automatic font loading is disabled:
    fonts.load()

    signal.signal(signal.SIGINT, signal.SIG_DFL)  # handle Ctrl+C properly
    app = QtWidgets.QApplication(sys.argv)
    viewer = CadViewer(params={
        'linetype_renderer': args.ltype,
        'lineweight_scaling': args.lwscale,
    })
    filename = args.file
    if filename:
        doc, auditor = load_document(filename)
        viewer.set_document(doc, auditor)
        viewer.draw_layout('Model')
    sys.exit(app.exec_())

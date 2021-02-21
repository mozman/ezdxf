#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import os
import glob
import ezdxf
from ezdxf import recover
from ezdxf.lldxf import const
from ezdxf.lldxf.validator import is_dxf_file

# Load and draw proxy graphic:
ezdxf.options.load_proxy_graphics = True


def audit(args):
    """ Launcher sub-command: audit """

    def processing_msg(text: str) -> None:
        print(text)
        print('-' * len(text))

    def _audit(filename: str) -> None:
        try:
            doc, auditor = recover.readfile(filename)
        except IOError:
            print(f'Not a DXF file or a generic I/O error.')
            sys.exit(1)
        except const.DXFStructureError:
            print(f'Invalid or corrupted DXF file.')
            sys.exit(2)

        if auditor.has_errors:
            auditor.print_error_report()
        if auditor.has_fixes:
            auditor.print_fixed_errors()
        if auditor.has_errors is False and auditor.has_fixes is False:
            print('No errors found.')

    for pattern in args.files:
        names = list(glob.glob(pattern))
        if len(names) == 0:
            print(f"File(s) '{pattern}' not found.")
            continue
        for filename in names:
            if not os.path.exists(filename):
                print(f"File '{filename}' not found.")
                continue
            if not is_dxf_file(filename):
                print(f"File '{filename}' is not a DXF file.")
                continue
            processing_msg(filename)
            _audit(filename)


def load_document(filename: str):
    try:
        doc, auditor = recover.readfile(filename)
    except IOError:
        print(f'Not a DXF file or a generic I/O error: {filename}')
        sys.exit(2)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {filename}')
        sys.exit(3)

    if auditor.has_errors:
        # But is most likely good enough for rendering.
        print(f'Found {len(auditor.errors)} unrecoverable errors.')
    if auditor.has_fixes:
        print(f'Fixed {len(auditor.fixes)} errors.')
    return doc, auditor


def draw(args):
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.tools import fonts

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
    import signal
    from ezdxf.tools import fonts
    from PyQt5 import QtWidgets
    from ezdxf.addons.drawing.qtviewer import CadViewer

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

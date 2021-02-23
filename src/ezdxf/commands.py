#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Callable, Optional, Dict
import abc
import sys
import os
import glob
import signal
import logging
from pathlib import Path

from ezdxf import recover
from ezdxf.lldxf import const
from ezdxf.lldxf.validator import is_dxf_file

__all__ = ['get', 'add_parsers']

logger = logging.getLogger('ezdxf')


def get(cmd: str) -> Optional[Callable]:
    cls = _commands.get(cmd)
    if cls:
        return cls.run
    return None


def add_parsers(subparsers) -> None:
    for cmd in _commands.values():  # in order of registration
        cmd.add_parser(subparsers)


class Command:
    """ abstract base class for launcher commands """
    NAME = "command"

    @staticmethod
    @abc.abstractmethod
    def add_parser(subparsers) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def run(args) -> None:
        pass


_commands: Dict[str, Command] = dict()


def register(cls: Command):
    """ Register a launcher sub-command. """
    _commands[cls.NAME] = cls
    return cls


@register
class PrettyPrint(Command):
    """ Launcher sub-command: pp """
    NAME = 'pp'

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            PrettyPrint.NAME,
            help="pretty print DXF files as HTML file"
        )
        parser.add_argument(
            'files',
            metavar='FILE',
            nargs='+',
            help='DXF files pretty print',
        )
        parser.add_argument(
            '-o', '--open',
            action='store_true',
            help='open generated HTML file by the default web browser',
        )
        parser.add_argument(
            '-r', '--raw',
            action='store_true',
            help='raw mode, no DXF structure interpretation',
        )
        parser.add_argument(
            '-x', '--nocompile',
            action='store_true',
            help="don't compile points coordinates into single tags "
                 "(only in raw mode)",
        )
        parser.add_argument(
            '-l', '--legacy',
            action='store_true',
            help="legacy mode, reorder DXF point coordinates",
        )
        parser.add_argument(
            '-s', '--sections',
            action='store',
            default='hctbeo',
            help="choose sections to include and their order, h=HEADER, c=CLASSES, "
                 "t=TABLES, b=BLOCKS, e=ENTITIES, o=OBJECTS",
        )

    @staticmethod
    def run(args):
        from ezdxf.pp import run
        run(args)


@register
class Audit(Command):
    """ Launcher sub-command: audit """
    NAME = 'audit'

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            Audit.NAME,
            help="audit and repair DXF files"
        )
        parser.add_argument(
            'files',
            metavar='FILE',
            nargs='+',
            help='audit DXF files',
        )
        parser.add_argument(
            '-s', '--save',
            action='store_true',
            help="save recovered files with extension \".rec.dxf\" "
        )

    @staticmethod
    def run(args):
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
                return  # keep on processing additional files
            except const.DXFStructureError:
                msg = 'Invalid or corrupted DXF file.'
                print(msg)
                logger.error(msg)
                return  # keep on processing additional files

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
    except const.DXFStructureError:
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


@register
class Draw(Command):
    """ Launcher sub-command: draw """
    NAME = 'draw'

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            Draw.NAME,
            help="draw and convert DXF files by Matplotlib"
        )
        parser.add_argument(
            'file',
            metavar='FILE',
            nargs='?',
            help='DXF file to view or convert',
        )
        parser.add_argument(
            '--formats',
            action='store_true',
            help="show all supported export formats and exit"
        )
        parser.add_argument(
            '-o', '--out',
            required=False,
            help="output filename for export"
        )
        parser.add_argument(
            '--dpi',
            type=int,
            default=300,
            help="target render resolution, default is 300",
        )
        parser.add_argument(
            '--ltype',
            default='internal',
            choices=['internal', 'ezdxf'],
            help="select the line type rendering engine, default is internal",
        )

    @staticmethod
    def run(args):
        # Import on demand for a quicker startup:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print('Matplotlib package not found.')
            sys.exit(2)

        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

        # Print all supported export formats:
        if args.formats:
            fig = plt.figure()
            for extension, description in fig.canvas.get_supported_filetypes().items():
                print(f'{extension}: {description}')
            sys.exit(0)

        if args.file:
            filename = args.file
        else:
            print('argument FILE is required')
            sys.exit(1)

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


@register
class View(Command):
    """ Launcher sub-command: view """
    NAME = 'view'

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            View.NAME,
            help="view DXF files by the PyQt viewer"
        )
        parser.add_argument(
            'file',
            metavar='FILE',
            nargs='?',
            help='DXF file to view',
        )
        parser.add_argument(
            '--ltype',
            default='internal',
            choices=['internal', 'ezdxf'],
            help="select the line type rendering engine, default is internal",
        )
        # disable lineweight at all by default:
        parser.add_argument(
            '--lwscale',
            type=float,
            default=0,
            help="set custom line weight scaling, default is 0 to disable "
                 "line weights at all",
        )

    @staticmethod
    def run(args):
        # Import on demand for a quicker startup:
        try:
            from PyQt5 import QtWidgets
        except ImportError:
            print('PyQt5 package not found.')
            sys.exit(1)
        from ezdxf.addons.drawing.qtviewer import CadViewer

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

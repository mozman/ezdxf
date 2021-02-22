#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import argparse
from pathlib import Path
from ezdxf import __version__
from ezdxf.acc import USE_C_EXT

YES_NO = {True: 'yes', False: 'no'}


def add_common_arguments(parser):
    parser.add_argument(
        '-V', '--version',
        action='store_true',
        help="show version and exit",
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="give more output",
    )
    parser.add_argument(
        '--log',
        action='store',
        help="path to a verbose appending log",
    )


def add_pp_parser(subparser):
    parser = subparser.add_parser(
        "pp",
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
        help='open generated HTML file with the default web browser',
    )
    parser.add_argument(
        '-r', '--raw',
        action='store_true',
        help='raw mode - just print tags, no DXF structure interpretation',
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
        help="legacy mode - reorders DXF point coordinates",
    )
    parser.add_argument(
        '-s', '--sections',
        action='store',
        default='hctbeo',
        help="choose sections to include and their order, h=HEADER, c=CLASSES, "
             "t=TABLES, b=BLOCKS, e=ENTITIES, o=OBJECTS",
    )


def add_audit_parser(subparsers):
    parser = subparsers.add_parser(
        "audit",
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


def add_draw_parser(subparsers):
    parser = subparsers.add_parser(
        "draw",
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


def add_view_parser(subparsers):
    parser = subparsers.add_parser(
        "view",
        help="view DXF files by PyQt viewer"
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


def _print_config(func):
    from ezdxf import options
    func(f"ezdxf v{__version__} @ {Path(__file__).parent}")
    func(f"Python version: {sys.version}")
    func(f"using C-extensions: {YES_NO[USE_C_EXT]}")
    func(f"using Matplotlib: {YES_NO[options.use_matplotlib]}")


def print_version():
    _print_config(print)


def setup_log(args):
    import logging
    from datetime import datetime
    level = "DEBUG" if args.verbose else "INFO"
    logging.basicConfig(filename=args.log, level=level)
    print(f"Appending logs to file \"{args.log}\", logging level: {level}\n")
    logger = logging.getLogger('ezdxf')
    logger.info("***** Launch time: " + datetime.now().isoformat() + " *****")
    if args.verbose:
        _print_config(logger.info)


DESCRIPTION = """
This launcher is part of the ezdxf Python package (https://pypi.org/project/ezdxf/) 
and provides some tools to work with DXF files.

"""


def main():
    parser = argparse.ArgumentParser(
        "ezdxf",
        description=DESCRIPTION,
    )
    add_common_arguments(parser)
    subparsers = parser.add_subparsers(dest="command")
    add_pp_parser(subparsers)
    add_audit_parser(subparsers)
    add_draw_parser(subparsers)
    add_view_parser(subparsers)

    args = parser.parse_args(sys.argv[1:])
    if args.log:
        setup_log(args)
    if args.version:
        print_version()
    elif args.command == "pp":
        from ezdxf.pp import run
        run(args)
    elif args.command == "audit":
        from ezdxf.commands import audit
        audit(args)
    elif args.command == "draw":
        from ezdxf.commands import draw
        draw(args)
    elif args.command == "view":
        from ezdxf.commands import view
        view(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import argparse


def add_common_arguments(parser):
    pass


def add_pp_parser(subparser):
    parser = subparser.add_parser("pp", help="DXF pretty printer")
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
    parser = subparsers.add_parser("audit", help="Audit DXF files")
    parser.add_argument(
        'files',
        metavar='FILE',
        nargs='+',
        help='audit DXF files',
    )


def add_draw_parser(subparsers):
    parser = subparsers.add_parser("draw", help="Draw DXF files by Matplotlib")
    parser.add_argument(
        'file',
        metavar='FILE',
        nargs='?',
        help='DXF file to view or convert',
    )
    parser.add_argument(
        '--formats',
        action='store_true',
        help="show all supported export formats"
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
        '-t', '--ltype',
        default='internal',
        choices=['internal', 'ezdxf'],
        help="select the line type rendering engine, default is internal",
    )


def add_view_parser(subparsers):
    parser = subparsers.add_parser("view", help="View DXF files by PyQt viewer")
    parser.add_argument(
        'file',
        metavar='FILE',
        nargs='?',
        help='DXF file to view',
    )
    parser.add_argument(
        '-t', '--ltype',
        default='internal',
        choices=['internal', 'ezdxf'],
        help="select the line type rendering engine, default is internal",
    )
    # disable lineweight at all by default:
    parser.add_argument(
        '-s', '--lwscale',
        type=float,
        default=0,
        help="set custom line weight scaling, default is 0 to disable "
             "line weights at all",
    )


def main():
    parser = argparse.ArgumentParser("ezdxf")
    add_common_arguments(parser)
    subparsers = parser.add_subparsers(dest="command")
    add_pp_parser(subparsers)
    add_audit_parser(subparsers)
    add_draw_parser(subparsers)
    add_view_parser(subparsers)

    args = parser.parse_args(sys.argv[1:])

    if args.command == "pp":
        from ezdxf.pp.__main__ import run
        run(args)
    elif args.command == "audit":
        from .commands import audit
        audit(args)
    elif args.command == "draw":
        from .commands import draw
        draw(args)
    elif args.command == "view":
        from .commands import view
        view(args)


if __name__ == "__main__":
    main()

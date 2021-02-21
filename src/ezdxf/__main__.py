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
        'files',
        metavar='FILE',
        nargs='+',
        help='Draw DXF files by Matplotlib',
    )


def add_view_parser(subparsers):
    parser = subparsers.add_parser("view", help="View DXF files by PyQt viewer")
    parser.add_argument(
        'files',
        metavar='FILE',
        nargs='+',
        help='View DXF files by PyQt Viewer',
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
        print('draw')
    elif args.command == "view":
        print('view')


if __name__ == "__main__":
    main()

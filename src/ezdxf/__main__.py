#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import argparse

Parser = argparse.ArgumentParser


def add_common_arguments(parser: Parser):
    pass


def add_pp_arguments(parser: Parser):
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


def add_audit_arguments(parser: Parser):
    parser.add_argument(
        'files',
        metavar='FILE',
        nargs='+',
        help='audit DXF files',
    )
    pass


def main():
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)
    subparser = parser.add_subparsers(dest="command")
    pp_parser = subparser.add_parser("pp", help="DXF pretty printer")
    add_pp_arguments(pp_parser)
    audit_parser = subparser.add_parser("audit", help="Audit DXF files")
    add_audit_arguments(audit_parser)

    args = parser.parse_args(sys.argv[1:])

    if args.command == "pp":
        from ezdxf.pp.__main__ import run
        run(args)
    elif args.command == "audit":
        from ezdxf.audit.__main__ import run
        run(args)
    elif args.command == "draw":
        print('draw')
    elif args.command == "view":
        print('view')


if __name__ == "__main__":
    main()

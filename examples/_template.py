#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
#  Template for examples

import pathlib
import sys
import argparse
import ezdxf

DIR = pathlib.Path("~/Desktop/Outbox").expanduser()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        metavar="FILE",
        nargs=1,  # or "+"
        help="DXF input file",
    )
    parser.add_argument(  # positional argument
        "arg",
        metavar="ARG",
        type=int,
        nargs=1,
        help="help text",
    )
    parser.add_argument(
        "-o",
        "--option",
        action="store_true",
        help="help text",
    )
    return parser.parse_args()


def main(filename, arg, option):
    try:
        doc = ezdxf.readfile(filename)
    except (IOError, ezdxf.DXFStructureError):
        print(f"IOError or invalid DXF file: '{filename}'")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = parse_args()
        main(args.file[0], args.arg[0], args.option)
    else:
        pass  # predefined setup for IDE usage

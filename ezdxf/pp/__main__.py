# Purpose: DXF Pretty Printer
# Created: 16.07.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

import sys
import io
import argparse
from pathlib import Path

from .dxf2html import dxf2html, pp_raw_tags
from ezdxf import readfile, options
from ezdxf.lldxf.const import DXFError
from ezdxf.lldxf.tagger import low_level_tagger, tag_compiler
from ezdxf.lldxf.validator import is_dxf_file
from ezdxf.filemanagement import detect_encoding


def pretty_print(filename):
    try:
        dwg = readfile(str(filename), legacy_mode=True)
    except IOError:
        print("Unable to read DXF file '{}', or invalid DXF file.".format(filename))
        sys.exit()
    except DXFError as e:
        print(str(e))
        sys.exit()

    html_filename = filename.parent / (filename.stem + '.html')
    try:
        with io.open(html_filename, mode='wt', encoding='utf-8') as fp:
            fp.write(dxf2html(dwg))
    except IOError:
        print("IOError: can not write file '{}'.".format(html_filename))
    else:
        print("dxfpp created '{}'".format(html_filename))


def raw_pretty_print(filename, nocompile=True):
    try:
        encoding = detect_encoding(str(filename))
    except IOError:
        print("Unable to read DXF file '{}', or invalid DXF file.".format(filename))
        sys.exit()
    except DXFError as e:
        print(str(e))
        sys.exit()

    with io.open(filename, mode='rt', encoding=encoding, errors='ignore') as dxf:
        tagger = low_level_tagger(dxf)
        if nocompile is False:
            tagger = tag_compiler(tagger)
        html_filename = filename.parent / (filename.stem + '.html')
        try:
            with io.open(html_filename, mode='wt', encoding='utf-8') as html:
                html.write(pp_raw_tags(tagger, str(filename)))
        except IOError:
            print("IOError: can not write file '{}'.".format(html_filename))
        else:
            print("dxfpp created '{}'".format(html_filename))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'files',
        metavar='FILE',
        nargs='+',
        help='DXF files pretty print',
    )
    parser.add_argument(
        '-r', '--raw',
        action='store_true',
        help='raw mode',
    )
    parser.add_argument(
        '-x', '--nocompile',
        action='store_true',
        help="don't compile points coordinates into single tags (only in raw mode)",
    )
    parsed_args = parser.parse_args(sys.argv[1:])

    options.compress_binary_data = True
    for filename in parsed_args.files:
        if not Path(filename).exists():
            print("File '{}' not found.".format(filename))
            continue
        if not is_dxf_file(filename):
            print("File '{}' is not a DXF file.".format(filename))
            continue

        if parsed_args.raw:
            raw_pretty_print(Path(filename), parsed_args.nocompile)
        else:
            pretty_print(Path(filename))


if __name__ == "__main__":
    main()

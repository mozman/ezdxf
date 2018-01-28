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

from .dxfpp import dxfpp
from .rawpp import rawpp
from ezdxf import readfile, options
from ezdxf.lldxf.const import DXFError, DXFStructureError
from ezdxf.lldxf.tagger import low_level_tagger, tag_compiler
from ezdxf.lldxf.validator import is_dxf_file
from ezdxf.filemanagement import dxf_file_info
from ezdxf.lldxf.repair import tag_reorder_layer
import webbrowser


def pretty_print(filename):
    try:
        dwg = readfile(str(filename), legacy_mode=True)
    except IOError:
        print("Unable to read DXF file '{}'.".format(filename))
        sys.exit(1)
    except DXFError as e:
        print(str(e))
        sys.exit(2)

    html_filename = filename.parent / (filename.stem + '.html')
    try:
        with io.open(html_filename, mode='wt', encoding='utf-8') as fp:
            fp.write(dxfpp(dwg))
    except IOError:
        print("IOError: can not write file '{}'.".format(html_filename))
    return html_filename


def raw_pretty_print(filename, nocompile=True, legacy_mode=False):
    try:
        info = dxf_file_info(str(filename))
    except IOError:
        print("Unable to read DXF file '{}'.".format(filename))
        sys.exit(1)
    except DXFError as e:
        print(str(e))
        sys.exit(2)

    with io.open(filename, mode='rt', encoding=info.encoding, errors='ignore') as dxf:
        tagger = low_level_tagger(dxf)
        if legacy_mode:
            tagger = tag_reorder_layer(tagger)
        if nocompile is False:
            tagger = tag_compiler(tagger)
        html_filename = filename.parent / (filename.stem + '.html')
        try:
            with io.open(html_filename, mode='wt', encoding='utf-8') as html:
                html.write(rawpp(tagger, str(filename)))
        except IOError:
            print("IOError: can not write file '{}'.".format(html_filename))
        except DXFStructureError as e:
            print("DXFStructureError: {}".format(str(e)))
    return html_filename


def main():
    parser = argparse.ArgumentParser()
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
        help="don't compile points coordinates into single tags (only in raw mode)",
    )
    parser.add_argument(
        '-l', '--legacy',
        action='store_true',
        help="legacy mode - reorders DXF point coordinates",
    )
    args = parser.parse_args(sys.argv[1:])

    options.compress_binary_data = True
    for filename in args.files:
        if not Path(filename).exists():
            print("File '{}' not found.".format(filename))
            continue
        if not is_dxf_file(filename):
            print("File '{}' is not a DXF file.".format(filename))
            continue

        if args.raw:
            html_path = raw_pretty_print(Path(filename), args.nocompile, args.legacy)
        else:
            html_path = pretty_print(Path(filename))  # legacy mode is always used

        print("dxfpp created '{}'".format(html_path))
        if args.open:
            webbrowser.open(html_path)


if __name__ == "__main__":
    main()

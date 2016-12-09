# Purpose: DXF Pretty Printer
# Created: 16.07.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

import sys
import os
import io

from .dxf2html import dxf2html
from ezdxf import readfile, options

if __name__ == "__main__":
    options.compress_binary_data = True
    try:
        filename = sys.argv[1]
    except IndexError:
        print("DXF pretty printer (pp) requires exact one filename of a DXF file.")
        sys.exit()
    try:
        dwg = readfile(filename)
    except IOError:
        print("Unable to read DXF file '{}', or invalid DXF file.".format(filename))
        sys.exit()
    html_filename = os.path.splitext(dwg.filename)[0] + '.html'
    try:
        with io.open(html_filename, mode='wt', encoding='utf-8') as fp:
            fp.write(dxf2html(dwg))
    except IOError:
        print("IOError: can not write file '{}'.".format(html_filename))

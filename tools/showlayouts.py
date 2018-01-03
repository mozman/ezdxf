#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: analyze layouts
# Created: 26.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

import sys

import ezdxf


def main(filename):
    dwg = ezdxf.readfile(filename)
    if dwg.dxfversion < 'AC1015':
        print('DXF Version >= AC1015 required')
        sys.exit()

    rootdict = dwg.rootdict
    db = dwg.entitydb
    layouts = dwg.dxffactory.wrap_handle(rootdict['ACAD_LAYOUT'])
    print(list(layouts.keys()))


if __name__ == '__main__':
    main(sys.argv[1])

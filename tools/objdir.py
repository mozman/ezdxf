#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: print object directory
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

import sys

import ezdxf


def main(filename):
    dwg = ezdxf.readfile(filename)
    with open('objects.txt', 'wt') as outstream:
        dumpobjects(outstream, dwg.objects)


def dumpobjects(stream, objects):
    for entity in sorted(objects, key=lambda e: int(e.dxf.handle, 16)):
        stream.write("handle: {:6s} name: {}\n".format(entity.dxf.handle, entity.dxftype()))


if __name__ == '__main__':
    main(sys.argv[1])

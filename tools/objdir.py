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
        dumpobjects(outstream, dwg.entitydb, dwg.sections.objects)


def dumpobjects(stream, database, objects):
    def printobj(tags):
        name = tags[0].value
        handle = tags.gethandle()
        stream.write("handle: %6s name: %s\n" % (handle, name))

    handles = ((int(handle, 16), handle) for handle in objects.iterhandles())
    for key, handle in sorted(handles):
        tags = database[handle]
        printobj(tags)

if __name__ == '__main__':
    main(sys.argv[1])
#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dump entity database
# Created: 14.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

import sys
import os
import ezdxf

def main(filename):
    ezdxf.options['DEBUG'] = True
    drawing = ezdxf.readfile(filename)
    folder = os.path.dirname(filename)
    dbcontent = os.path.join(folder, 'dbcontent.txt')
    print('writing content to: %s' % dbcontent)
    with open(dbcontent, 'wt') as stream:
        drawing.entitydb.dumpcontent(stream, verbose=False)
    dbcollisions = os.path.join(folder, 'dbcollisions.txt')
    print('writing collisions to: %s' % dbcollisions)
    with open(dbcollisions, 'wt') as stream:
        drawing.entitydb.dumpcollisions(stream)

if __name__=='__main__':
    main(sys.argv[1])
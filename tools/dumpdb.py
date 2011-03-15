#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dump entity database
# Created: 14.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import ezdxf

def main(filename):
    ezdxf.options['DEBUG'] = True
    drawing = ezdxf.readfile(filename)
    print('writing content to dbcontent.txt')
    with open('dbcontent.txt', 'wt', encoding='utf8') as stream:
        drawing.entitydb.dumpcontent(stream, verbose=False)
    print('writing collisions to dbcollisions.txt')
    with open('dbcollisions.txt', 'wt') as stream:
        drawing.entitydb.dumpcollisions(stream)

if __name__=='__main__':
    main(sys.argv[1])
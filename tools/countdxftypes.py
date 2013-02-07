#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: count dxftypes
# Created: 28.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from operator import itemgetter as _itemgetter

import sys
import ezdxf

from collections import Counter

def count_elements(db):
    counter = Counter()
    for tags in db.values():
        counter[tags[0].value] += 1
    return counter
def print_result(counter):
    sum_ = 0

    for key, count in sorted(counter.items(), key=_itemgetter(1), reverse=True):
        sum_ += count
        print("{1:6d}x DXFType: {0}".format(key, count))
    print("Overall sum: {0}".format(sum_))

def main(filename):
    print('reading file ...')
    dwg = ezdxf.readfile(filename)
    print('counting elements ...')
    result = count_elements(dwg.entitydb)
    print_result(result)

if __name__=="__main__":
    main(sys.argv[1])
#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test copy dxf file
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: MIT License

import sys
import io
import time

from ezdxf import readfile

def copydxf(fromfile, tofile):
    starttime = time.time()
    dwg = readfile(fromfile)
    dwg.saveas(tofile)
    endtime = time.time()
    print('copy time: %.2f seconds' % (endtime-starttime) )

if __name__=='__main__':
    copydxf(sys.argv[1], sys.argv[2])
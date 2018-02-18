# Purpose: test copy dxf file
# Created: 12.03.2011
# Copyright (c) , Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import sys
import time
import ezdxf


def copydxf(fromfile, tofile):
    starttime = time.time()
    dwg = ezdxf.readfile(fromfile)
    dwg.saveas(tofile)
    endtime = time.time()
    print('copy time: %.2f seconds' % (endtime-starttime))


if __name__=='__main__':
    copydxf(sys.argv[1], sys.argv[2])
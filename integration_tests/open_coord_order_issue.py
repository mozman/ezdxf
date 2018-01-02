#!/usr/bin/env python3
# Author:  mozman -- <mozman@gmx.at>
# Purpose: open DXF file with coordinate tags in unusual order
# Created: 02.01.2017
# Copyright (C) 2017, Manfred Moitzi
# License: MIT License
import os
import ezdxf
FILE = 'AC1003_LINE_Example.dxf'

if not os.path.exists(FILE):
    print("{} not found, test skipped.".format(__file__))
    exit(1)

dwg = ezdxf.readfile(FILE, legacy_mode=True)
msp = dwg.modelspace()
lines = msp.query('LINE')
print('Reading LINE coordinates in unusual order: ')
if lines[0].dxf.start == (1.5, 0, 0):
    print('ok')
else:
    print('ERROR: invalid coordinates')

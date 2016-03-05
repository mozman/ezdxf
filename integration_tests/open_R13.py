#!/usr/bin/env python3
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: open a DXF R13 file without plot style name structure setup
# Created: 05.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License

import ezdxf

FILENAME = "small_r13.dxf"


def main():
    dwg = ezdxf.readfile(FILENAME)
    if 'Model' in dwg.layouts:
        print('Model space found.')
    else:
        print('Model space NOT found.')

    if 'Layout1' in dwg.layouts:
        print('Paper space found.')
    else:
        print('Paper space NOT found.')

    msp = dwg.modelspace()
    msp.add_line((0, 0), (10, 3))

    dwg.saveas("small_r13_converted_AC1015.dxf")


if __name__ == '__main__':
    main()

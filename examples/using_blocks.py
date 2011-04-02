#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: block example
# Created: 02.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys

import ezdxf

def main():
    dwg = ezdxf.new('AC1009')

    # block creation
    block = dwg.blocks.new('TEST')
    block.add_line((-1, -1), (+1, +1))
    block.add_line((-1, +1), (+1, -1))

    # block usage
    ms = dwg.modelspace()
    ms.add_blockref('TEST', (5, 5))
    dwg.saveas('using_blocks.dxf')


if __name__=='__main__':
    main()
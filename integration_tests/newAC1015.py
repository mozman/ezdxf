#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: create new AC1009 Drawing
# Created: 20.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import ezdxf

def main():
    dwg = ezdxf.new('AC1015')
    dwg.layers.create('ADDING_A_NEW_LAYER')
    dwg.saveas('testAC1015.dxf')

if __name__=='__main__':
    main()

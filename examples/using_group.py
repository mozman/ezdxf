#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: using DXF groups
# Created: 15.07.2015
# Copyright (C) , Manfred Moitzi
# License: MIT License

import ezdxf


dwg = ezdxf.readfile('group.dxf')
for name, group in dwg.get_dxf_groups():
    print("GROUP: {}\n".format(name))
    for entity in group:
        print("  Entity: {}".format(entity.dxftype()))

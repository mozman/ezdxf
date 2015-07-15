#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: using DXF groups
# Created: 15.07.2015
# Copyright (C) , Manfred Moitzi
# License: MIT License

import ezdxf


def reading_groups():
    dwg = ezdxf.readfile('group.dxf')
    # GROUP resides in the OBJECTS section
    all_groups = dwg.objects.query("GROUP")
    count = 1
    for group in all_groups:
        print("GROUP: {}\n".format(count))
        for entity in group:
            print("  Entity: {}".format(entity.dxftype()))
        count += 1

reading_groups()

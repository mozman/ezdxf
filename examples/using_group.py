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
    for group in all_groups:
        print("GROUP: {}\n".format(group.get_name()))
        for entity in group:
            print("  Entity: {}".format(entity.dxftype()))

reading_groups()

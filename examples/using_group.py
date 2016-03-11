#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: using DXF groups
# Created: 15.07.2015
# Copyright (C) , Manfred Moitzi
# License: MIT License

import ezdxf


def create_group():
    dwg = ezdxf.new('Ac1015')
    msp = dwg.modelspace()
    # create a new unnamed group, in reality they have a name like '*Annnn' and group names have to be unique
    group = dwg.groups.new()
    # group management is implemented as context manager, returning a standard Python list
    with group.edit_data() as g:
        # the group itself is not an entity space, DXF entities has to be placed in model space, paper space
        # or in a block
        g.append(msp.add_line((0, 0), (3, 0)))
        g.append(msp.add_circle((0, 0), radius=2))
    dwg.saveas('group.dxf')


def read_group():
    dwg = ezdxf.readfile('group.dxf')
    for name, group in dwg.groups:
        print("GROUP: {}\n".format(name))
        for entity in group:
            print("  ENTITY: {}".format(entity.dxftype()))

create_group()
read_group()

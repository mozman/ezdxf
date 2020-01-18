# Purpose: using DXF groups
# Created: 15.07.2015
# Copyright (c) 2015 Manfred Moitzi
# License: MIT License
import ezdxf


def create_group():
    doc = ezdxf.new('R2000')
    msp = doc.modelspace()
    # create a new unnamed group, in reality they have a name like '*Annnn' and group names have to be unique
    group = doc.groups.new()
    # group management is implemented as context manager, returning a standard Python list
    with group.edit_data() as g:
        # the group itself is not an entity space, DXF entities has to be placed in model space, paper space
        # or in a block
        g.append(msp.add_line((0, 0), (3, 0)))
        g.append(msp.add_circle((0, 0), radius=2))
    doc.saveas('group.dxf')


def read_group():
    doc = ezdxf.readfile('group.dxf')
    for name, group in doc.groups:
        print(f"GROUP: {name}\n")
        for entity in group:
            print(f"  ENTITY: {entity.dxftype()}")


create_group()
read_group()

#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: 'flag' example
# Created: 04.11.2010
# Copyright (C) 2010, 2011 Manfred Moitzi
# License: MIT License

import sys
import os
import random

import ezdxf

def get_random_point():
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return (x, y)

sample_coords = [get_random_point() for x in range(50)]

flag_symbol = [(0,0), (0, 5), (4, 3), (0, 3)]


dwg = ezdxf.new('ac1009')
dwg.layers.create('FLAGS')

# first create a block
flag = dwg.blocks.new(name='FLAG')

# add dxf entities to the block (the flag)
# use basepoint = (x, y) to define an other basepoint than (0, 0)
flag.add_polyline2d(flag_symbol)
flag.add_circle((0, 0), .4, dxfattribs={'color': 2})

# define some attributes
flag.add_attdef('NAME', (0.5, -0.5), {'height':0.5, 'color':3})
flag.add_attdef('XPOS', (0.5, -1.0), {'height':0.25, 'color':4})
flag.add_attdef('YPOS', (0.5, -1.5), {'height':0.25, 'color':4})
modelspace = dwg.modelspace()
for number, point in enumerate(sample_coords):
    values = {
        'NAME': "P(%d)" % (number+1),
        'XPOS': "x = %.3f" % point[0],
        'YPOS': "y = %.3f" % point[1]
    }
    randomscale = 0.5 + random.random() * 2.0
    modelspace.add_autoblockref('FLAG', point, values, dxfattribs={
        'xscale': randomscale,
        'yscale': randomscale,
        'layer': 'FLAGS',
        'rotation':-15
    })

filename = 'flags.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)

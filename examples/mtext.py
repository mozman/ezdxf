#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: 'mtext' example
# Created: 11.08.2013
# Copyright (C) 2013 Manfred Moitzi
# License: MIT License

import ezdxf

dwg = ezdxf.new('ac1015')
modelspace = dwg.modelspace()
attribs = {
    'char_height': 0.7,
    'width': 5.0,
}
modelspace.add_mtext("This is a long MTEXT line with line wrapping!", attribs)

filename = 'mtext.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)

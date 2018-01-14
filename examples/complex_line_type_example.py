#!/usr/bin/env python
# Author:  mozman
# Purpose: example for complex line types
# Created: 13.01.2018
# Copyright (C) 2018 Manfred Moitzi
# License: MIT License


import ezdxf

FILENAME = r'C:\Users\manfred\Desktop\Outbox\complex_linetype_example.dxf'

dwg = ezdxf.new('R2018')  # DXF R13 or later is required

ltype_string = dwg.linetypes.new('GASLEITUNG2', dxfattribs={
    'description': 'Gasleitung2 ----GAS----GAS----GAS----GAS----GAS----GAS--',
    'length': 1,  # required for complex line types
    # line type definition in acadlt.lin:
    'pattern': 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
})

# shapes only work if the ltypeshp.shx and the DXF file are in the same directory
ltype_shape = dwg.linetypes.new('GRENZE2', dxfattribs={
    'description': 'Grenze eckig ----[]-----[]----[]-----[]----[]--',
    'length': 1.45,  # required for complex line types
    # line type definition in acadlt.lin:
    # A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1
    # replacing BOX by shape index 132 (got index from an AutoCAD file), ezdxf can't get shape index from ltypeshp.shx
    'pattern': 'A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1',
})


msp = dwg.modelspace()
msp.add_line((0, 0), (100, 0), dxfattribs={'linetype': 'GASLEITUNG2'})
msp.add_line((0, 50), (100, 50), dxfattribs={'linetype': 'GRENZE2'})

dwg.saveas(FILENAME)

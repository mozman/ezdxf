#!/usr/bin/env python
# Author:  mozman
# Purpose: example for complex line types
# Created: 13.01.2018
# Copyright (C) 2018 Manfred Moitzi
# License: MIT License


import ezdxf

dwg = ezdxf.new('R2018')  # DXF R13 or later is required

ltype_string = dwg.linetypes.new('GASLEITUNG2', dxfattribs={
    'description': 'Gasleitung2 ----GAS----GAS----GAS----GAS----GAS----GAS--',
})

ltype_string.setup_complex_line_type(
    length=1.,
    definition='A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',  # line type definition copied from acadlt.lin
)

ltype_shape = dwg.linetypes.new('GRENZE2', dxfattribs={
    'description': 'Grenze eckig ----[]-----[]----[]-----[]----[]--',
})

# shapes only work if the ltypeshp.shx and the DXF file are in the same directory
ltype_shape.setup_complex_line_type(
    length=3.0,  # for the total length I have to guess
    definition='A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1',  # line type definition copied from acadlt.lin
    shapes_table={'BOX': 132},  # shape number taken from an AutoCAD file
)

msp = dwg.modelspace()
msp.add_line((0, 0), (100, 0), dxfattribs={'linetype': 'GASLEITUNG2'})
msp.add_line((0, 50), (100, 50), dxfattribs={'linetype': 'GRENZE2'})

dwg.saveas('complex_linetype_example.dxf')

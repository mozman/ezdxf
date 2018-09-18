# Purpose: examples for add-on table usage
# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.addons import Table


def get_mat_symbol(dwg):
    symbol = dwg.blocks.new('matsymbol')
    p1 = 0.5
    p2 = 0.25
    points = [(p1, p2), (p2, p1), (-p2, p1), (-p1, p2), (-p1, -p2),
              (-p2, -p1), (p2, -p1), (p1, -p2)]

    # should run with DXF R12, so not symbol.add_lwpolyline()
    symbol.add_polyline2d(points, dxfattribs={
        'color': 2,
        'closed': True,
    })

    symbol.add_attdef(tag='num', text='0', dxfattribs={
        'height': 0.7,
        'color': 1,
    }).set_align('MIDDLE_CENTER')
    return symbol


name = 'table.dxf'
dwg = ezdxf.new('R12')
msp = dwg.modelspace()

table = Table(insert=(0, 0), nrows=20, ncols=10)
# create a new styles
ctext = table.new_cell_style(
    name='ctext',
    textcolor=7,
    textheight=0.5,
    align='MIDDLE_CENTER',
)
# halign = const.CENTER is still supported
# valign = const.MIDDLE is still supported

# modify border settings
border = table.new_border_style(color=6, linetype='DOT', priority=51)
ctext.set_border_style(border, right=False)

table.new_cell_style(
    name='vtext',
    textcolor=3,
    textheight=0.3,
    align='MIDDLE_CENTER',  # halign and valign still supported
    rotation=90,  # vertical written
    bgcolor=8,
)
# set column width, first column has index 0
table.set_col_width(1, 7)

# set row height, first row has index 0
table.set_row_height(1, 7)

# create a text cell with the default style
cell1 = table.text_cell(0, 0, 'Zeile1\nZeile2', style='ctext')

# cell spans over 2 rows and 2 cols
cell1.span = (2, 2)

cell2 = table.text_cell(4, 0, 'VERTICAL\nTEXT', style='vtext', span=(4, 1))

# create frames
table.frame(0, 0, 10, 2, 'framestyle')

# because style is defined by a namestring
# style can be defined later
hborder = table.new_border_style(color=4)
vborder = table.new_border_style(color=17)
table.new_cell_style(
    name='framestyle',
    left=hborder,
    right=hborder,
    top=vborder,
    bottom=vborder,
)
mat_symbol = get_mat_symbol(dwg)

table.new_cell_style(
    name='matsym',
    align='MIDDLE_CENTER',
    xscale=0.6,
    yscale=0.6,
)

# 1. table rendering
# render table to a layout: can be the model space, a paper space or a block definition.
table.render(msp, insert=(40, 20))
# additional changes don't affect the first rendering

# if you want different tables, in ezdxf you don't have to deepcopy the table
table.new_cell_style(
    name='57deg',
    textcolor=2,
    textheight=0.5,
    rotation=57,
    align='MIDDLE_CENTER',
    bgcolor=123,
)

table.text_cell(6, 3, "line one\nline two\nand line three", span=(3, 3), style='57deg')

# 2. table rendering
# create anonymous block
block = dwg.blocks.new_anonymous_block()
# render table into block at 0, 0
table.render(block, insert=(0, 0))
# add block reference into model space at 80, 20
msp.add_blockref(block.name, insert=(80, 20))


# a stacked text: Letters are stacked top-to-bottom, but not rotated
table.new_cell_style(
    name='stacked',
    textcolor=6,
    textheight=0.25,
    align='MIDDLE_CENTER',
    stacked=True,
)
table.text_cell(6, 3, "STACKED FIELD", span=(7, 1), style='stacked')

for pos in [3, 4, 5, 6]:
    blockcell = table.block_cell(pos, 1, mat_symbol, attribs={'num': pos}, style='matsym')

# 3. table rendering
# render table to a layout: can be the model space, a paper space or a block definition.
table.render(msp, insert=(0, 0))
dwg.saveas(name)
print("drawing '%s' created.\n" % name)

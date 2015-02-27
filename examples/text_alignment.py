#!/usr/bin/env python3
# encoding: utf-8
# Purpose: 
# Created: 14.07.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import ezdxf


def create_dwg(filename):
    def add_justify_text(content, p1, p2, align):
        msp.add_text(content).set_pos(p1, p2, align)
        msp.add_line(p1, p2)

    def add_grid(pos, width, height):
        attribs = {'height': 0.2, 'color': 3}
        x, y = pos
        dx = width / 2
        dy = height / 2
        msp.add_line((x, y), (x, y+height))
        msp.add_line((x+dx, y), (x+dx, y+height))
        msp.add_line((x+width, y), (x+width, y+height))

        msp.add_line((x, y-1), (x+width, y-1))
        msp.add_text('BASELINE ADJUSTMENTS', dxfattribs=attribs).set_pos((x, y-1.5))
        msp.add_text('LEFT', dxfattribs=attribs).set_pos((x, y-1), align='LEFT')
        msp.add_text('CENTER', dxfattribs=attribs).set_pos((x+dx, y-1), align='CENTER')
        msp.add_text('RIGHT', dxfattribs=attribs).set_pos((x+width, y-1), align='RIGHT')

        attribs['color'] = 2
        msp.add_line((x, y), (x+width, y))
        msp.add_text('BOTTOM_LEFT', dxfattribs=attribs).set_pos((x, y), align='BOTTOM_LEFT')
        msp.add_text('BOTTOM_CENTER', dxfattribs=attribs).set_pos((x+dx, y), align='BOTTOM_CENTER')
        msp.add_text('BOTTOM_RIGHT', dxfattribs=attribs).set_pos((x+width, y), align='BOTTOM_RIGHT')

        y += dy

        msp.add_line((x, y), (x+width, y))
        msp.add_text('MIDDLE_LEFT', dxfattribs=attribs).set_pos((x, y), align='MIDDLE_LEFT')
        msp.add_text('MIDDLE_CENTER', dxfattribs=attribs).set_pos((x+dx, y), align='MIDDLE_CENTER')
        msp.add_text('MIDDLE_RIGHT', dxfattribs=attribs).set_pos((x+width, y), align='MIDDLE_RIGHT')

        y += dy

        msp.add_line((x, y), (x+width, y))
        msp.add_text('TOP_LEFT', dxfattribs=attribs).set_pos((x, y), align='TOP_LEFT')
        msp.add_text('TOP_CENTER', dxfattribs=attribs).set_pos((x+dx, y), align='TOP_CENTER')
        msp.add_text('TOP_RIGHT', dxfattribs=attribs).set_pos((x+width, y), align='TOP_RIGHT')

    dwg = ezdxf.new(dxfversion='AC1018') # AutoCAD R2004
    msp = dwg.modelspace()
    add_justify_text("ALIGNED-TEXT", (15,0), (35, 5), 'ALIGNED')
    add_justify_text("FITTED-TEXT", (15,10), (35, 5), 'FIT')
    add_grid((0, 0), width=10, height=10)

    dwg.saveas(filename)

if __name__ == '__main__':
    create_dwg("text_alignment.dxf")
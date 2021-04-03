# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from typing import Dict, TYPE_CHECKING
import math
import ezdxf
from ezdxf.math import Vec3, Matrix44, X_AXIS, linspace
from ezdxf import zoom

if TYPE_CHECKING:
    from ezdxf.eztypes import BlockLayout, Drawing, BaseLayout

BLK_CONTENT = "BLK_CONTENT"
BLK_REF_LEVEL_0 = "BLK_REF_LEVEL_0"
BLK_REF_LEVEL_1 = "BLK_REF_LEVEL_1"
ATTRIBS = 'ATTRIBS'


def create_doc(filename, content_creator):
    doc = ezdxf.new(dxfversion='R2004')
    doc.layers.new(BLK_CONTENT)
    doc.layers.new(BLK_REF_LEVEL_0)
    doc.layers.new(BLK_REF_LEVEL_1)
    doc.styles.new(ATTRIBS, dxfattribs={
        'font': 'OpenSansCondensed-Light.ttf'
    })
    content_creator(doc)
    zoom.extents(doc.modelspace())
    doc.saveas(filename)


def create_base_block(block: 'BlockLayout', arrow_length=4):
    def add_axis(attribs: Dict, m: Matrix44 = None):
        start = -X_AXIS * arrow_length / 2
        end = X_AXIS * arrow_length / 2
        leg1 = Vec3.from_deg_angle(180 - leg_angle) * leg_length
        leg2 = Vec3.from_deg_angle(180 + leg_angle) * leg_length

        lines = [
            block.add_line(start, end, dxfattribs=attribs),
            block.add_line(end, end + leg1, dxfattribs=attribs),
            block.add_line(end, end + leg2, dxfattribs=attribs),
        ]
        if m is not None:
            for line in lines:
                line.transform(m)

    leg_length = arrow_length / 10
    leg_angle = 15
    deg_90 = math.radians(90)
    # red x-axis
    add_axis(attribs={'color': 1, 'layer': BLK_CONTENT})
    # green y-axis
    add_axis(attribs={'color': 3, 'layer': BLK_CONTENT},
             m=Matrix44.z_rotate(deg_90))
    # blue z-axis
    add_axis(attribs={'color': 5, 'layer': BLK_CONTENT},
             m=Matrix44.y_rotate(-deg_90))
    x = -arrow_length * 0.45
    y = arrow_length / 20
    line_spacing = 1.50
    height = arrow_length / 20
    block.add_attdef('ROTATION', (x, y), dxfattribs={
        'style': ATTRIBS, 'height': height})
    y += height * line_spacing
    block.add_attdef('SCALE', (x, y), dxfattribs={
        'style': ATTRIBS, 'height': height})
    y += height * line_spacing
    block.add_attdef('EXTRUSION', (x, y), dxfattribs={
        'style': ATTRIBS, 'height': height})


def show_config(blk_ref):
    dxf = blk_ref.dxf
    blk_ref.add_auto_attribs({
        'ROTATION': f"Rotation: {dxf.rotation:.2f} deg",
        'SCALE': f"Scale: x={dxf.xscale}  y={dxf.yscale}  z={dxf.zscale}",
        'EXTRUSION': f"Extrusion: {str(dxf.extrusion.round(3))}",
    })


def create_l0_block_references(layout: 'BaseLayout'):
    y = 0
    grid_x = 4.5
    grid_y = 4.5
    for sx, sy, sz in [(1, 1, 1), (-1, 1, 1), (1, -1, 1), (1, 1, -1)]:
        for index, angle in enumerate(linspace(0, 270, 10)):
            x = index * grid_x
            blk_ref = layout.add_blockref("BASE", (x, y), dxfattribs={
                'layer': BLK_REF_LEVEL_0,
                'rotation': angle,
                'xscale': sx,
                'yscale': sy,
                'zscale': sz,
            })
            show_config(blk_ref)
        y += grid_y


def create_l1_block_references(layout: 'BaseLayout'):
    pass


def nesting_depth_0(doc: 'Drawing'):
    blk = doc.blocks.new("BASE")
    create_base_block(blk)
    msp = doc.modelspace()
    create_l0_block_references(msp)


def nesting_depth_1(doc: 'Drawing'):
    blk = doc.blocks.new("BASE")
    create_base_block(blk)
    blk0 = doc.blocks.new("LEVEL0")
    create_l0_block_references(blk0)
    msp = doc.modelspace()
    create_l1_block_references(msp)


if __name__ == '__main__':
    create_doc("insert_depth_0.dxf", nesting_depth_0)
    # create_doc("insert_depth_1.dxf", nesting_depth_1)

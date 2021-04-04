# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from typing import Dict, TYPE_CHECKING, cast
import math
import ezdxf
from ezdxf.math import Vec3, Matrix44, X_AXIS, linspace, OCS
from ezdxf import zoom, disassemble
from ezdxf.entities import copy_attrib_as_text

if TYPE_CHECKING:
    from ezdxf.eztypes import BlockLayout, Drawing, BaseLayout

# Check if a viewer/ezdxf does correct block reference (INSERT) transformations.
# If the viewer/ezdxf works correct only the exploded arrows are visible a
# after loading. (The magenta colored content)
# Turn of the "EXPLODE" layer to see the original block references.
EXPLODE_CONTENT = True

BLK_CONTENT = "BLK_CONTENT"
BLK_REF_LEVEL_0 = "BLK_REF_LEVEL_0"
BLK_REF_LEVEL_1 = "BLK_REF_LEVEL_1"
EXPLODE = 'EXPLODE'
LAYERS = [
    BLK_CONTENT, BLK_REF_LEVEL_0, BLK_REF_LEVEL_1, EXPLODE
]
ATTRIBS = 'ATTRIBS'


def explode(layout: 'BaseLayout'):
    if EXPLODE_CONTENT:
        entities = list(disassemble.recursive_decompose(layout))
        for e in entities:
            if e.dxftype() in ('ATTRIB', 'ATTDEF'):
                e = copy_attrib_as_text(cast('BaseAttrib', e))
            e = cast('DXFGraphic', e)
            e.dxf.layer = EXPLODE
            e.dxf.color = 6
            layout.add_entity(e)


def create_doc(filename, content_creator):
    doc = ezdxf.new(dxfversion='R2004')
    for name in LAYERS:
        doc.layers.new(name)
    doc.styles.new(ATTRIBS, dxfattribs={
        'font': 'OpenSansCondensed-Light.ttf'
    })
    content_creator(doc)
    explode(doc.modelspace())
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


def create_block_references(
        layout: 'BaseLayout', block_name: str, layer: str = "LAYER",
        grid=(10, 10),
        extrusions=((0, 0, 1), (0, 0, -1)),
        scales=((1, 1, 1), (-1, 1, 1), (1, -1, 1), (1, 1, -1)),
        angles=(0, 45, 90, 135, 180, 225, 270, 315),
):
    y = 0
    grid_x, grid_y = grid
    for extrusion in extrusions:
        ocs = OCS(extrusion)
        for sx, sy, sz in scales:
            for index, angle in enumerate(angles):
                x = index * grid_x
                insert = ocs.from_wcs((x, y))
                blk_ref = layout.add_blockref(block_name, insert, dxfattribs={
                    'layer': layer,
                    'rotation': angle,
                    'xscale': sx,
                    'yscale': sy,
                    'zscale': sz,
                    'extrusion': extrusion,
                })
                show_config(blk_ref)
            y += grid_y


def create_l0_block_references(layout: 'BaseLayout', block_name: str):
    create_block_references(
        layout, block_name,
        layer=BLK_REF_LEVEL_0,
        grid=(4.5, 4.5),
        extrusions=((0, 0, 1), (0, 0, -1)),
        scales=((1, 1, 1), (-1, 1, 1), (1, -1, 1), (1, 1, -1)),
        angles=(0, 45, 90, 135, 180, 225, 270, 315),
    )


def create_l1_block_references(layout: 'BaseLayout', block_name: str):
    create_block_references(
        layout, block_name,
        layer=BLK_REF_LEVEL_1,
        grid=(100, 100),
        extrusions=((0, 0, 1),),
        scales=((1, 1, 1), (-1, 1, 1), (1, -1, 1)),
        angles=(0, 90, 180),
    )


def nesting_level_0(doc: 'Drawing'):
    blk = doc.blocks.new("BASE")
    create_base_block(blk)
    msp = doc.modelspace()
    create_l0_block_references(msp, "BASE")


def nesting_level_1(doc: 'Drawing'):
    blk = doc.blocks.new("BASE")
    create_base_block(blk)
    blk0 = doc.blocks.new("LEVEL0")
    create_l0_block_references(blk0, "BASE")

    msp = doc.modelspace()
    create_l1_block_references(msp, "LEVEL0")


if __name__ == '__main__':
    create_doc("insert_nesting_level_0.dxf", nesting_level_0)
    create_doc("insert_nesting_level_1.dxf", nesting_level_1)

# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import ezdxf

SIZE = 5

doc = ezdxf.new()

msp = doc.modelspace()
msp.add_polyline2d([(0, 0), (SIZE, 0), (SIZE, SIZE), (0, SIZE)], dxfattribs={'closed': True})
msp.add_circle((SIZE / 2, SIZE / 2), radius=SIZE / 2)

doc.saveas('transformation_example_before.dxf')

# create a new block
block = doc.blocks.new_anonymous_block(base_point=(0, 0))
# create a list, because entities are removed from modelspace while iterating
for entity in list(msp):
    msp.move_to_layout(entity, block)

# insert block wherever you want
msp.add_blockref(block.name, insert=(10, 10), dxfattribs={
    'rotation': 23,  # with rotation
    'xscale': 1.5,  # and none uniform scaling
    'yscale': 3.7,
})

doc.saveas('transformation_example_after.dxf')

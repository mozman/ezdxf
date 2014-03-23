import ezdxf
import random  # needed for random placing points


def get_random_point():
    """Creates random x, y coordinates."""
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return x, y

# Create a new drawing in the DXF format of AutoCAD 2010
dwg = ezdxf.new('ac1024')

# Create a block with the name 'FLAG'
flag = dwg.blocks.new(name='FLAG')

# Add DXF entities to the block 'FLAG'.
# The default base point (= insertion point) of the block is (0, 0).
flag.add_polyline2d([(0, 0), (0, 5), (4, 3), (0, 3)])  # the flag as 2D polyline
flag.add_circle((0, 0), .4, dxfattribs={'color': 2})  # mark the base point with a circle

# Get the modelspace of the drawing.
modelspace = dwg.modelspace()

# Get 50 random placing points.
placing_points = [get_random_point() for _ in range(50)]

for point in placing_points:
    # Every flag has a different scaling and a rotation of -15 deg.
    random_scale = 0.5 + random.random() * 2.0
    # Add a block reference to the block named 'FLAG' at the coordinates 'point'.
    modelspace.add_blockref('FLAG', point, dxfattribs={
        'xscale': random_scale,
        'yscale': random_scale,
        'rotation': -15
    })

# Save the drawing.
dwg.saveas("blockref_tutorial.dxf")

# Define some attributes for the block 'FLAG', placed relative to the base point, (0, 0) in this case.
flag.add_attdef('NAME', (0.5, -0.5), {'height': 0.5, 'color': 3})
flag.add_attdef('XPOS', (0.5, -1.0), {'height': 0.25, 'color': 4})
flag.add_attdef('YPOS', (0.5, -1.5), {'height': 0.25, 'color': 4})

# Get another 50 random placing points.
placing_points = [get_random_point() for _ in range(50)]

for number, point in enumerate(placing_points):
    # values is a dict with the attribute tag as item-key and the attribute text content as item-value.
    values = {
        'NAME': "P(%d)" % (number+1),
        'XPOS': "x = %.3f" % point[0],
        'YPOS': "y = %.3f" % point[1]
    }

    # Every flag has a different scaling and a rotation of +15 deg.
    random_scale = 0.5 + random.random() * 2.0
    modelspace.add_auto_blockref('FLAG', point, values, dxfattribs={
        'xscale': random_scale,
        'yscale': random_scale,
        'rotation': 15
    })

# Save the drawing.
dwg.saveas("auto_blockref_tutorial.dxf")
# Collect all block references starting with 'U*'

anonymous_block_refs = modelspace.query('INSERT[name ? "^\*U.+"]')

# Collect real references to 'FLAG'
flag_refs = []
for block_ref in anonymous_block_refs:
    block = dwg.blocks.get(block_ref.dxf.name)
    flag_refs.extend(block.query('INSERT[name=="FLAG"]'))

# Collect all flag names.
flag_numbers = []
for flag in flag_refs:
    flag_number = flag.get_attrib('NAME')
    if flag_number is not None:
        flag_numbers.append(flag_number.dxf.text)

print(flag_numbers)
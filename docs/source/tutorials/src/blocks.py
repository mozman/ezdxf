import ezdxf
import random  # needed for random placing points


def get_random_point():
    """Returns random x, y coordinates."""
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return x, y


# Create a new drawing in the DXF format of AutoCAD 2010
doc = ezdxf.new('R2010')

# Create a block with the name 'FLAG'
flag = doc.blocks.new(name='FLAG')

# Add DXF entities to the block 'FLAG'.
# The default base point (= insertion point) of the block is (0, 0).
flag.add_lwpolyline([(0, 0), (0, 5), (4, 3), (0, 3)])  # the flag symbol as 2D polyline
flag.add_circle((0, 0), .4, dxfattribs={'color': 2})  # mark the base point with a circle

# Get the modelspace of the drawing.
msp = doc.modelspace()

# Get 50 random placing points.
placing_points = [get_random_point() for _ in range(50)]

for point in placing_points:
    # Every flag has a different scaling and a rotation of -15 deg.
    random_scale = 0.5 + random.random() * 2.0
    # Add a block reference to the block named 'FLAG' at the coordinates 'point'.
    msp.add_blockref('FLAG', point, dxfattribs={
        'xscale': random_scale,
        'yscale': random_scale,
        'rotation': -15
    })

# Save the drawing.
doc.saveas("blockref_tutorial.dxf")

# Define some attributes for the block 'FLAG', placed relative
# to the base point, (0, 0) in this case.
flag.add_attdef('NAME', (0.5, -0.5), dxfattribs={'height': 0.5, 'color': 3})
flag.add_attdef('XPOS', (0.5, -1.0), dxfattribs={'height': 0.25, 'color': 4})
flag.add_attdef('YPOS', (0.5, -1.5), dxfattribs={'height': 0.25, 'color': 4})

# Get another 50 random placing points.
placing_points = [get_random_point() for _ in range(50)]

for number, point in enumerate(placing_points):
    # values is a dict with the attribute tag as item-key and
    # the attribute text content as item-value.
    values = {
        'NAME': "P(%d)" % (number + 1),
        'XPOS': "x = %.3f" % point[0],
        'YPOS': "y = %.3f" % point[1]
    }

    # Every flag has a different scaling and a rotation of +15 deg.
    random_scale = 0.5 + random.random() * 2.0
    msp.add_auto_blockref('FLAG', point, values, dxfattribs={
        'xscale': random_scale,
        'yscale': random_scale,
        'rotation': 15
    })

# Save the drawing.
doc.saveas("auto_blockref_tutorial.dxf")

block = doc.blocks.get('FLAG')
# Getting the block layout from the block reference is also possible:
# block = flag_ref.block()
for flag_ref in msp.query('INSERT[name=="FLAG"]'):
    brcs = flag_ref.brcs()
    for entity in block:
        # Copy entity with all DXF attributes
        # Not all DXF types support copying!
        try:
            copy = doc.entitydb.duplicate_entity(entity)
        except ezdxf.DXFTypeError:
            continue
        if entity.dxftype() == 'CIRCLE':
            # OCS support is ignored to keep it simple
            # scaling and rotating is applied by transforming center to WCS
            copy.dxf.center = brcs.to_wcs(entity.dxf.center)
            # simple scaling of radius
            copy.dxf.radius = entity.dxf.radius * flag_ref.dxf.xscale
            # but first problem of exploding blocks shows up:
            # convert CIRCLE/ARC to ELLIPSE if x- and y-scaling is not uniform

        elif entity.dxftype() == 'LWPOLYLINE':
            # this will not work if the block reference establish an OCS
            # and the transformed LWPOLYLINE is placed in 3D space,
            # but luckily non uniform scaling is not a problem.
            transformed_points = []
            for x, y, s, e, b in copy.get_points(format='xyseb'):
                p = brcs.to_wcs((x, y))
                transformed_points.append((p[0], p[1], s, e, b))
            copy.set_points(transformed_points, format='xyseb')

        # add copy to modelspace
        msp.add_entity(copy)

    # Last step is to move attached ATTRIB entities into modelspace,
    # the attributes are already placed in WCS.
    for attrib in flag_ref.attribs:
        msp.add_entity(attrib)
    # Unlink ATTRIB entities else they will be destroyed by deleting
    # the block reference.
    flag_ref.attribs = []
    # delete 'exploded' block reference
    msp.delete_entity(flag_ref)

.. _tut_blocks:

Tutorial for Blocks
===================

What are Blocks?
----------------

Blocks are reusable elements, you can see it as container for other DXF entities which can be placed multiply times on
different places. But instead of inserting the DXF entities of the block several times just a block reference is placed.

Create a Block
--------------

Blocks are managed by the :class:`BlocksSection` class and every drawing has only one blocks section:
:attr:`Drawing.blocks`.

::

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

Insert a Block
--------------

A block reference is a DXF :class:`Insert` entity and can be placed in any :ref:`layout`:
:ref:`model space`, any :ref:`paper space` or a :ref:`block layout` (which enables blocks in blocks).
Every block reference can be scaled and rotated individually.

Lets insert some random flags into the modelspace::

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

What are Attributes?
--------------------

An attribute (:class:`Attrib`) is a text annotation to block reference with an associated tag.
Attributes are often used to add information to blocks which can be evaluated and exported by CAD programs.
An attribute can be visible or hidden. The simple way to use attributes is just to add an attribute to a block
reference by :meth:`Insert.add_attrib`, but the attribute is geometrically not related to the block, so you
have to calculate the insertion point, rotation and scaling of the attribute by yourself.

Using Attribute Definitions
---------------------------

The second way to use attributes in block references is a two step process, first step is to create an attribute
definition (template) in the block definition, the second step is adding the block reference by
:meth:`Layout.add_auto_blockref` ('auto' is for automatically filled attributes). The advantage of this method is that
all attributes are placed relative to the block base point with the same rotation and scaling as the block, but it has
the disadvantage, that the block reference is wrapped into an anonymous block, which makes evaluation of attributes more
complex.

Using attribute definitions (:class:`Attdef`)::

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

Get/Set Attributes of Existing Block References
-----------------------------------------------

See the howto: :ref:`howto_get_attribs`

Evaluate wrapped block references
---------------------------------

As mentioned above evaluation of block references wrapped into anonymous blocks is complex::

    # Collect all anonymous block references starting with '*U'
    anonymous_block_refs = modelspace.query('INSERT[name ? "^\*U.+"]')

    # Collect real references to 'FLAG'
    flag_refs = []
    for block_ref in anonymous_block_refs:
        # Get the block layout of the anonymous block
        block = dwg.blocks.get(block_ref.dxf.name)
        # Find all block references to 'FLAG' in the anonymous block
        flag_refs.extend(block.query('INSERT[name=="FLAG"]'))

    # Evaluation example: collect all flag names.
    flag_numbers = [flag.get_attrib_text('NAME') for flag in flag_refs if flag.has_attrib('NAME')]

    print(flag_numbers)


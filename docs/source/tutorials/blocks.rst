.. _tut_blocks:

Tutorial for Blocks
===================

What are Blocks?
----------------

Blocks are collections of DXF entities which can be placed multiply times as
block references in different layouts and other block definitions.
The block reference (:class:`~ezdxf.entities.Insert`) can be rotated, scaled,
placed in 3D by :ref:`OCS` and arranged in a grid like manner, each
:class:`~ezdxf.entities.Insert` entity can have individual attributes
(:class:`~ezdxf.entities.Attrib`) attached.


Create a Block
--------------

Blocks are managed as :class:`~ezdxf.layouts.BlockLayout` by a
:class:`~ezdxf.sections.blocks.BlocksSection` object, every drawing has only
one blocks section stored in the attribute: :attr:`Drawing.blocks`.

.. literalinclude:: src/blocks.py
    :lines: 1-21

Block References (Insert)
-------------------------

A block reference is a DXF :class:`~ezdxf.entities.Insert` entity and can be placed in any layout:
:class:`~ezdxf.layouts.Modelspace`, any :class:`~ezdxf.layouts.Paperspace` or :class:`~ezdxf.layouts.BlockLayout`
(which enables nested block references). Every block reference can be scaled and rotated individually.

Lets insert some random flags into the modelspace:

.. literalinclude:: src/blocks.py
    :lines: 23-40

Query all block references of block ``FLAG``:

.. code-block:: python

    for flag_ref in msp.query('INSERT[name=="FLAG"]'):
        print(str(flag_ref))

When inserting a block reference into the modelspace or another block
layout with different units, the scaling factor between these units
should be applied as scaling attributes (:attr:`xscale`, ...) e.g.
modelspace in meters and block in centimeters, :attr:`xscale` has to
be 0.01.

What are Attributes?
--------------------

An attribute (:class:`~ezdxf.entities.Attrib`) is a text annotation attached to a block reference with an associated tag.
Attributes are often used to add information to blocks which can be evaluated and exported by CAD programs.
An attribute can be visible or hidden. The simple way to use attributes is just to add an attribute to a block
reference by :meth:`Insert.add_attrib`, but the attribute is geometrically not related to the
block reference, so you have to calculate the insertion point, rotation and scaling of the attribute by yourself.

Using Attribute Definitions
---------------------------

The second way to use attributes in block references is a two step process, first step is to create an attribute
definition (template) in the block definition, the second step is adding the block reference by
:meth:`Layout.add_blockref` and attach and fill attribute automatically by the
:meth:`~ezdxf.entities.Insert.add_auto_attribs` method to the block reference.
The advantage of this method is that all attributes are placed relative to the block base point with the same
rotation and scaling as the block, but has the disadvantage that non uniform scaling is not handled very well.
The method :meth:`Layout.add_auto_blockref` handles non uniform scaling better by wrapping the block reference and its
attributes into an anonymous block and let the CAD application do the transformation work which will create correct
graphical representations at least by AutoCAD and BricsCAD. This method has the disadvantage of a more complex
evaluation of attached attributes

Using attribute definitions (:class:`~ezdxf.entities.Attdef`):

.. literalinclude:: src/blocks.py
    :lines: 42-69

Get/Set Attributes of Existing Block References
-----------------------------------------------

See the howto: :ref:`howto_get_attribs`

Evaluate Wrapped Block References
---------------------------------

As mentioned above evaluation of block references wrapped into anonymous blocks is complex:

.. code-block:: python

    # Collect all anonymous block references starting with '*U'
    anonymous_block_refs = modelspace.query('INSERT[name ? "^\*U.+"]')

    # Collect real references to 'FLAG'
    flag_refs = []
    for block_ref in anonymous_block_refs:
        # Get the block layout of the anonymous block
        block = doc.blocks.get(block_ref.dxf.name)
        # Find all block references to 'FLAG' in the anonymous block
        flag_refs.extend(block.query('INSERT[name=="FLAG"]'))

    # Evaluation example: collect all flag names.
    flag_numbers = [flag.get_attrib_text('NAME') for flag in flag_refs if flag.has_attrib('NAME')]

    print(flag_numbers)


Exploding Block References
--------------------------

This is an advanced and still experimental feature and because `ezdxf` is still not a CAD application, the
results may no be perfect. **Non uniform scaling** lead to incorrect results for text entities
(TEXT, MTEXT, ATTRIB) and some other entities like HATCH with arc or ellipse path segments.

By default the "exploded" entities are added to the same layout as the block
reference is located.


.. code-block:: Python

    for flag_ref in msp.query('INSERT[name=="FLAG"]'):
        flag_ref.explode()

Examine Entities of Block References
------------------------------------

If you just want to examine the entities of a block reference use the :meth:`~ezdxf.entities.Insert.virtual_entities`
method.
This methods yields "virtual" entities with attributes identical to "exploded" entities but they are not
stored in the entity database, have no handle and are not assigned to any layout.

.. code-block:: Python

    for flag_ref in msp.query('INSERT[name=="FLAG"]'):
        for entity in flag_ref.virtual_entities():
            if entity.dxftype() == 'LWPOLYLINE':
                print(f'Found {str(entity)}.')


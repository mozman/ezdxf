.. _tut_blocks:

Tutorial for Blocks
===================

If you are not familiar with the concept of blocks, please read this first:
Concept of :ref:`block_concept`

Create a Block
--------------

Blocks are managed as :class:`~ezdxf.layouts.BlockLayout` objects by the
:class:`~ezdxf.sections.blocks.BlocksSection` object, every drawing has only
one blocks section referenced by attribute :attr:`Drawing.blocks`.

.. literalinclude:: src/blocks.py
    :lines: 1-21

Block References (Insert)
-------------------------

A block reference can be created by adding an :class:`~ezdxf.entities.Insert`
entity to any of these layout types:

  - :class:`~ezdxf.layouts.Modelspace`
  - :class:`~ezdxf.layouts.Paperspace`
  - :class:`~ezdxf.layouts.BlockLayout`

A block reference can be scaled and rotated individually.
Lets add some random flags to the modelspace:

.. literalinclude:: src/blocks.py
    :lines: 23-40

Query all block references of block ``FLAG``:

.. code-block:: python

    for flag_ref in msp.query('INSERT[name=="FLAG"]'):
        print(str(flag_ref))

When adding a block reference to a layout with different units, the scaling
factor between these units should be applied as scaling attributes
(:attr:`xscale`, ...) e.g. modelspace in meters and block in centimeters,
:attr:`xscale` has to be 0.01.

Block Attributes
----------------

A block attribute (:class:`~ezdxf.entities.Attrib`) is a text annotation
attached to a block reference with an associated tag.
Attributes are often used to add information to blocks which can be evaluated
and exported by CAD applications.
An attribute can be added to a block reference by the :meth:`Insert.add_attrib`
method, the ATTRIB entity is geometrically not related to the block reference,
so insertion point, rotation and scaling of the attribute have to be calculated
by the user, but helper tools for that do exist.

Using Attribute Definitions
---------------------------

Another way to add attributes to block references is using attribute templates
(:class:`~ezdxf.entities.AttDef`). First create the attribute definition in the
block definition, then add the block reference by :meth:`add_blockref`
and attach and fill attributes automatically by the :meth:`~ezdxf.entities.Insert.add_auto_attribs`
method to the block reference. This method has the advantage that all attributes
are placed relative to the block base point with the same rotation and scaling
as the block reference, but non-uniform scaling is not handled very well.

The :meth:`~ezdxf.layouts.BaseLayout.add_auto_blockref` method handles
non-uniform scaling better by wrapping the block reference and its attributes
into an anonymous block and let the CAD application do the transformation work.
This method has the disadvantage of a more complex evaluation of attached
attributes

Using attribute definitions (:class:`~ezdxf.entities.AttDef` templates):

.. literalinclude:: src/blocks.py
    :lines: 42-68

Get/Set Attributes of Existing Block References
-----------------------------------------------

See the howto: :ref:`howto_get_attribs`

Evaluate Wrapped Block References
---------------------------------

As mentioned above the evaluation of block references wrapped into anonymous
blocks is complex:

.. code-block:: python

    # Collect all anonymous block references starting with '*U'
    anonymous_block_refs = modelspace.query('INSERT[name ? "^\*U.+"]')

    # Collect the references of the 'FLAG' block
    flag_refs = []
    for block_ref in anonymous_block_refs:
        # Get the block layout of the anonymous block
        block = doc.blocks.get(block_ref.dxf.name)
        # Find all block references to 'FLAG' in the anonymous block
        flag_refs.extend(block.query('INSERT[name=="FLAG"]'))

    # Evaluation example: collect all flag names.
    flag_numbers = [
        flag.get_attrib_text("NAME")
        for flag in flag_refs
        if flag.has_attrib("NAME")
    ]

    print(flag_numbers)


Exploding Block References
--------------------------

This is an advanced feature and the results may not be perfect.
A **non-uniform scaling** lead to incorrect results for text entities (TEXT,
MTEXT, ATTRIB) and some other entities like HATCH with circular- or elliptic
path segments.  The "exploded" entities are added to the same layout as the
block reference by default.


.. code-block:: Python

    for flag_ref in msp.query('INSERT[name=="FLAG"]'):
        flag_ref.explode()

Examine Entities of Block References
------------------------------------

To just examine the content entities of a block reference use the
:meth:`~ezdxf.entities.Insert.virtual_entities` method.
This methods yields "virtual" entities with properties identical to "exploded"
entities but they are not stored in the entity database, have no handle and are
not assigned to any layout.

.. code-block:: Python

    for flag_ref in msp.query('INSERT[name=="FLAG"]'):
        for entity in flag_ref.virtual_entities():
            if entity.dxftype() == "LWPOLYLINE":
                print(f"Found {str(entity)}.")


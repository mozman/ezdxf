.. _tut_blocks:

Tutorial for Blocks
===================

What are Blocks?
----------------

Blocks are collections of DXF entities which can be placed multiply times at different layouts and blocks as
references to the block definition. The block reference (:class:`~ezdxf.entities.Insert`) can be rotated, scaled,
placed in 3D by :ref:`OCS` and arranged in a grid like manner, each :class:`~ezdxf.entities.Insert` entity can
have individual attributes (:class:`~ezdxf.entities.Attrib`) attached.


Create a Block
--------------

Blocks are managed as :class:`~ezdxf.layouts.BlockLayout` by the :class:`~ezdxf.sections.blocks.BlocksSection` class
and every drawing has only one blocks section: :attr:`Drawing.blocks`.

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
:meth:`Layout.add_auto_blockref` ('auto' is for automatically filled attributes).
The advantage of this method is that all attributes are placed relative to the block base point with the same
rotation and scaling as the block, but it has the disadvantage, that the block reference is wrapped into an
anonymous block, which makes evaluation of attributes more complex.

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


Copying Block Reference Entities Into Modelspace
------------------------------------------------

.. versionadded:: 0.11.2

This is an advanced feature and not for beginners!

Because `ezdxf` is still not a CAD application, the most work has to be done by yourself.
The transformation of coordinates and directions has to be done individually for each
entity in the block definition.

First get the block reference coordinate system :class:`~ezdxf.entities.BRCS`,
which provides all required transformation methods, next step is to iterate over all
block entities and copy the entities into modelspace and transform their coordinates
and properties if required:

.. literalinclude:: src/blocks.py
    :lines: 71-

This is a kind of poor mans :func:`explode` function, which also shows the problems which
are arising by supporting :ref:`OCS` and scaling.
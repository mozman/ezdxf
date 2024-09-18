.. _add_blockrefs:

Add Block References
====================

Blocks are collections of DXF entities which can be placed multiple times as block 
references in different layouts and other block definitions.  
A block reference is represented by the INSERT entity.

Add Block Reference
-------------------

Add a block reference to the modelspace for a block definition "BlockName"::

    my_block_ref = msp.add_blockref('BlockName', location, dxfattribs={
        'xscale': 1.0,
        'yscale': 1.0,
        'zscale': 1.0,
        'rotation': angle,
    })

Non-uniform scaling is supported by CAD applications. The rotations angle is in degrees 
(circle=360 degrees).

- :meth:`ezdxf.layouts.BaseLayout.add_blockref`

Add Block Attribute
-------------------

To avoid confusion, it's important to distinguish block attributes (ATTRIB entities) 
from DXF attributes. Block attributes are text annotations linked to a block reference. 
They have their own location and can be attached to any block reference, even without a 
corresponding attribute definition (ATTDEF) in the block layout.

Add a block attribute to :code:`my_block_ref`::

    my_attribute = my_block_ref.add_attrib("MY_TAG", "VALUE_STR")
    my_attribute.set_placement(location)


- "MY_TAG": a unique identifier or label for the attribute, unique in the context of 
  the block reference
- "VALUE_STR": the text content displayed by the attribute

Block attributes are a subtype of the TEXT entity. This means they inherit placement and 
editing functionalities from the TEXT class.

- :meth:`ezdxf.entities.Insert.add_attrib`
- :meth:`ezdxf.entities.Text.set_placement`


Add Block Attribute from Template
---------------------------------

Block definitions can include pre-defined templates for attributes using ATTDEF entities. 
The :meth:`~ezdxf.entities.Insert.add_auto_attribs` method simplifies adding these 
attributes to block references. It takes a dictionary argument where:

- Keys: the attribute tags (e.g. "MY_TAG").
- Values: the content for each attribute (e.g. "VALUE_STR").

The :meth:`add_auto_attribs` method automatically attaches attributes (ATTRIB entities) 
to the block reference. These attributes inherit relevant DXF properties (layer, color, 
text style, etc.) from the corresponding ATTDEF entities within the block definition.

The method also ensures that the relative position of each attribute within the block 
reference mirrors the position of its corresponding ATTDEF entity relative to the 
block origin::

    my_block_ref.add_auto_attrib({"MY_TAG": "VALUE_STR"})


- :meth:`ezdxf.entities.Insert.add_auto_attribs`

.. seealso::

    **Tasks:**

    - :ref:`add_dxf_entities`
    - :ref:`copy_or_move_entities`
    - :ref:`delete_dxf_entities`

    **Tutorials:**

    - :ref:`tut_blocks`
    - :ref:`tut_getting_data`
    - :ref:`tut_simple_drawings`

    **Basics:**

    - :ref:`modelspace_concept`
    - :ref:`paperspace_concept`
    - :ref:`block_concept`

    **Classes:**

    - :class:`ezdxf.layouts.BlockLayout`
    - :class:`ezdxf.entities.BlockRecord`
    - :class:`ezdxf.entities.Block`
    - :class:`ezdxf.entities.Insert`
    - :class:`ezdxf.entities.Attrib`
    - :class:`ezdxf.entities.AttDef`
    - :class:`ezdxf.entities.Text`
    

.. _delete_layouts:

Delete Layouts and Blocks
=========================

Modelspace
----------

This is not possible.

Paperspace Layouts
------------------

Delete a paperspace layout and it's entities.

.. code-block::

    name = "MyLayout"
    try:
        doc.layouts.delete(name)
    except ezdxf.DXFKeyError:
        print(f"layout '{name}' not found")
    except ezdxf.DXFValueError:
        print(f"layout '{name}' cannot be deleted")
        # modelspace or last remaining paperspace layout

Block Definitions
-----------------

Delete a block definition:

.. code-block::

    try:
        doc.blocks.delete_block(name, safe=True)
    except ezdxf.DXFBlockInUseError:
        print(f"cannot delete block '{name}'")

Raises a :class:`DXFBlockInUseError` exception if the block is referenced by an INSERT
entity or if it is an anonymous/special block.

Purge/delete unused (unreferenced) block definitions:

.. versionadded:: 1.3.5

.. code-block::

    from ezdxf import blkrefs

    ...

    for name in blkrefs.find_unreferenced_blocks(doc)
        doc.blocks.delete_block(name, safe=False)

.. seealso::

    **Tasks:**

    - :ref:`add_layouts`
    - :ref:`get_layouts`
    - :ref:`add_blockrefs`
    - :ref:`delete_dxf_entities`

    **Tutorials:**

    - :ref:`tut_blocks`

    **Basics:**

    - :ref:`layout`
    - :ref:`modelspace_concept`
    - :ref:`paperspace_concept`
    - :ref:`block_concept`

    **Classes:**

    - :class:`ezdxf.layouts.Layouts`
    - :class:`ezdxf.document.Drawing`

    **Modules:**

    - :mod:`ezdxf.blkrefs`

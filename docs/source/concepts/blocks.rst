.. _block_concept:

Blocks
======

Blocks are collections of DXF entities which can be placed multiple times as
block references in different layouts and other block definitions.
The block reference (:class:`~ezdxf.entities.Insert`) can be rotated, scaled,
placed in 3D space by :ref:`OCS` and arranged in a grid like manner, each
:class:`~ezdxf.entities.Insert` entity can have individual attributes
(:class:`~ezdxf.entities.Attrib`) attached.

Block Attributes
----------------

A block attribute (:class:`~ezdxf.entities.Attrib`) is a text annotation attached
to a block reference with an associated tag. Attributes are often used to add
information to block references which can be evaluated and exported by CAD
applications.

Extended Block Features
-----------------------

Autodesk added many new features to BLOCKS (dynamic blocks, constraints) as
undocumented DXF entities, many of these features are not fully supported by
other CAD application and `ezdxf` also has no support or these features beyond
the preservation of these undocumented DXF entities.

.. seealso::

    :ref:`tut_blocks`

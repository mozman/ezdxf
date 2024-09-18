.. _add_resource_table_entries:

Add Resource Table Entries
==========================

All resources require a unique name in their category (names are case-insensitive).

Layer 
-----

A layer in a DXF document is a category that controls visual properties (like color and 
linetype) for associated entities. It acts like a grouping tag, not a container.

Add a new layer to a DXF document::

    doc.layers.add("MY_NEW_LAYER", color=1, linetype="DASHED")

DXF entities reference layers, but layers themselves don't directly contain entities. 
Instead, each entity has a :attr:`dxf.layer` attribute that specifies the layer by name 
it belongs to.

- :meth:`ezdxf.sections.table.LayerTable.add`

Linetype
--------

The linetype defines the rendering pattern of linear graphical entities like LINE, ARC, 
CIRCLE and so on. 

Add a new linetype to a DXF document::

    doc.linetypes.add("DOTTED", pattern=[0.2, 0.0, -0.2])

- :meth:`ezdxf.sections.table.LinetypeTable.add`

Text Style
----------

The text style defines the rendering font for text based entities like TEXT, ATTRIB and 
MTEXT.

Add a new text style to a DXF document::

    doc.styles.add("ARIAL", font="arial.ttf")

- :meth:`ezdxf.sections.table.TextstyleTable.add`

Dimension Style
---------------

The dimension style defines the initial properties for the DIMENSION entity.

Add a new dimension style to a DXF document::

    doc.dimstyles.add("EZDXF")

- :meth:`ezdxf.sections.table.DimStyleTable.add`

AppID
-----

The XDATA section of DXF entities is grouped by AppIDs and these ids require an entry in 
the :class:`AppIDTable` otherwise the DXF file in invalid (for AutoCAD)::

    doc.appids.add("EZDXF")

- :meth:`ezdxf.sections.table.AppIDTable.add`

.. seealso::

    **Tutorials:**

    - :ref:`tut_layers`
    - :ref:`tut_linetypes`
    - :ref:`tut_text`
    - :ref:`tut_mtext`
    - :ref:`tut_common_graphical_attributes`

    **Basics:**

    - :ref:`layer_concept`
    - :ref:`linetypes`
    - :ref:`lineweights`
    - :ref:`aci`
    - :ref:`true color`
    - :ref:`font resources`

    **Classes:**

    - :class:`ezdxf.entities.Layer`
    - :class:`ezdxf.entities.Linetype`
    - :class:`ezdxf.entities.Textstyle`
    - :class:`ezdxf.entities.DimStyle`
    - :class:`ezdxf.entities.Appid`
    - :mod:`ezdxf.fonts.fonts`

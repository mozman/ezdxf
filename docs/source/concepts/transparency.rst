.. _transparency:

Transparency
============

The support for transparency was added to the DXF file format in revision R2004.
The raw transparency value stored as 32 bit value in the DXF namespace as
:attr:`transparency` attribute, has a range from 0 to 255 where 0 is fully
transparent and 255 if opaque and has the top byte set to ``0x02``.
For a more easy usage all graphical entities support the
:attr:`~ezdxf.entities.DXFGraphic.transparency` property to get and set the
transparency as float value in the range frem 0.0 to 1.0 where 0.0 is opaque and
1.0 is fully transparent. The transparency value can be set explicit in the
entity, by layer or by block.

.. code-block:: Python

    import ezdxf

    doc = ezdxf.new()
    msp = doc.modelspace()
    line = msp.add_line((0, 0), (10, 0))
    line.transparency = 0.5

.. seealso::

    - :mod:`ezdxf.colors`
    - :ref:`tut_common_graphical_attributes`
    - Autodesk Knowledge Network: `About Making Objects Transparent`_
    - BricsCAD Help Center: `Entity Transparency`_

.. _About Making Objects Transparent: https://knowledge.autodesk.com/support/autocad/learn-explore/caas/CloudHelp/cloudhelp/2019/ENU/AutoCAD-Core/files/GUID-E6EB9CA5-B039-4262-BE17-1AD3E7230EF7-htm.html
.. _Entity Transparency: https://help.bricsys.com/document/_guides--BCAD_2D_drafting--GD_transparency/V22/EN_US?id=165079137340

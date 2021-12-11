.. _aci:

AutoCAD Color Index (ACI)
=========================

The :attr:`~ezdxf.entities.DXFGraphic.dxf.color` attribute represents an `ACI`
(AutoCAD Color Index).
AutoCAD and many other :term:`CAD` application provides a default color table,
but pen table would be the more correct term.
Each ACI entry defines the color value, the line weight and some other
attributes to use for the pen. This pen table can be edited by the user or
loaded from an :term:`CTB` or :term:`STB` file.
`Ezdxf` provides functions to create (:func:`~ezdxf.acadctb.new`) or modify
(:func:`ezdxf.acadctb.load`) plot styles files.


DXF R12 and prior are not good in preserving the layout of a drawing, because
of the lack of a standard color table defined by the DXF reference and missing
DXF structures to define these color tables in the DXF file. So if a CAD
user redefined an ACI and do not provide a :term:`CTB` or :term:`STB` file,
you have no ability to determine which color or lineweight was used. This is
better in later DXF versions by providing additional DXF attributes like
:attr:`~ezdxf.entities.DXFGraphic.dxf.lineweight` and
:attr:`~ezdxf.entities.DXFGraphic.dxf.true_color`.

.. seealso::

    :ref:`plot_style_files`
    :mod:`ezdxf.colors`

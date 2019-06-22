.. _aci:

AutoCAD Color Index (ACI)
=========================

The :attr:`color` value represents an `ACI` (AutoCAD Color Index). AutoCAD and every other CAD application provides a
default color table, but pen table would be the more correct term. Each ACI entry defines the color value, the line
weight and some other attributes to use for the pen. This pen table can be edited by the user or loaded from an
`.ctb` file.


DXF R12 and prior are not good in preserving the layout of a drawing, because of the lack of a standard color table
defined by the DXF reference and missing DXF structures to define these color tables in the DXF file. So if a CAD
user redefined an ACI and do not provide a .ctb file, you have no ability to determine which color or lineweight
was used. This is better in later DXF versions by providing additional DXF attributes like :attr:`lineweight`,
:attr:`true_color` and :attr:`transparency`.

.. _dxf units:

.. module:: ezdxf.units

DXF Units
=========

The `DXF reference`_ has no explicit information how to handle units in DXF, any
information in this section is based on experiments with BricsCAD and may differ
in other CAD application, BricsCAD tries to be as compatible with AutoCAD as
possible. Therefore, this information should also apply to AutoCAD.

Please open an issue on `github`_ if you have any corrections or additional
information about this topic.

Length Units
------------

Any length or coordinate value in DXF is unitless in the first place, there is
no unit information attached to the value. The unit information comes from the
context where a DXF entity is used. The document/modelspace get the unit
information from the header variable $INSUNITS, paperspace and block layouts get
their unit information form the attribute :attr:`~ezdxf.layouts.BaseLayout.units`.
The modelspace object has also a :attr:`units` property, but this value do not
represent the modelspace units, this value is always set to 0 "unitless".

Get and set  document/modelspace units as enum by the
:class:`~ezdxf.document.Drawing` property :attr:`units`:

.. code-block:: python

    import ezdxf
    from ezdxf import units

    doc = ezdxf.new()
    # Set centimeter as document/modelspace units
    doc.units = units.CM
    # which is a shortcut (including validation) for
    doc.header['$INSUNITS'] = units.CM

Block Units
-----------

As said each block definition can have independent units, but there is no
implicit unit conversion applied, not in CAD applications and not in ezdxf.

When inserting a block reference (INSERT) into the modelspace or another block
layout with different units, the scaling factor between these units **must** be
applied explicit as scaling DXF attributes (:attr:`xscale`, ...) of the
:class:`~ezdxf.entities.Insert` entity, e.g. modelspace in meters and block in
centimeters, x-, y- and z-scaling has to be 0.01:

.. code-block:: python

    doc.units = units.M
    my_block = doc.blocks.new('MYBLOCK')
    my_block.units = units.CM
    block_ref = msp.add_block_ref('MYBLOCK')
    # Set uniform scaling for x-, y- and z-axis
    block_ref.set_scale(0.01)

Use helper function :func:`conversion_factor` to calculate the
scaling factor between units:

.. code-block:: python

    factor = units.conversion_factor(doc.units, my_block.units)
    # factor = 100 for 1m is 100cm
    # scaling factor = 1 / factor
    block_ref.set_scale(1.0/factor)

.. hint::

    It is never a good idea to use different measurement system in one
    document, ask the NASA about their Mars Climate Orbiter from 1999.
    The same applies for units of the same measurement system, just use one unit
    like meters or inches.


Angle Units
-----------

Angles are always in degrees (360 deg = full circle) and in counter clockwise
orientation, unless stated explicit otherwise.

Display Format
--------------

How values are shown in the CAD GUI is controlled by the header variables
$LUNITS and $AUNITS, but this has no meaning for values stored in DXF files.

$INSUNITS
---------

The most important setting is the header variable $INSUNITS, this variable
defines the drawing units for the modelspace and therefore for the DXF
document if no further settings are applied.

The modelspace LAYOUT entity has a property :attr:`~ezdxf.layouts.BaseLayout.units`
as any layout like object, but it seem to have no meaning for the modelspace,
BricsCAD set this property always to 0, which means unitless.

The most common units are 6 for meters and 1 for inches.

.. code-block:: python


    doc.header['$INSUNITS'] = 6

=== ===============
0   Unitless
1   Inches, :attr:`units.IN`
2   Feet, :attr:`units.FT`
3   Miles, :attr:`units.MI`
4   Millimeters, :attr:`units.MM`
5   Centimeters, :attr:`units.CM`
6   Meters, :attr:`units.M`
7   Kilometers, :attr:`units.KM`
8   Microinches
9   Mils
10  Yards, :attr:`units.YD`
11  Angstroms
12  Nanometers
13  Microns
14  Decimeters, :attr:`units.DM`
15  Decameters
16  Hectometers
17  Gigameters
18  Astronomical units
19  Light years
20  Parsecs
21  US Survey Feet
22  US Survey Inch
23  US Survey Yard
24  US Survey Mile
=== ===============

$MEASUREMENT
------------

The header variable $MEASUREMENT controls whether the current drawing uses
imperial or metric hatch pattern and linetype files, this setting is not applied
correct in `ezdxf` yet, but will be fixed in the future:

This setting is independent from $INSUNITS, it is possible to set the drawing
units to inch and use metric linetypes and hatch pattern.

In BricsCAD the base scaling of the linetypes is only depending from the
$MEASUREMENT value, is not relevant if $INSUNITS is meter, centimeter,
millimeter, ... and so on and the same is valid for hatch pattern.

.. code-block:: python


    doc.header['$MEASUREMENT'] = 1

=== ===============
0   English
1   Metric
=== ===============

$LUNITS
-------

The header variable $LUNITS defines how CAD applications show linear values in
the GUI and has no meaning for `ezdxf`:

.. code-block:: python


    doc.header['$LUNITS'] = 2

=== ===============
1   Scientific
2   Decimal (default)
3   Engineering
4   Architectural
5   Fractional
=== ===============

$AUNITS
-------

The header variable $AUNITS defines how CAD applications show angular values in
the GUI and has no meaning for `ezdxf`, DXF angles are always degrees in
counter-clockwise orientation, unless stated explicit otherwise:

.. code-block:: python

    doc.header['$AUNITS'] = 0

=== ===============
0   Decimal degrees
1   Degrees/minutes/seconds
2   Grad
3   Radians
=== ===============

Helper Tools
------------

.. autofunction:: conversion_factor

.. _github: https://github.com/mozman/ezdxf/issues
.. _DXF reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3
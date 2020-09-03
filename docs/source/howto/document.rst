General Document
================


General preconditions:

.. code-block:: python

    import sys
    import ezdxf

    try:
        doc = ezdxf.readfile("your_dxf_file.dxf")
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file.')
        sys.exit(2)
    msp = doc.modelspace()

This works well with DXF files from trusted sources like AutoCAD or BricsCAD,
for loading DXF files with minor or major flaws look at the
:mod:`ezdxf.recover` module.

Load DXF Files with Structure Errors
------------------------------------

If you know the files you will process have most likely minor or major flaws,
use the :mod:`ezdxf.recover` module:

.. code-block:: Python

    import sys
    from ezdxf import recover

    try:  # low level structure repair:
        doc, auditor = recover.readfile(name)
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {name}.')
        sys.exit(2)

    # DXF file can still have unrecoverable errors, but this is maybe
    # just a problem when saving the recovered DXF file.
    if auditor.has_errors:
        print(f'Found unrecoverable errors in DXF file: {name}.')
        auditor.print_error_report()

For more loading scenarios follow the link: :mod:`ezdxf.recover`

.. _set/get header variables:

Set/Get Header Variables
------------------------

`ezdxf` has an interface to get and set HEADER variables:

.. code-block:: python

    doc.header['VarName'] = value
    value = doc.header['VarName']

.. seealso:: :class:`HeaderSection` and online documentation from Autodesk for available `header variables`_.

.. _set drawing units:

Set DXF Drawing Units
---------------------

Use this HEADER variables to setup the default units for CAD applications opening the DXF file.
This settings are not relevant for `ezdxf` API calls, which are unitless for length values and coordinates
and decimal degrees for angles (in most cases).

Sets drawing units:

$MEASUREMENT controls whether the current drawing uses imperial or metric hatch pattern and linetype files:

.. code-block:: python


    doc.header['$MEASUREMENT'] = 1

=== ===============
0   English
1   Metric
=== ===============

$LUNITS sets the linear units format for creating objects:

.. code-block:: python


    doc.header['$LUNITS'] = 2

=== ===============
1   Scientific
2   Decimal (default)
3   Engineering
4   Architectural
5   Fractional
=== ===============

$AUNITS set units format for angles:

.. code-block:: python

    doc.header['$AUNITS'] = 0

=== ===============
0   Decimal degrees
1   Degrees/minutes/seconds
2   Grad
3   Radians
=== ===============

$INSUNITS set default drawing units for AutoCAD DesignCenter blocks:

.. code-block:: python


    doc.header['$INSUNITS'] = 6

=== ===============
0   Unitless
1   Inches
2   Feet
3   Miles
4   Millimeters
5   Centimeters
6   Meters
7   Kilometers
8   Microinches
9   Mils
10  Yards
11  Angstroms
12  Nanometers
13  Microns
14  Decimeters
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

Create More Readable DXF Files (DXF Pretty Printer)
---------------------------------------------------

DXF files are plain text files, you can open this files with every text editor which handles bigger files.
But it is not really easy to get quick the information you want.

Create a more readable HTML file (DXF Pretty Printer):

.. code-block::

    # on Windows
    py -3 -m ezdxf.pp your_dxf_file.dxf

    # on Linux/Mac
    python3 -m ezdxf.pp your_dxf_file.dxf

This produces a HTML file `your_dxf_file.html` with a nicer layout than a plain DXF file and DXF handles as links
between DXF entities, this simplifies the navigation between the DXF entities.

.. versionchanged:: 0.8.3

    Since ezdxf `v0.8.3 <https://ezdxf.mozman.at/release-v0-8-3.html>`_, a script called ``dxfpp`` will be added
    to your Python script path:

.. code-block:: none

    usage: dxfpp [-h] [-o] [-r] [-x] [-l] FILE [FILE ...]

    positional arguments:
      FILE             DXF files pretty print

    optional arguments:
      -h, --help       show this help message and exit
      -o, --open       open generated HTML file with the default web browser
      -r, --raw        raw mode - just print tags, no DXF structure interpretation
      -x, --nocompile  don't compile points coordinates into single tags (only in
                       raw mode)
      -l, --legacy     legacy mode - reorders DXF point coordinates


.. important:: This does not render the graphical content of the DXF file to a HTML canvas element.

Set Initial View/Zoom for the Modelspace
----------------------------------------

To show an arbitrary location of the modelspace centered in the CAD application window, set the ``'*Active'`` VPORT to
this location. The DXF attribute :attr:`dxf.center` defines the location in the modelspace, and the :attr:`dxf.height`
specifies the area of the modelspace to view. Shortcut function:

.. code-block:: Python

    doc.set_modelspace_vport(height=10, center=(10, 10))

.. versionadded:: 0.11

.. _header variables: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A
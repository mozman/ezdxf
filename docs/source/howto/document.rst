General Document
================


General preconditions:

.. code-block:: python

    import sys
    import ezdxf

    try:
        doc = ezdxf.readfile("your_dxf_file.dxf")
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file.")
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
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file: {name}.")
        sys.exit(2)

    # DXF file can still have unrecoverable errors, but this is maybe
    # just a problem when saving the recovered DXF file.
    if auditor.has_errors:
        print(f"Found unrecoverable errors in DXF file: {name}.")
        auditor.print_error_report()

For more loading scenarios follow the link: :mod:`ezdxf.recover`

.. _set/get header variables:

Set/Get Header Variables
------------------------

`ezdxf` has an interface to get and set HEADER variables:

.. code-block:: python

    doc.header["VarName"] = value
    value = doc.header["VarName"]

.. seealso::

    :class:`HeaderSection` and online documentation from Autodesk for
    available `header variables`_.

.. _set drawing units:

Set DXF Drawing Units
---------------------

The header variable $INSUNITS defines the drawing units for the modelspace and
therefore for the DXF document if no further settings are applied. The most
common units are 6 for meters and 1 for inches.

Use this HEADER variables to setup the default units for CAD applications
opening the DXF file. This setting is not relevant for `ezdxf` API calls,
which are unitless for length values and coordinates and decimal degrees for
angles (in most cases).

Sets drawing units:

.. code-block:: python


    doc.header["$INSUNITS"] = 6

For more information see section :ref:`DXF Units`.

Create More Readable DXF Files (DXF Pretty Printer)
---------------------------------------------------

DXF files are plain text files, you can open this files with every text editor
which handles bigger files. But it is not really easy to get quick the
information you want.

Create a more readable HTML file (DXF Pretty Printer):

.. code-block::

    # Call as executable script from the command line:
    ezdxf pp FILE [FILE ...]

    # Call as module on Windows:
    py -m ezdxf pp FILE [FILE ...]

    # Call as module on Linux/Mac
    python3 -m ezdxf pp FILE [FILE ...]

This creates a HTML file with a nicer layout than a plain text file, and
handles are links between DXF entities, this simplifies the navigation
between the DXF entities.

.. code-block:: none

    usage: ezdxf pp [-h] [-o] [-r] [-x] [-l] FILE [FILE ...]

    positional arguments:
      FILE             DXF files pretty print

    optional arguments:
      -h, --help       show this help message and exit
      -o, --open       open generated HTML file with the default web browser
      -r, --raw        raw mode - just print tags, no DXF structure interpretation
      -x, --nocompile  don't compile points coordinates into single tags (only in
                       raw mode)
      -l, --legacy     legacy mode - reorders DXF point coordinates


.. important::

    This does not render the graphical content of the DXF file to a HTML canvas
    element.

.. _calc msp extents:

Calculate Extents for the Modelspace
------------------------------------

Since `ezdxf` v0.16 exist a :mod:`ezdxf.bbox` module to calculate bounding
boxes for DXF entities. This module makes the extents calculation very easy,
but read the documentation for the :mod:`~ezdxf.bbox` module to understand its
limitations.

.. code-block:: Python

    import ezdxf
    from ezdxf import bbox

    doc = ezdxf.readfile("your.dxf")
    msp = doc.modelspace()

    extents = bbox.extents(msp)


The returned `extents` is a :class:`ezdxf.math.BoundingBox` object.

.. _set msp initial view:

Set Initial View/Zoom for the Modelspace
----------------------------------------

To show an arbitrary location of the modelspace centered in the CAD application
window, set the ``'*Active'`` VPORT to this location. The DXF attribute
:attr:`dxf.center` defines the location in the modelspace, and the :attr:`dxf.height`
specifies the area of the modelspace to view. Shortcut function:

.. code-block:: Python

    doc.set_modelspace_vport(height=10, center=(10, 10))

.. seealso::

    The :mod:`ezdxf.zoom` module is another way to set the initial modelspace
    view.

Setting the initial view to the extents of all entities in the modelspace:

.. code-block:: Python

    import ezdxf
    from ezdxf import zoom

    doc = ezdxf.readfile("your.dxf")
    msp = doc.modelspace()
    zoom.extents(msp)

Setting the initial view to the extents of just some entities:

.. code-block:: Python

    lines = msp.query("LINES")
    zoom.objects(lines)

The :mod:`~ezdxf.zoom` module also works for paperspace layouts.

.. Important::

    The :mod:`~ezdxf.zoom` module uses the :mod:`~ezdxf.bbox` module to
    calculate the bounding boxes for DXF entities. Read the documentation for
    the :mod:`~ezdxf.bbox` module to understand its limitations and the
    bounding box calculation for large documents can take a while!

Hide the UCS Icon
-----------------

The visibility of the UCS icon is controlled by the DXF
:attr:`~ezdxf.entities.VPort.dxf.ucs_icon` attribute of the
:class:`~ezdxf.entities.VPort` entity:

    - bit 0: 0=hide, 1=show
    - bit 1: 0=display in lower left corner, 1=display at origin

The state of the UCS icon can be set in conjunction with the initial
:class:`~ezdxf.entities.VPort` of the model space, this code turns off the UCS
icon:

.. code-block:: Python

    doc.set_modelspace_vport(10, center=(10, 10), dxfattribs={"ucs_icon": 0})

Alternative: turn off UCS icons for all :class:`VPort` entries in the active
viewport configuration:

.. code-block:: Python

    for vport in doc.viewports.get_config("*Active"):
        vport.dxf.ucs_icon = 0

Show Lineweights in DXF Viewers
-------------------------------

By default lines and curves are shown without lineweights in DXF viewers.
By setting the header variable $LWDISPLAY to 1 the DXF viewer should display
lineweights, if supported by the viewer.

.. code-block:: Python

    doc.header["$LWDISPLAY"] = 1

Add `ezdxf` Resources to Existing DXF Document
----------------------------------------------

Add all `ezdxf` specific resources (line types, text- and dimension styles)
to an existing DXF document:

.. code-block:: Python

    import ezdxf
    from ezdxf.tools.standards import setup_drawing

    doc = ezdxf.readfile("your.dxf")
    setup_drawing(doc, topics="all")

Set Logging Level of `ezdxf`
----------------------------

Set the logging level of the `ezdxf` package to a higher level to minimize
logging messages from ezdxf. At level ``ERROR`` only severe errors will be
logged and ``WARNING``, ``INFO`` and ``DEBUG`` messages will be suppressed:

.. code-block:: Python

    import logging

    logging.getLogger("ezdxf").setLevel(logging.ERROR)


.. _header variables: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A
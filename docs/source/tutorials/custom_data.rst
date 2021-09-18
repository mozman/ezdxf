.. _tut_custom_data:

Storing Custom Data in DXF Files
================================

This tutorial describes how to store custom data in DXF files using
standard DXF features.

Saving data in comments is not covered in this section, because comments are not
a reliable way to store information in DXF files and `ezdxf` does not support
adding comments to DXF files. Comments are also ignored by `ezdxf` and many
other DXF libraries when loading DXF files, but there is a :mod:`ezdxf.comments`
module to load comments from DXF files.

The DXF data format is a very versatile and flexible data format and supports
various ways to store custom data. This starts by setting special header variables,
storing XData, AppData and extension dictionaries in DXF entities and objects,
storing XRecords in the OBJECTS section and ends by using proxy entities or
even extending the DXF format by user defined entities and objects.

Retrieving User Data
--------------------

Retrieving the is a simple task by `ezdxf`, but often not possible in CAD
applications without using the scripting features (AutoLisp) or even the SDK.

.. warning::

    I have no experience with AutoLisp so far and I created this scripts for
    AutoLisp while writing this tutorial. There may be better ways to accomplish
    these tasks, and feedback on this is very welcome.
    Everything is tested with BricsCAD and should also work with the
    full version of AutoCAD.

This is the common prolog for all Python code examples shown in this tutorial:

.. code-block:: Python

    import ezdxf

    doc = ezdxf.new()
    msp = doc.modelspace()

Header Section
--------------

The HEADER section has tow ways to store custom data.

Predefined User Variables
+++++++++++++++++++++++++

There are ten predefined user variables, five 16-bit integer variables called
``$USERI1`` up to ``$USERI5`` and five floating point variables (reals) called
``$USERR1`` up to ``$USERR5``.
This is very limited and the data maybe will be overwritten by the next
application which opens and saves the DXF file. Advantage of this methods is,
it works for all supported DXF versions starting at R12.

Settings the data:

.. literalinclude:: src/customdata/header.py
    :lines: 10-11

Getting the data by `ezdxf`:

.. literalinclude:: src/customdata/header.py
    :lines: 14-15

Getting the data in `BricsCAD` at the command line::

    : USERI1
    New current value for USERI1 (-32768 to 32767) <4711>:

Getting the data by AutoLisp::

    : (getvar 'USERI1)
    4711

Setting the value by AutoLisp::

    : (setvar 'USERI1 1234)
    1234

Custom Document Properties
++++++++++++++++++++++++++

This method defines custom document properties, but requires at least DXF R2004.
The custom document properties are stored in a :class:`~ezdxf.sections.header.CustomVars`
instance in the :attr:`~ezdxf.sections.header.HeaderSection.custom_vars` attribute of
the :class:`~ezdxf.sections.header.HeaderSection` object and supports only
string values.

Settings the data:

.. literalinclude:: src/customdata/header.py
    :lines: 18

Getting the data by `ezdxf`:

.. literalinclude:: src/customdata/header.py
    :lines: 21

The document property ``MyFirstVar`` is available in `BricsCAD` as FIELD
variable:

.. image:: gfx/custom_header_property.png

AutoLisp script for getting the custom document properties:

.. code-block:: Lisp

    (defun C:CUSTOMDOCPROPS (/ Info Num Index Custom)
      (vl-load-com)
      (setq acadObject (vlax-get-acad-object))
      (setq acadDocument (vla-get-ActiveDocument acadObject))

      ;;Get the SummaryInfo
      (setq Info (vlax-get-Property acadDocument 'SummaryInfo))
      (setq Num (vla-NumCustomInfo Info))
      (setq Index 0)
      (repeat Num
        (vla-getCustomByIndex Info Index 'ID 'Value)
        (setq Custom (cons (cons ID Value) Custom))
        (setq Index (1+ Index))
      )  ;repeat

      (if Custom (reverse Custom))
    )

Running the script in BricsCAD:

.. code-block:: Text

    : (load "customdocprops.lsp")
    C:CUSTOMDOCPROPS
    : CUSTOMDOCPROPS
    (("MyFirstVar" . "First Value"))

Meta Data
---------

XDATA
-----

AppData
-------

Extension Dictionaries
----------------------

XRecord
-------

UserRecord
----------


.. _link1: https://adndevblog.typepad.com/autocad/2012/08/lisp-example-for-setting-and-getting-drawing-properties.html
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

Starting with version v0.16.4 `ezdxf` stores some meta data in the DXF file and
the AppID ``EZDXF`` will be created.
Two entries will be added to the :class:`~ezdxf.document.MetaData`
instance, the ``CREATED_BY_EZDXF`` for DXF documents created by `ezdxf` and the
entry ``WRITTEN_BY_EZDXF`` if the DXF document will be saved by `ezdxf`.
The marker string looks like this ``"0.17b0 @ 2021-09-18T05:14:37.921826+00:00"``
and contains the `ezdxf` version and an UTC timestamp in ISO format.

You can add your own data to the :class:`~ezdxf.document.MetaData`
instance as a string with a maximum of 254 characters and choose a good name
which may never be used by `ezdxf` in the future.

.. code-block:: Python

    metadata = doc.ezdxf_metadata()
    metadata["MY_UNIQUE_KEY"] = "my additional meta data"

    print(metadata.get("CREATED_BY_EZDXF"))
    print(metadata.get("MY_UNIQUE_KEY"))


The data is stored as XDATA in then BLOCK entity of the model space for DXF R12
and for DXF R2000 and later as a DXF :class:`~ezdxf.entities.Dictionary`
in the root dictionary by the key ``EZDXF_META``.
See following chapters for accessing such data by AutoLisp.

XDATA
-----

:ref:`extended_data` is a way to attach arbitrary data to DXF entities.
Each application needs a unique AppID registered in the AppID table to add
XDATA to an entity. The AppID ``ACAD`` is reserved and by using `ezdxf`
the AppID ``EZDXF`` is also registered automatically.
The total size of XDATA for a single DXF entity is limited to 16kB for AutoCAD.
XDATA is supported by all DXF versions and is accessible by AutoLisp.

The valid group codes for extended data are limited to the following values,
see also the internals of :ref:`xdata_internals`:

================= ==============================================================
Group Code        Description
================= ==============================================================
1000              Strings up to 255 bytes long
1001              (fixed) Registered application name up to 31 bytes long
1002              (fixed) An extended data control string ``'{'``  or ``'}'``
1004              Binary data
1005              Database Handle of entities in the drawing database
1010              Simple 3D point in WCS, in the order X, Y, Z
1011              3D point in WCS That is moved, scaled, rotated, mirrored,
                  and stretched along with the entity
1012              3D point in WCS that is scaled, rotated, and mirrored along
                  with the entity
1013              3D point in WCS that is scaled, rotated, and mirrored along
                  with the entity
1040              A real value
1041              Distance, a real value that is scaled along with the entity
1042              Scale Factor, a real value that is scaled along with the entity
1070              A 16-bit integer (signed or unsigned)
1071              A 32-bit signed (long) integer
================= ==============================================================

.. literalinclude:: src/customdata/xdata.py
    :lines: 10-40

Extension Dictionaries
----------------------

XRecord
-------

UserRecord
----------

AppData
-------

:ref:`application_defined_data` was introduced in DXF R13/14 and is used by
AutoCAD internally to store the handle to the :ref:`extension_dictionary` and
the :ref:`reactors` in DXF entities.
`Ezdxf` supports these kind of data storage for any AppID and the data is
preserved by AutoCAD and BricsCAD, but I haven't found a way to access this
data by AutoLisp or even the SDK.
So I don't recommend this feature to store application defined data,
because :ref:`extended_data` and the :ref:`extension_dictionary` are well
documented and safe ways to attach custom data to entities.

.. literalinclude:: src/customdata/appdata.py
    :lines: 10-26

Printed output:

.. code-block:: Text

    LINE(#30) has 3 tags of AppData for AppID 'YOUR_UNIQUE_ID'
    (300, 'custom text')
    (370, 4711)
    (460, 3.141592)

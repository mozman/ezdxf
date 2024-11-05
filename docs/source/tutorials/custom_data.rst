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

This is the common prolog for all Python code examples shown in this tutorial:

.. code-block:: Python

    import ezdxf

    doc = ezdxf.new()
    msp = doc.modelspace()

Retrieving User Data
--------------------

Retrieving the custom data is a simple task by `ezdxf`, but often not possible in CAD
applications without using the scripting features (AutoLISP) or even the SDK.

AutoLISP Resources
++++++++++++++++++

- `Autodesk Developer Documentation <http://help.autodesk.com/view/OARX/2018/ENU/>`_
- `AfraLISP`_
- `Lee Mac Programming <http://www.lee-mac.com>`_

.. warning::

    I have no experience with AutoLISP so far and I created this scripts for
    AutoLISP while writing this tutorial. There may be better ways to accomplish
    these tasks, and feedback on this is very welcome.
    Everything is tested with BricsCAD and should also work with the
    full version of AutoCAD.

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

Getting the data by AutoLISP::

    : (getvar 'USERI1)
    4711

Setting the value by AutoLISP::

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

AutoLISP script for getting the custom document properties:

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
See following chapters for accessing such data by AutoLISP.

XDATA
-----

:ref:`extended_data` is a way to attach arbitrary data to DXF entities.
Each application needs a unique AppID registered in the AppID table to add
XDATA to an entity. The AppID ``ACAD`` is reserved and by using `ezdxf`
the AppID ``EZDXF`` is also registered automatically.
The total size of XDATA for a single DXF entity is limited to 16kB for AutoCAD.
XDATA is supported by all DXF versions and is accessible by AutoLISP.

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
1010              3D point, in the order X, Y, Z that will not be modified at
                  any transformation of the entity
1011              A WCS point that is moved, scaled, rotated and mirrored
                  along with the entity
1012              A WCS displacement that is scaled, rotated and
                  mirrored along with the entity, but not moved
1013              A WCS direction that is rotated and mirrored along
                  with the entity but not moved and scaled.
1040              A real value
1041              Distance, a real value that is scaled along with the entity
1042              Scale Factor, a real value that is scaled along with the entity
1070              A 16-bit integer (signed or unsigned)
1071              A 32-bit signed (long) integer
================= ==============================================================

Group codes are not unique in the XDATA section and can be repeated, therefore
tag order matters.

.. literalinclude:: src/customdata/xdata.py
    :lines: 10-39

AutoLISP script for getting XDATA for AppID ``YOUR_UNIQUE_ID``:

.. code-block:: Lisp

    (defun C:SHOWXDATA (/ entity_list xdata_list)
        (setq entity_list (entget (car (entsel)) '("YOUR_UNIQUE_ID")))
        (setq xdata_list (assoc -3 entity_list))
        (car (cdr xdata_list))
    )

Script output:

.. code-block:: Text

    : SHOWXDATA
    Select entity: ("YOUR_UNIQUE_ID" (1000 . "custom text") (1040 . 3.141592) ...

.. seealso::

    - `AfraLISP XDATA tutorial <https://www.afralisp.net/autolisp/tutorials/extended-entity-data-part-1.php>`_
    - :ref:`extended_data` Reference

XDATA Helper Classes
--------------------

The :class:`~ezdxf.entities.xdata.XDataUserList` and
:class:`~ezdxf.entities.xdata.XDataUserDict` are helper classes to manage XDATA
content in a simple way.

Both classes store the Python types ``int``, ``float`` and ``str`` and the
`ezdxf` type :class:`~ezdxf.math.Vec3`. As the names suggests has the
:class:`XDataUserList` a list-like interface and the :class:`XDataUserDict` a
dict-like interface. This classes can not contain additional container types,
but multiple lists and/or dicts can be stored in the same XDATA section for the
same AppID.

These helper classes uses a fixed group code for each data type:

==== ========================
1001 strings (max. 255 chars)
1040 floats
1071 32-bit ints
1010 Vec3
==== ========================

Additional required imports for these examples:

.. code-block:: Python

    from ezdxf.math import Vec3
    from ezdxf.entities.xdata import XDataUserDict, XDataUserList

Example for :class:`~ezdxf.entities.xdata.XDataUserDict`:

Each :class:`XDataUserDict` has a unique name, the default name is "DefaultDict"
and the default AppID is ``EZDXF``.
If you use your own AppID, don't forget to create the requited AppID table entry
like :code:`doc.appids.new("MyAppID")`, otherwise AutoCAD will not open the
DXF file.

.. literalinclude:: src/customdata/xdata_helper.py
    :lines: 11-19

If you modify the content of without using the context manager
:meth:`~ezdxf.entities.xdata.XDataUserDict.entity`, you have to call
:meth:`~ezdxf.entities.xdata.XDataUserDict.commit` by yourself, to transfer the
modified data back into the XDATA section.

Getting the data back from an entity:

.. literalinclude:: src/customdata/xdata_helper.py
    :lines: 22-25

Example for :class:`~ezdxf.entities.xdata.XDataUserList`:

This example stores the data in a :class:`XDataUserList` named "AppendedPoints",
the default name is "DefaultList" and the default AppID is ``EZDXF``.

.. literalinclude:: src/customdata/xdata_helper.py
    :lines: 29-32

Now the content of both classes are stored in the same XDATA section for AppID
``EZDXF``. The :class:`XDataUserDict` is stored by the name "DefaultDict" and
the :class:`XDataUserList` is stored by the name "AppendedPoints".

Getting the data back from an entity:

.. literalinclude:: src/customdata/xdata_helper.py
    :lines: 35-39

.. seealso::

    - :class:`~ezdxf.entities.xdata.XDataUserList` class
    - :class:`~ezdxf.entities.xdata.XDataUserDict` class

Extension Dictionaries
----------------------

Extension dictionaries are another way to attach custom data to any DXF
entity. This method requires DXF R13/14 or later. I will use the short term
XDICT for extension dictionaries in this tutorial.

The :ref:`extension_dictionary` is a regular DXF :class:`~ezdxf.entities.Dictionary`
which can store (key, value) pairs where the key is a string and the value is a
DXF object from the OBJECTS section.
The usual objects to store custom data are :class:`~ezdxf.entities.DictionaryVar`
to store simple strings and :class:`~ezdxf.entities.XRecord` to store complex
data.

Unlike XDATA, custom data attached by extension dictionary will not be
transformed along with the DXF entity!

This example shows how to manage the XDICT and to store simple strings as
:class:`~ezdxf.entities.DictionaryVar` objects in the XDICT, to store more
complex data go to the next section `XRecord`_.

1. Get or create the XDICT for an entity:

.. literalinclude:: src/customdata/xdict.py
    :lines: 10-18

2. Add strings as :class:`~ezdxf.entities.DictionaryVar` objects to the XDICT.
No AppIDs required, but existing keys will be overridden, so be careful by
choosing your keys:

.. literalinclude:: src/customdata/xdict.py
    :lines: 20-21

3. Retrieve the strings from the XDICT as :class:`~ezdxf.entities.DictionaryVar`
objects:

.. literalinclude:: src/customdata/xdict.py
    :lines: 23-24


The AutoLISP access to DICTIONARIES is possible, but it gets complex and I'm
only referring to the `AfraLISP Dictionaries and XRecords`_ tutorial.

.. seealso::

    - `AfraLISP Dictionaries and XRecords`_ Tutorial
    - :ref:`extension_dictionary` Reference
    - DXF :class:`~ezdxf.entities.Dictionary` Reference
    - :class:`~ezdxf.entities.DictionaryVar` Reference

XRecord
-------

The :class:`~ezdxf.entities.XRecord` object can store arbitrary data like the
XDATA section, but is not limited by size and can use all group codes in the
range from 1 to 369 for :ref:`dxf_tags_internals`.
The :class:`~ezdxf.entities.XRecord` can be referenced by any DXF
:class:`~ezdxf.entities.Dictionary`, other :class:`XRecord` objects (tricky
ownership!), the XDATA section (store handle by group code 1005) or any other
DXF object by adding the :class:`XRecord` object to the
:ref:`extension_dictionary` of the DXF entity.

It is recommend to follow the DXF reference to assign appropriate group codes
to :ref:`dxf_tags_internals`. My recommendation is shown in the table
below, but all group codes from 1 to 369 are valid. I advice against using the
group codes 100 and 102 (structure tags) to avoid confusing generic tag loaders.
Unfortunately, Autodesk doesn't like general rules and uses DXF format
exceptions everywhere.

=== ======================
1   strings (max. 2049 chars)
2   structure tags as strings like ``"{"`` and  ``"}"``
10  points and vectors
40  floats
90  integers
330 handles
=== ======================

Group codes are not unique in :class:`XRecord` and can be repeated, therefore
tag order matters.

This example shows how to attach a :class:`~ezdxf.entities.XRecord` object to a
LINE entity by :ref:`extension_dictionary`:

.. literalinclude:: src/customdata/xrecord.py
    :lines: 11-28

Script output:

.. code-block:: Text

    [DXFTag(1, 'text1'),
     DXFTag(40, 3.141592),
     DXFTag(90, 256),
     DXFVertex(10, (1.0, 2.0, 0.0)),
     DXFTag(330, '30')]

Unlike XDATA, custom data attached by extension dictionary will not be
transformed along with the DXF entity! To react to entity modifications by a
CAD applications it is possible to write event handlers by AutoLISP, see the
`AfraLISP Reactors Tutorial`_ for more information. This is very advanced stuff!

.. seealso::

    - `AfraLISP Dictionaries and XRecords`_ Tutorial
    - `AfraLISP Reactors Tutorial`_
    - :class:`~ezdxf.entities.XRecord` Reference
    - helper functions: :func:`ezdxf.lldxf.types.dxftag` and :func:`ezdxf.lldxf.types.tuples_to_tags`

XRecord Helper Classes
----------------------

The :class:`~ezdxf.urecord.UserRecord` and :class:`~ezdxf.urecord.BinaryRecord`
are helper classes to manage XRECORD content in a simple way.
The :class:`~ezdxf.urecord.UserRecord` manages the data as plain
Python types: ``dict``, ``list``, ``int``, ``float``, ``str`` and the `ezdxf`
types :class:`~ezdxf.math.Vec2` and :class:`~ezdxf.math.Vec3`. The top level
type for the :attr:`UserRecord.data` attribute has to be a ``list``.
The :class:`~ezdxf.urecord.BinaryRecord` stores arbitrary binary data as `BLOB`_.
These helper classes uses fixed group codes to manage the data in XRECORD,
you have no choice to change them.

Additional required imports for these examples:

.. literalinclude:: src/customdata/urecord.py
    :lines: 6-11

Example 1: Store entity specific data in the :ref:`extension_dictionary`:


.. literalinclude:: src/customdata/urecord.py
    :lines: 23-37

Example 1: Get entity specific data back from the :ref:`extension_dictionary`:

.. literalinclude:: src/customdata/urecord.py
    :lines: 42-47

If you modify the content of :attr:`UserRecord.data` without using the context
manager, you have to call :meth:`~ezdxf.urecord.UserRecord.commit` by yourself,
to store the modified data back into the XRECORD.

Example 2: Store arbitrary data in DICTIONARY objects.
The XRECORD is stored in the named DICTIONARY, called :attr:`rootdict` in `ezdxf`.
This DICTIONARY is the root entity for the tree-like data structure
stored in the OBJECTS section, see also the documentation of the
:mod:`ezdxf.sections.objects` module.

.. literalinclude:: src/customdata/urecord.py
    :lines: 52-69

Example 2:  Get user data back from the DICTIONARY object

.. literalinclude:: src/customdata/urecord.py
    :lines: 74-78

Example 3: Store arbitrary binary data

.. literalinclude:: src/customdata/urecord.py
    :lines: 83-91

Example 3: Get binary data back from the DICTIONARY object

.. literalinclude:: src/customdata/urecord.py
    :lines: 99-106

.. hint::

    Don't be fooled, the ability to save any binary data such as images, office
    documents, etc. in the DXF file doesn't impress AutoCAD, it simply ignores
    this data, this data only has a meaning for your application!

.. seealso::

    - :mod:`~ezdxf.urecord` module
    - :class:`~ezdxf.urecord.UserRecord` class
    - :class:`~ezdxf.urecord.BinaryRecord` class


AppData
-------

:ref:`application_defined_data` was introduced in DXF R13/14 and is used by
AutoCAD internally to store the handle to the :ref:`extension_dictionary` and
the :ref:`reactors` in DXF entities.
`Ezdxf` supports these kind of data storage for any AppID and the data is
preserved by AutoCAD and BricsCAD, but I haven't found a way to access this
data by AutoLISP or even the SDK.
So I don't recommend this feature to store application defined data,
because :ref:`extended_data` and the :ref:`extension_dictionary` are well
documented and safe ways to attach custom data to entities.

.. literalinclude:: src/customdata/appdata.py
    :lines: 10-25

Printed output:

.. code-block:: Text

    LINE(#30) has 3 tags of AppData for AppID 'YOUR_UNIQUE_ID'
    (300, 'custom text')
    (370, 4711)
    (460, 3.141592)

.. _AfraLISP: https://www.afralisp.net/index.php
.. _AfraLISP Dictionaries and XRecords: https://www.afralisp.net/autolisp/tutorials/dictionaries-and-xrecords.php
.. _Visual AutoLISP: https://www.afralisp.net/visual-lisp/
.. _AfraLISP Reactors Tutorial: https://www.afralisp.net/visual-lisp/tutorials/reactors-part-1.php
.. _BLOB: https://en.wikipedia.org/wiki/Binary_large_object
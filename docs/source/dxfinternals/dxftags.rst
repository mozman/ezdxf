.. _DXF Tags:

DXF Tags
========

A Drawing Interchange File is simply an ASCII text file with a file
type of .dxf and special formatted text. The basic file structure
are DXF tags, a DXF tag consist of a DXF group code as an integer
value on its own line and a the DXF value on the following line.
In the ezdxf documentation DXF tags will be written as :code:`(group code, value)`.

Group codes are indicating the value type:

============ ==================
Group Code   Value Type
============ ==================
0-9          String (with the introduction of extended symbol names in DXF R2000, the 255-character limit has been
             increased to 2049 single-byte characters not including the newline at the end of the line)
10-39        Double precision 3D point value
40-59        Double-precision floating-point value
40-59        Double-precision floating-point value
60-79        16-bit integer value
90-99        32-bit integer value
100          String (255-character maximum, less for Unicode strings)
102          String (255-character maximum, less for Unicode strings)
105          String representing hexadecimal (hex) handle value
110-119      Double precision floating-point value
120-129      Double precision floating-point value
130-139      Double precision floating-point value
140-149      Double precision scalar floating-point value
160-169      64-bit integer value
170-179      16-bit integer value
210-239      Double-precision floating-point value
270-279      16-bit integer value
280-289      16-bit integer value
290-299      Boolean flag value
300-309      Arbitrary text string
310-319      String representing hex value of binary chunk
320-329      String representing hex handle value
330-369      String representing hex object IDs
370-379      16-bit integer value
380-389      16-bit integer value
390-399      String representing hex handle value
400-409      16-bit integer value
410-419      String
420-429      32-bit integer value
430-439      String
440-449      32-bit integer value
450-459      Long
460-469      Double-precision floating-point value
470-479      String
480-481      String representing hex handle value
999          Comment (string)
1000-1009    String (same limits as indicated with 0-9 code range)
1010-1059    Double-precision floating-point value
1060-1070    16-bit integer value
1071         32-bit integer value
============ ==================

Explanation for some important group codes:

================= =======
Group Code        Meaning
================= =======
0                 DXF structure tag, entity start/end or table entries
1                 The primary text value for an entity
2                 A name: Attribute tag, Block name, and so on. Also used to identify a DXF section or table name.
3-4               Other textual or name values
5                 Entity handle expressed as a hex string (fixed)
6                 Line type name (fixed)
7                 Text style name (fixed)
8                 Layer name (fixed)
9                 Variable name identifier (used only in HEADER section of the DXF file)
10                Primary X coordinate (start point of a Line or Text entity, center of a Circle, etc.)
11-18             Other X coordinates
20                Primary Y coordinate. 2n values always correspond to 1n values and immediately follow them in the file
                  (expected by ezdxf!)
21-28             Other Y coordinates
30                Primary Z coordinate. 3n values always correspond to 1n and 2n values and immediately follow them in the
                  file (expected by ezdxf!)
31-38             Other Z coordinates
39                This entity's thickness if nonzero (fixed)
40-48             Float values (text height, scale factors, etc.)
49                Repeated value - multiple 49 groups may appear in one entity for variable length tables (such as the dash
                  lengths in the LTYPE table). A 7x group always appears before the first 49 group to specify the table
                  length
50-58             Angles
62                Color number (fixed)
66                "Entities follow" flag (fixed), only in INSERT and POLYLINE entities
67                Identifies whether entity is in model space or paper space
68                Identifies whether viewport is on but fully off screen, is not active, or is off
69                Viewport identification number
70-78             Integer values such as repeat counts, flag bits, or modes
210, 220, 230     X, Y, and Z components of extrusion direction (fixed)
999               Comments
================= =======

For explanation of all group codes see: `DXF Group Codes in Numerical Order Reference`_ provided by Autodesk

.. _xdata_tags:

Extended Data
-------------

Extended data (XDATA) is created by AutoLISP or ObjectARX applications but any other application like *ezdxf* can also
define XDATA. If an entity contains extended data, it **follows** the entity's normal definition data but ends
**before** :ref:`Embedded Objects`.

But extended group codes (>=1000) can appear **before** the XDATA section, an example is the BLOCKBASEPOINTPARAMETER
entity in AutoCAD Civil 3D or AutoCAD Map 3D.

================= ===================================================================================
Group Code        Description
================= ===================================================================================
1000              Strings in extended data can be up to 255 bytes long (with the 256th byte reserved
                  for the null character)
1001              (fixed) Registered application name (ASCII string up to 31 bytes long) for XDATA
1002              (fixed) An extended data control string can be either “{”or “}”.
                  These braces enable applications to organize their data by subdividing
                  the data into lists. Lists can be nested.
1003              Name of the layer associated with the extended data
1004              Binary data is organized into variable-length chunks. The maximum length of each
                  chunk is 127 bytes. In ASCII DXF files, binary data is represented as a string of
                  hexadecimal digits, two per binary byte
1005              Database Handle of entities in the drawing database, see also:
                  :ref:`About 1005 Group Codes`
1010, 1020, 1030  Three real values, in the order X, Y, Z. They can be used as a point or vector
                  record.
1011, 1021, 1031  Unlike a simple 3D point, the world space coordinates are moved, scaled, rotated,
                  mirrored, and stretched along with the parent entity to which the extended data
                  belongs.
1012, 1012, 1022  Also a 3D point that is scaled, rotated, and mirrored along with the parent
                  (but is not moved or stretched)
1013, 1023, 1033  Also a 3D point that is scaled, rotated, and mirrored along with the parent
                  (but is not moved or stretched)
1040              A real value
1041              Distance, a real value that is scaled along with the parent entity
1042              Scale Factor, also a real value that is scaled along with the parent.
                  The difference between a distance and a scale factor is application-defined
1070              A 16-bit integer (signed or unsigned)
1071              A 32-bit signed (long) integer
================= ===================================================================================


The :code:`(1001, ...)` tag indicates the beginning of extended data. In contrast to normal entity data, with extended
data the same group code can appear multiple times, and **order is important**.

Extended data is grouped by registered application name. Each registered application group begins with a
:code:`(1001, APPID)` tag, with the application name as APPID string value. Registered application names correspond to
APPID symbol table entries.

An application can use as many APPID names as needed. APPID names are permanent, although they can be purged if they
aren't currently used in the drawing. Each APPID name can have **no more than one data group** attached to each entity.
Within an application group, the sequence of extended data groups and their meaning is defined by the application.

.. _String Value Encoding:

String Value Encoding
---------------------

String values stored in a DXF file is plain ASCII or UTF-8, AutoCAD also supports CIF (Common Interchange Format) and MIF
(Maker Interchange Format) encoding. The UTF-8 format is only supported in DXF R2007 and later.

ezdxf on import converts all strings into Python unicode strings without encoding or decoding CIF/MIF.

String values containing Unicode characters are represented with control character sequences.

For example, 'TEST\U+7F3A\U+4E4F\U+89E3\U+91CA\U+6B63THIS\U+56FE'

To support the DXF unicode encoding ezdxf registers an encoding codec `dxf_backslash_replace`, defined in
:func:`ezdxf.lldxf.encoding`.

String values can be stored with these dxf group codes:

- 0 - 9
- 100 - 101
- 300 - 309
- 410 - 419
- 430 - 439
- 470 - 479
- 999 - 1003

Multi Tag Text (MTEXT)
----------------------

If the text string is less than 250 characters, all characters appear in tag :code:`(1, ...)`. If the text string is
greater than 250 characters, the string is divided into 250-character chunks, which appear in one or more
:code:`(3, ...)` tags. If :code:`(3, ...)` tags are used, the last group is a :code:`(1, ...)` tag and has fewer than
250 characters:

.. code-block:: none

    3
    ... TwoHundredAndFifty Characters ....
    3
    ... TwoHundredAndFifty Characters ....
    1
    less than TwoHundredAndFifty Characters

As far I know this is only supported by the MTEXT entity.

.. seealso::

    :ref:`DXF File Encoding`

.. _Tag Structure DXF R13 and later:

Tag Structure DXF R13 and later
-------------------------------

With the introduction of DXF R13 Autodesk added additional group codes and DXF tag structures to the DXF Standard.

Subclass Markers
~~~~~~~~~~~~~~~~

Subclass markers :code:`(100, Subclass Name)` divides DXF objects into several sections. Group codes can be reused
in different sections. A subclass ends with the following subclass marker or at the beginning of xdata or the end of the
object. See `Subclass Marker Example`_ in the DXF Reference.

Extension Dictionary
~~~~~~~~~~~~~~~~~~~~

The extension dictionary is an optional sequence that stores the handle of a dictionary object that belongs to the
current object, which in turn may contain entries. This facility allows attachment of arbitrary database objects to any
database object. Any object or entity may have this section.

The extension dictionary tag sequence:

.. code-block:: none

  102
  {ACAD_XDICTIONARY
  360
  Hard-owner ID/handle to owner dictionary
  102
  }

Persistent Reactors
~~~~~~~~~~~~~~~~~~~

Persistent reactors are an optional sequence that stores object handles of objects registering themselves as reactors on
the current object. Any object or entity may have this section.

The persistent reactors tag sequence:

.. code-block:: none

  102
  {ACAD_REACTORS
  330
  first Soft-pointer ID/handle to owner dictionary
  330
  second Soft-pointer ID/handle to owner dictionary
  ...
  102
  }

.. _app_data_tags:

Application-Defined Codes
~~~~~~~~~~~~~~~~~~~~~~~~~

Starting at DXF R13, DXF objects can contain application-defined codes outside of XDATA. This application-defined
codes can contain any tag except :code:`(0, ...)` and :code:`(102, '{...')`. "{YOURAPPID" means the APPID string with an
preceding "{". The application defined data tag sequence:

.. code-block:: none

    102
    {YOURAPPID
    ...
    102
    }

:code:`(102, 'YOURAPPID}')` is also a valid closing tag:

.. code-block:: none

    102
    {YOURAPPID
    ...
    102
    YOURAPPID}

All groups defined with a beginning :code:`(102, ...)` appear in the DXF reference before the first subclass marker,
I don't know if these groups can appear after the first or any subclass marker. ezdxf accepts them at any position,
and by default ezdxf adds new app data in front of the first subclass marker to the first tag section of an DXF object.

**Exception XRECORD:** Tags with group code 102 and a value string without a preceding "{" or the scheme "YOURAPPID}",
should be treated as usual group codes.

.. _Embedded Objects:

Embedded Objects
~~~~~~~~~~~~~~~~

The concept of embedded objects was introduced with AutoCAD 2018 (DXF version AC1032) and this is the only information
I found about it at the Autodesk knowledge base: `Embedded and Encapsulated Objects`_

Quote from `Embedded and Encapsulated Objects`_:

    For DXF filing, the embedded object must be filed out and in after all the data of the encapsulating object
    has been filed out and in.

    A separator is needed between the encapsulating object's data and the subsequent embedded object's data.
    The separator must be similar in function to the group 0 or 100 in that it must cause the filer to stop
    reading data. The normal DXF group code 0 cannot be used because DXF proxies use it to determine when to
    stop reading data. The group code 100 could have been used, but it might have caused confusion when manually
    reading a DXF file, and there was a need to distinguish when an embedded object is about to be written out in
    order to do some internal bookkeeping. Therefore, the DXF group code 101 was introduced.

**Hard facts:**

- Embedded object start with :code:`(101, "Embedded Object")` tag
- Embedded object is appended to the encapsulated object
- :code:`(101, "Embedded Object")` tag is the end of the encapsulating object, also of its :ref:`xdata_tags`
- Embedded object tags can contain any group code except the DXF structure tag :code:`(0, ...)`

**Unconfirmed assumptions:**

- The encapsulating object can contain more than one embedded object.
- Embedded objects separated by :code:`(101, "Embedded Object")` tags
- every entity can contain embedded objects
- XDATA sections replaced by embedded objects, at least for the MTEXT entity

Real world example from an AutoCAD 2018 file:

.. code-block:: none

  100       <<< start of encapsulating object
  AcDbMText
  10
  2762.148
  20
  2327.073
  30
  0.0
  40
  2.5
  41
  18.852
  46
  0.0
  71
  1
  72
  5
  1
  {\fArial|b0|i0|c162|p34;CHANGE;\P\P\PTEXT}
  73
  1
  44
  1.0
  101       <<< start of embedded object
  Embedded Object
  70
  1
  10
  1.0
  20
  0.0
  30
  0.0
  11
  2762.148
  21
  2327.073
  31
  0.0
  40
  18.852
  41
  0.0
  42
  15.428
  43
  15.043
  71
  2
  72
  1
  44
  18.852
  45
  12.5
  73
  0
  74
  0
  46
  0.0

.. include:: reflinks.inc


.. _DXF Group Codes in Numerical Order Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-3F0380A5-1C15-464D-BC66-2C5F094BCFB9

.. _Subclass Marker Example: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-CC5ACB1B-BBA3-463B-84A5-6CCD320C66E7

.. _Embedded and Encapsulated Objects: https://knowledge.autodesk.com/search-result/caas/CloudHelp/cloudhelp/2017/ENU/OARXMAC-DevGuide/files/GUID-C953866F-A335-4FFD-AE8C-256A76065552-htm.html
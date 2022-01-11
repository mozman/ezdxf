.. _reference:

Reference
=========

The `DXF Reference`_ is online available at `Autodesk`_.

Quoted from the original DXF 12 Reference which is not available on the web:

   Since the AutoCAD drawing database (.dwg file) is written in a
   compact format that changes significantly as new features are added
   to AutoCAD, we do not document its format and do not recommend that
   you attempt to write programs to read it directly. To assist in
   interchanging drawings between AutoCAD and other programs, a Drawing
   Interchange file format (DXF) has been defined. All implementations
   of AutoCAD accept this format and are able to convert it to and from
   their internal drawing file representation.

DXF Document
------------

.. toctree::
    :maxdepth: 2

    drawing/management
    drawing/drawing
    drawing/recover
    appsettings

DXF Structures
--------------

.. toctree::
    :maxdepth: 2

    sections/index
    tables/index
    blocks/index
    layouts/index
    groups
    dxfentities/index
    dxfobjects/index
    xdata
    appdata
    xdict
    reactors
    blkrefs
    const

DXF Entity Creation
-------------------

.. toctree::
    :maxdepth: 1

    entity_creation

Enums
-----

.. toctree::
    :maxdepth: 1

    enums

Colors
------

.. toctree::
    :maxdepth: 1

    colors

Data Query
----------

.. toctree::
    :maxdepth: 1

    query
    groupby

Math Utilities
--------------

.. toctree::
    :maxdepth: 1

    math

Construction
------------

.. toctree::
    :maxdepth: 1

    path
    disassemble
    bbox
    upright

Custom Data
-----------

.. toctree::
    :maxdepth: 1

    user_xdata
    user_record

Tools
-----

.. toctree::
    :maxdepth: 2

    tools/functions
    tools/gfxattribs
    tools/text
    tools/text_size
    tools/fonts


Global Options
--------------

.. toctree::
    :maxdepth: 1

    options


Miscellaneous
-------------

.. toctree::
    :maxdepth: 1

    zoom
    comments
    reorder

.. _DXF Reference: http://docs.autodesk.com/ACD/2014/ENU/index.html?url=files/GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3.htm,topicNumber=d30e652301
.. _Autodesk: http://usa.autodesk.com/
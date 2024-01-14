DXF Objects
===========

All DXF objects can only reside in the OBJECTS section of a DXF document.

The purpose of the OBJECTS section is to allow CAD software developers to define and
store custom objects that are not included in the basic DXF file format. These custom
objects can be used to represent complex data structures, such as database tables or
project management information, that are not easily represented by basic DXF entities.

By including custom objects in the OBJECTS section, CAD software developers can extend
the functionality of their software to support new types of data and objects. For
example, a custom application might define a new type of block or dimension style that
is specific to a particular industry or workflow. By storing this custom object
definition in the OBJECTS section, the CAD software can recognize and use the new object
type in a drawing.

In summary, the OBJECTS section is an important part of the DXF file format because it
allows CAD software developers to extend the functionality of their software by defining
and storing custom objects and entity types. This makes it possible to represent complex
data structures and workflows in CAD drawings, and allows CAD software to be customized
to meet the specific needs of different industries and applications.

.. toctree::
    :maxdepth: 1

    dictionary
    dxflayout
    dxfobject
    geodata
    imagedef
    mleaderstyle
    placeholder
    plotsettings
    spatial_filter
    sun
    underlaydef
    xrecord

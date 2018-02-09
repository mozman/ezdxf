.. _Coordinate Systems:

Coordinate Systems
==================

`AutoLISP Reference to Coordinate Systems <http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-0F0B833D-78ED-4491-9918-9481793ED10B>`_
provided by Autodesk.

WCS
---

World coordinate system - the reference coordinate system. All other coordinate systems are defined relative to the WCS,
which never changes. Values measured relative to the WCS are stable across changes to other coordinate systems.

UCS
---

User coordinate system - the working coordinate system defined by the user to make drawing tasks easier. All points
passed to AutoCAD commands, including those returned from AutoLISP routines and external functions, are points in the
current UCS. As far as I know, all coordinates stored in DXF files are always WCS or OCS never UCS.

OCS
---

Object coordinate system - coordinates relative to the object itself. These points are usually converted into the WCS,
current UCS, or current DCS, according to the intended use of the object. Conversely, points must be translated into an
OCS before they are written to the database. This is also known as the entity coordinate system.

DCS
---

Display coordinate system - the coordinate system into which objects are transformed before they are displayed. The
origin of the DCS is the point stored in the AutoCAD system variable TARGET, and its Z axis is the viewing direction.
In other words, a viewport is always a plan view of its DCS. These coordinates can be used to determine where something
will be displayed to the AutoCAD user.

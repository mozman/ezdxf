.. _Handles:

Handles
=======

A handle is an arbitrary but in your DXF file unique hex value as string like '10FF'.
It is common to to use uppercase letters for hex numbers. Handle can have up to 16
hexadecimal digits (8 bytes).

For DXF R10 until R12 the usage of handles was optional. The header variable $HANDLING
set to 1 indicate the usage of handles, else $HANDLING is 0 or missing.

For DXF R13 and later the usage of handles is mandatory and the header variable $HANDLING
was removed.

The $HANDSEED variable in the header section should be greater than the biggest handle
used in the DXF file, so a CAD application can assign handle values starting with the
$HANDSEED value. But as always, don't rely on the header variable it could be wrong,
AutoCAD ignores this value.

Handle Definition
-----------------

Entity handle definition is always the :code:`(5, ...)`, except for entities of the
DIMSTYLE table :code:`(105, ...)`, because the DIMSTYLE entity has also a group
code 5 tag for DIMBLK.

Handle Pointer
--------------

A pointer is a reference to a DXF object in the same DXF file. There are four types of
pointers:

- Soft-pointer handle
- Hard-pointer handle
- Soft-owner handle
- Hard-owner handle

Also, a group code range for "arbitrary" handles is defined to allow convenient storage
of handle values that are unchanged at any operation (AutoCAD).

Pointer and Ownership
---------------------

A pointer is a reference that indicates usage, but not possession or responsibility, for
another object. A pointer reference means that the object uses the other object in some
way, and shares access to it. An ownership reference means that an owner object is
responsible for the objects for which it has an owner handle.  An object can have any
number of pointer references associated with it, but it can have only one owner.

Hard and Soft References
------------------------

Hard references, whether they are pointer or owner, protect an object from being purged.
Soft references do not.

In AutoCAD, block definitions and complex entities are hard owners of their elements.
A symbol table and dictionaries are soft owners of their elements. Polyline entities are
hard owners of their vertex and seqend entities. Insert entities are hard owners of
their attrib and seqend entities.

When establishing a reference to another object, it is recommended that you think about
whether the reference should protect an object from the PURGE command.

A hard- and soft pointers will be translated during INSERT and XREF operations.

Arbitrary Handles
-----------------

Arbitrary handles are distinct in that they are not translated to session-persistent
identifiers internally, or to entity names in AutoLISP, and so on. They are stored as
handles. When handle values are translated in drawing-merge operations, arbitrary handles
are ignored.

In all environments, arbitrary handles can be exchanged for entity names of the current
drawing by means of the handent functions. A common usage of arbitrary handles is to
refer to objects in external DXF and DWG files.

.. _About 1005 Group Codes:

About 1005 Group Codes
----------------------

:code:`(1005, ...)` xdata have the same behavior and semantics as soft pointers, which
means that they are translated whenever the host object is merged into a different
drawing. However, 1005 items are not translated to session-persistent identifiers or
internal entity names in AutoLISP and ObjectARX. They are stored as handles.

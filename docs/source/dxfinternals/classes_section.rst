.. _Classes Section:

Classes Section
===============


CLASS Entities
--------------

CLASS entities have no handle!

ezdxf needs for all entities handles and therefor store a :code:`(5, handle)` tag in CLASS entities, but do not write
this handle tags into DXF files.

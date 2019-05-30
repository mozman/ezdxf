TODO
====

Python Code
-----------

- import data from DXF files
    - import paper space layouts
- optimized Vector class, SVec for simple or speedy vectors? profiling required!!!

DXF Entities
------------

- DIMENSION rendering
    - angular dim
    - angular 3 point dim
    - diameter dim
    - radius dim
    - ordinate dim
- MLEADER
- MLINE
- FIELD
- ACAD_TABLE

DXF Audit & Cleanup
-------------------

- check ownership
    - DXF objects in OBJECTS section
    - DXF Entities in a layout (model space, paper space, block)
- check required DXF attributes:
    - R12: layer; cleanup: set to '0' (in ezdxf defaults to '0')
    - R2000+: layer, owner?, handle?
- VERTEX on same layer as POLYLINE; cleanup: set VERTEX layer to POLYLINE layer
- find unreferenced objects:
    - DICTIONARY e.g. orphaned extension dicts; cleanup: delete
- find unused BLOCK definitions: has no corresponding INSERT (except layout blocks); cleanup: delete

Documentation
-------------

- use auto-doc feature of sphinx
  - for all DXF entities
  - for all DXF objects
  - for all table entries
  - for all modules

- DIMENSION docs & tutorials
- HATCH tutorial with islands
- MTEXT tutorial
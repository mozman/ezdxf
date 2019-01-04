TODO
====

Python Code
-----------

- caching for entity creation
    - options for enable/disable caching
    - cache all for max performance
    - cache some to balance performance/memory usage
    - cache none for least memory usage
- CORRECT entity copy
    - copy table entries: BLOCK_RECORD, STYLE, DIMSTYLE, LINETYPE, LAYER, VPORT
    - copy DXF entities including attached data (extension dict, ...)
    - copy DXF objects !!!pointer handling!!!
    - copy BLOCK: BLOCK_RECORD, Entities
    - copy layout
        - copy BLOCK, BLOCK_RECORD, LAYOUT
        - not possible for model space
        - no converting paper space -> model space, this is a rendering task for CAD applications
- optimized Vector class, SVec for simple or speedy vector? profiling required!!!

DXF Entities
------------

- DIMENSION rendering
    - aligned dim
    - rotated dim
    - angular dim
    - diameter dim
    - radius dim
    - angular 3 point dim
    - ordinate dim
- LEADER rendering
- MLEADER rendering ???
- MLINE rendering ???

DXF Audit & Cleanup
-------------------

- check ownership
    - DXF objects in OBJECTS section
    - DXF Entities in a layout (model space, paper space, block)
- check required DXF attributes:
    - R12: layer; cleanup: set to '0' (in ezdxf defaults to '0')
    - R2000+: layer, owner?, handle?
- check required subclasses
- VERTEX on same layer as POLYLINE; cleanup: set VERTEX layer to POLYLINE layer
- find unreferenced objects:
    - DICTIONARY e.g. orphaned extension dicts; cleanup: delete
- find unused BLOCK definitions: has no corresponding INSERT (except layout blocks); cleanup: delete

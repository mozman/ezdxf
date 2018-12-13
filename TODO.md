TODO
====

Python Code
-----------

- type annotations
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


DXF Entities
------------

- dim line rendering

DXF Audit
---------

- check ownership
    - DXF objects in OBJECTS section
    - DXF Entities in a layout (model space, paper space, block)
- VERTEX on same layer as POLYLINE
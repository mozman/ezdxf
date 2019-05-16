TODO
====

Python Code
-----------

- new entity system (NES) in V0.10 (work in progress): the layer between low level DXF and user API will be replaced
- the NES enables to save the drawing in any DXF version you want, but data loss, if you save a older DXF version than 
  loaded (ezdxf will not be a DXF converted), so it is intended for upgrading not for downgrading of DXF drawings.
- correct entity copy is a design goal for the NES
    - copy table entries: BLOCK_RECORD, STYLE, DIMSTYLE, LINETYPE, LAYER, VPORT
    - copy DXF entities including attached data (extension dict, ...)
    - copy DXF objects !!!pointer handling!!!
    - copy BLOCK: BLOCK_RECORD, Entities
    - copy layout: including BLOCK, BLOCK_RECORD, LAYOUT
    - no converting paperspace -> model space, this is a rendering task for CAD applications       
- import data from DXF files is also a design goal for the NES, API design already in v0.10, implementation in v0.11
    - import table entries
    - import entities including extended data and resources in the objects section
    - import layouts (modelspace, paperspace and blocks)
- simple & limited transformation API for translate, scale, rotate, API design already in v0.10, 
  implementation in v.11 or later
- optimized Vector class, SVec for simple or speedy vectors? profiling required!!!

DXF Entities
------------

- DIMENSION rendering
    - aligned & rotated dim, implemented in v0.9 (linear dimension)
    - angular dim, planned for v0.11 or later
    - diameter dim, planned for v0.11 or later
    - radius dim, planned for v0.11 or later
    - angular 3 point dim, planned for v0.11 or later
    - ordinate dim, planned for v0.11 or later
- LEADER rendering, planned
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

TODO
====

## Loading strategies

Remove the "legacy mode" in regular read and readfile function, use recover 
functions instead. Using a separated recover mode can help to optimize the 
loading process for well formed DXF files, malformed DXF files will raise 
a DXFStructureError. 

The recover process is __much slower__ than the loading process for well 
formed DXF files.

Some loading scenarios as examples:

### 1. It will work

Mostly DXF files from AutoCAD or BricsCAD (e.g. for In-house solutions)

```
try:
    doc = ezdxf.readfile(name)  
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file: {name}.')
```
    
### 2. Try Hard 

From trusted and untrusted sources but with good hopes, the worst case works 
like a cache miss, you pay for the first try and pay the extra fee for the 
recover mode:

```
try:  # fast path:
    doc = ezdxf.readfile(name)  
except ezdxf.DXFStructureError:
    try:  # slow path with low level structure repair:
        doc, auditor = ezdxf.recover.auto_readfile(name)
        if auditor.has_errors:
            print(f'Found unrecoverable errors in DXF file: {name}.')
            auditor.print_error_report()
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {name}.')
```
        
### 3. Just pay the extra fee

Untrusted sources and expecting many invalid DXF files, you always pay an 
extra fee for the recover mode:

```
try:  # low level structure repair:
    doc, auditor = ezdxf.recover.auto_readfile(name)
    if auditor.has_errors:
        print(f'Found unrecoverable errors in DXF file: {name}.')
        auditor.print_error_report()
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file: {name}.')

```

   
Add-ons
-------

- DWG loader (work in progress)
- Simple SVG exporter
- drawing
    - ACAD_TABLE
    - MLEADER ???
    - MLINE ???
    - render POINT symbols
    - render proxy graphic, class `ProxyGraphic()` is already 
      implemented but not tested with real world data.
         

Render Tools
------------

- `ACADTable.virtual_entities()`
- `MLeader.virtual_entities()` ???
- `MLine.virtual_entities()` ???
- LWPOLYLINE and 2D POLYLINE the `virtual_entities(dxftype='ARC')` method
  could return bulges as ARC, ELLIPSE or SPLINE entities
  

DXF Entities
------------

- DIMENSION rendering
    - angular dim
    - angular 3 point dim
    - ordinate dim
    - arc dim
- MLEADER
- MLINE
- FIELD
- ACAD_TABLE

- Blocks.purge() search for non-explicit block references in:
    - All arrows in DIMENSION are no problem, there has to be an explicit 
      INSERT for each used arrow in the associated geometry block.
    - user defined arrow blocks in LEADER, MLEADER
    - LEADER override: 'dimldrblk_handle'
    - MLEADER: block content
    - ACAD_TABLE: block content


DXF Audit & Repair
------------------

- check DIMENSION
    - dimstyle exist; repair: set to 'Standard'
    - arrows exist; repair: set to '' = default open filled arrow
    - text style exist; repair: set to 'Standard'
- check TEXT, MTEXT
    - text style exist; repair: set to 'Standard'


Cython Code
-----------

- optional for install, testing and development
- profiling required!!!
- optimized Vec2(), Vector() and Matrix44() classes
- optimized math & construction tools
- optimized tag loader

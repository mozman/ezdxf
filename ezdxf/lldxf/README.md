Low level DXF Handlers
======================

At the very base a DXF-file is an ASCII file containing loads of (group code, value) pairs, group code describes the
type of the value (see TYPE_TABLE in types.py).

The following specifies a line on layer 2 of index color number 4 from (1, 1, 0) to (-1, -1, -1):

```
0
LINE
8
2
62
4
10
1
20
1
30
0
11
-1
21
-1
31
-1
```

On the lowest level, those keys/values are stored as "DXFTag" objects:

```
[
    (code=0, value="LINE"),
    (code=8, value=2),
    (code=62, value=4),
    (code=10, value=1),
    (code=20, value=1),
    ...
]
```

There are Conventions for allowed values depending on the code which can be found at the
[official Autodesk dxf specification](http://www.autodesk.com/techpubs/autocad/acadr14/dxf/group_code_ranges_al_u05_c.htm)


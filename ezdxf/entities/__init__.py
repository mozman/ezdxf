# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# Unified Entity System (UES) with unified DXF attribute system for DXF R12 and DXF R2000+
# ========================================================================================
#
# 1. Store entities as DXFEntity () or inherited instances in the drawing database
# 2. remove separation of legacy and modern tag structures
#    - uses owner tag of DXF R2000+ also for DXF R12
#    - same layout structures (BLOCK_RECORDS, LAYOUT, OBJECTS section)
#    - just don't export DXF R2000+ structures to DXF R12 files
# 3. still store unknown entities (Map3d...) as bunch of tag, but inside of an special DXFEntity (DXFTagStorage)
# 4. preserve actual DXFEntity interface, DXFEntity.dxf seem still a good idea - other methods deprecate slowly
# 5. use individual DXF export functions for each entity, but provide a useful boiler plate

# first factory
from . import factory

# register management structures
from . import dxfclass, table

# register table entries
from . import ltype, layer, textstyle, dimstyle, view, vport, ucs, appid, blockrecord

# register DXF objects R2000
from . import dxfobj, dictionary, layout, idbuffer, sun

# register DXF objects R2007
from . import visualstyle

# register entities R12
from . import dxfgfx
from . import line, point, circle, arc, shape, solid, text, insert, block, polyline, attrib, dimension, viewport

# register graphical entities R2000
from . import lwpolyline, ellipse, xline, mtext, spline, mesh, hatch, image, underlay, acis, helix, leader, tolerance

# register graphical entities R2004

# register graphical entities R2007

from . import light

# register graphical entities R2010

from . import geodata

# register graphical entities R2013

# register graphical entities R2018


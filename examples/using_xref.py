# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import ezdxf

# AutoCAD 2010 can not resolve XREFS in DXF R12 Format :-(,
ref_dwg = ezdxf.new('R2000')
ref_dwg.modelspace().add_circle(center=(5, 5), radius=2.5)
ref_dwg.header['$INSBASE'] = (5, 5, 0)  # set insertion point
ref_dwg.saveas("xref_drawing.dxf")

# XREF definition
host_dwg = ezdxf.new('R2000')
host_dwg.add_xref_def(filename='xref_drawing.dxf', name='my_xref')
host_dwg.modelspace().add_blockref(name='my_xref', insert=(0, 0))
host_dwg.saveas("using_xref.dxf")

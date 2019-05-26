# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import ezdxf

# AutoCAD 2010 can not resolve XREFS in DXF R12 Format :-(,
ref_doc = ezdxf.new('R2000')
ref_doc.modelspace().add_circle(center=(5, 5), radius=2.5)
ref_doc.header['$INSBASE'] = (5, 5, 0)  # set insertion point
ref_doc.saveas("xref_drawing.dxf")

# XREF definition
host_doc = ezdxf.new('R2000')
host_doc.add_xref_def(filename='xref_drawing.dxf', name='my_xref')
host_doc.modelspace().add_blockref(name='my_xref', insert=(0, 0))
host_doc.saveas("using_xref.dxf")

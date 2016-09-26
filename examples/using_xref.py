import ezdxf
from ezdxf.lldxf import const


# AutoCAD 2010 can not resolve XREFS in DXF R12 Format :-(,
ref_dwg = ezdxf.new('AC1015')
ref_dwg.modelspace().add_circle(center=(5, 5), radius=2.5)
ref_dwg.saveas("xref_drawing.dxf")

# XREF definition
host_dwg = ezdxf.new('AC1015')
xref_def = host_dwg.blocks.new(name='my_xref', dxfattribs={
    'flags': const.BLK_XREF,
    'xref_path': 'xref_drawing.dxf'
})

host_dwg.modelspace().add_blockref(name='my_xref', insert=(0, 0))
host_dwg.saveas("using_xref.dxf")

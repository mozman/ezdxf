import ezdxf
from ezdxf.lldxf import const

#  Trying to have an hatch with hole.

name = 'test_hatch_hole.dxf'

dwg = ezdxf.new('AC1015')  # hatch requires the DXF R2000 (AC1015) format or later
msp = dwg.modelspace()  # adding entities to the model space

dwg.layers.new('HATCH',  dxfattribs={'linetype': 'Continuous', 'color': 8})

hatch = msp.add_hatch(color=1, dxfattribs={'layer': 'HATCH'})

with hatch.edit_boundary() as boundary: 
    # every boundary path is always a 2D element
    boundary.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)], is_closed=1, flags=const.BOUNDARY_PATH_EXTERNAL)
    boundary.add_polyline_path([(3, 3), (7, 3), (7, 7), (3, 7)], is_closed=1, flags=const.BOUNDARY_PATH_OUTERMOST)  # hole

dwg.saveas(name)

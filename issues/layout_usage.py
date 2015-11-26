import ezdxf

dwg = ezdxf.new('AC1027')
msp = dwg.modelspace()

dwg.create_layout("layoutA")
dwg.create_layout("layoutB")

layoutA = dwg.layout("layoutA")
# layoutA.add_viewport(center=(2.5, 2.5), size=(5, 5), view_center_point=(0, 1), view_height=0.5)
layoutA.add_line((0, 0), (3, 3), dxfattribs={'color': 2})

layoutB = dwg.layout("layoutB")
# layoutB.add_viewport(center=(2.5, 7.5), size=(5, 5), view_center_point=(1, 1), view_height=0.5)
layoutB.add_line((0, 1), (3, 4), dxfattribs={'color': 3})

msp.add_lwpolyline([(0, 0), (0, 1), (1, 1), (1, 0)])

dwg.saveas("multiple_layouts.dxf")
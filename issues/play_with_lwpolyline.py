import ezdxf

dwg = ezdxf.new('R2000')
msp = dwg.modelspace()
msp.add_lwpolyline(points=[(0., 0., 0, 0, 1.), (2., 0, 0, 0, 1.333333)], dxfattribs={'color': 2, 'closed': True})
msp.add_lwpolyline(points=[(0., 3., 0, 0, 1.), (2., 3.)], dxfattribs={'color': 3})

dwg.saveas('play_with_lwpolyline.dxf')
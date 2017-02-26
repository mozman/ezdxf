import ezdxf

move = (100.0, 100.0)
source = 'issue6.dxf'
target = 'issue6copy.dxf'

src = ezdxf.readfile(source)
dxf = ezdxf.new(src.dxfversion)
lay = dxf.layers.get('0')
lay.set_color(2)
target_msp = dxf.modelspace()
source_msp = src.modelspace()

for e in source_msp.query('LWPOLYLINE'):
    newPoints = []
    mx, my = move
    # get_points() returns  (x, y, start_width, end_width, bulge)
    for p in e.get_points():
        # you have to copy start- and end width and the bulge values
        x, y, start_width, end_width, bulge = p
        newPoints.append((x+mx, y+my, start_width, end_width, bulge))
    poly = target_msp.add_lwpolyline(newPoints, dxfattribs={
        'layer': e.dxf.layer,
        'flags': e.dxf.flags
    })
    poly.closed = e.closed

dxf.saveas(target)

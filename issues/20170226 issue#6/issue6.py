import ezdxf

move = (100.0, 100.0)
source = 'issue6.dxf'
target = 'issue6copy.dxf'

src = ezdxf.readfile(source)
source_msp = src.modelspace()

dxf = ezdxf.new(src.dxfversion)
target_msp = dxf.modelspace()

for e in source_msp.query('LWPOLYLINE'):
    # you have to copy start- and end width and the bulge values
    def move_point(point):
        x, y, start_width, end_width, bulge = point
        return x+mx, y+my, start_width, end_width, bulge

    mx, my = move
    # get_points() returns  (x, y, start_width, end_width, bulge)
    target_msp.add_lwpolyline((move_point(p) for p in e.get_points()), dxfattribs={
        'layer': e.dxf.layer,
        'flags': e.dxf.flags,
        'closed': e.closed,  # not a real DXF attribute, but it works ;)
    })


dxf.saveas(target)

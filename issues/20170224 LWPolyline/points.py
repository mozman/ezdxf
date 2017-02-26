from pprint import pprint
import ezdxf   # using 0.7.9

dwg = ezdxf.readfile("draw.dxf")

modelspace = dwg.modelspace()

# model space contains no LWPOLYLINE entities
# just one block reference named '835Z1187-114_P1_FC&R-&C'
# query the block reference - take the first, because there is just one block reference
blockref = modelspace.query('INSERT')[0]
# get the block definition
block = dwg.blocks.get(blockref.dxf.name)
# block behaves like any other layout object (modelspace)

for num, line in enumerate(block.query('LWPOLYLINE'), start=1):
    print("\n{}. POLYLINE:".format(num))
    with line.points() as points:
        pprint(points)
        # points is a list of tuples (x, y, start_width, end_width, bulge)
        # you can add and remove points in this list, and the associated LWPOLYLINE will be updated
        # add a point: points.append((x, y, 0, 0, 0))
        # remove some points: del points[2:4]
        # change a point: points[3] = (x, y, 0, 0, 0)



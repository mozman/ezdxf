import ezdxf
import random


def get_random_point():
    """Creates random x, y coordinates."""
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return x, y


dwg = ezdxf.new('R2010')
flag = dwg.blocks.new(name='FLAG')
flag.add_polyline2d([(0, 0), (0, 5), (4, 3), (0, 3)])
flag.add_circle((0, 0), .4, dxfattribs={'color': 2})

msp = dwg.modelspace()


for _ in range(50):
    msp.add_blockref(name='FLAG', insert=get_random_point())

q = msp.query('INSERT')
entity = q[0]

query = ezdxf.query.new()
query.extend([entity])

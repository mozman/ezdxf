import ezdxf
from ezdxf.tools.standards import linetypes

data = {'circles': [[5, [13, 2]], [19, [15, 15]], [19, [12, 4]], [8, [8, 13]],
                    [3, [29, 29]], [2, [8, 11]], [1, [2, 6]]],
        'lines': [[[12, 18], [3, 2], 'CONTINUOUS', 'B'],
                  [[29, 4], [18, 15], 'DASHED', 'A'],
                  [[5, 24], [10, 16], 'DASHED', 'A'],
                  [[8, 20], [21, 23], 'HIDDEN', 'B'],
                  [[7, 28], [5, 25], 'CONTINUOUS', 'B'],
                  [[3, 14], [4, 29], 'CONTINUOUS', 'A'],
                  [[11, 16], [13, 3], 'DOT', 'A']]}
# line format [x_start, x_end], [y_start, y_end], style, layer

dwg = ezdxf.new('AC1015')  # Version necessary for saving images
for name, desc, pattern in linetypes():
    try:
        dwg.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern':pattern})
    except ValueError:
        pass  # ignore already existing line types

print('available line types:')
for linetype in dwg.linetypes:
    print(linetype.dxf.name)

msp = dwg.modelspace()
layout = dwg.layout()


dwg.layers.new(name='CIRCLES', dxfattribs={'linetype': 'DASHED', 'color': 5})
dwg.layers.new(name='A', dxfattribs={'color': 5})
dwg.layers.new(name='B', dxfattribs={'color': 5})
dwg.layers.new(name='C', dxfattribs={'color': 5})

# WRITE
for circle in data['circles']:
    r = circle[0]
    center = tuple(circle[1])
    msp.add_circle(center, r, dxfattribs={'layer': 'CIRCLE'})

for line in data['lines']:
    line_strt = (line[0][0], line[1][0])
    line_end = (line[0][1], line[1][1])
    print(line_strt, line_end)
    msp.add_line(line_strt, line_end, dxfattribs={'linetype': line[2],
                                                  'layer': line[3]})

dwg.saveas('issue08.dxf')

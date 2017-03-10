import ezdxf
from ezdxf.tools.standards import linetypes

data = {
    'circles': (
        (5, (13, 2)),
        (19, (15, 15)),
        (19, (12, 4)),
        (8, (8, 13)),
        (3, (29, 29)),
        (2, (8, 11)),
        (1, (2, 6)),
    ),
    'lines': (
        ((12, 3), (18, 2), 'CONTINUOUS', 'B'),
        ((29, 18), (4, 15), 'DASHED', 'A'),
        ((5, 10), (24, 16), 'DASHED', 'A'),
        ((8, 21), (20, 23), 'HIDDEN', 'B'),
        ((7, 5), (28, 25), 'CONTINUOUS', 'B'),
        ((3, 4), (14, 29), 'CONTINUOUS', 'A'),
        ((11, 13), (16, 3), 'DOTTED', 'A'),
    ),
}

dwg = ezdxf.new('AC1027')  # Version necessary for saving images

for name, desc, pattern in linetypes():
    try:  # you can only create not existing line types
        dwg.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern': pattern})
    except ValueError:
        pass  # ignore already existing line types

# Define your own line types:
# dxf linetype definition
# name, description, elements:
# elements = [total_pattern_length, elem1, elem2, ...]
# total_pattern_length = sum(abs(elem))
# elem > 0 is line, < 0 is gap, 0.0 = dot;
my_line_types = [
    ("DOTTED", "Dotted .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .", [0.2, 0.0, -0.2]),
    ("DOTTEDX2", "Dotted (2x) .    .    .    .    .    .    .    . ", [0.4, 0.0, -0.4]),
    ("DOTTED2", "Dotted (.5) . . . . . . . . . . . . . . . . . . . ", [0.1, 0.0, -0.1]),
]
for name, desc, pattern in my_line_types:  # I know that DOTTED does not exist
    dwg.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern': pattern})


print('available line types:')
for linetype in dwg.linetypes:
    print(linetype.dxf.name)

msp = dwg.modelspace()

dwg.layers.new(name='CIRCLES', dxfattribs={'linetype': 'DASHED', 'color': 5})
dwg.layers.new(name='A', dxfattribs={'color': 5})
dwg.layers.new(name='B', dxfattribs={'color': 5})
dwg.layers.new(name='C', dxfattribs={'color': 5})

# WRITE
for r, center in data['circles']:
    msp.add_circle(center, r, dxfattribs={'layer': 'CIRCLE'})

for start, end, linetype, layer in data['lines']:
    msp.add_line(start, end, dxfattribs={'linetype': linetype, 'layer': layer})

result = dwg.audit()
if result:
    print('\nAudit found {} errors:'.format(len(result)))
    for err in result:
        e = err.dxf_entity
        if e is not None:
            print('{} in DXF entity {} with handle={}'.format(err.message, e.dxftype(), e.dxf.handle))
        else:
            print(err.message)

dwg.saveas('issue08.dxf')

import ezdxf

doc = ezdxf.new()
msp = doc.modelspace()

width = 40
height = 4

for i in range(26):
    c = chr(ord('a') + i)
    msp.add_mtext(f'{c}: abc^{c}def', {'insert': (0, -i * height, 0)})

for i in range(26):
    c = chr(ord('A') + i)
    msp.add_mtext(f'{c}: abc^{c}def', {'insert': (width, -i * height, 0)})

for i, c in enumerate(['?', '@', '[', ']', '\\', '_', ' ']):
    msp.add_mtext(f'{c}: abc^{c}def', {'insert': (2 * width, -i * height, 0)})

msp.add_mtext(f'^ : abc^^def', {'insert': (2 * width, -(i + 1) * height, 0)})
msp.add_mtext('^', {'insert': (2 * width, -(i + 2) * height, 0)})

doc.saveas('caret_encoding.dxf')


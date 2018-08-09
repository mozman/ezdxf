import ezdxf

dwg = ezdxf.readfile('mtext_2018.dxf')
msp = dwg.modelspace()

mtext = msp.query('MTEXT')[0]
mtext.set_text('Hello?')
dwg.saveas('mtext_2018_modified.dxf')


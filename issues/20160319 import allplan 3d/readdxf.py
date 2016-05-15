import ezdxf
ezdxf.options.compress_binary_data = True
dwg = ezdxf.readfile('104.dxf')
msp = dwg.modelspace()
print("Model spaces contains {} entities.".format(len(msp)))
polylines = msp.query('POLYLINE')


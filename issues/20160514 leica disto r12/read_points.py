import ezdxf

dwg = ezdxf.readfile("Leica_Disto_S910.dxf")
msp = dwg.modelspace()
for num, point in enumerate(msp.query('POINT')):
    print("#{num}: {location}".format(num=num, location=point.dxf.location))

dwg.saveas("Leica_Disto_S910_ezdxf.dxf")

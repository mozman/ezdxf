import ezdxf


FILENAME = 'x0292430_c.dxf'


def analyse_dxffile(dxffile):
    dwg = ezdxf.readfile(dxffile)
    modelspace = dwg.modelspace()
    for n, e in enumerate(modelspace.query('ELLIPSE')):
        print("\n----- Ellipse #{} -----".format(n+1))
        print("center: {}".format(e.dxf.center))
        print("major_axis: {}".format(e.dxf.major_axis))
        print("ratio: {}".format(e.dxf.ratio))
        print("start_param: {}".format(e.dxf.start_param))
        print("end_param: {}".format(e.dxf.end_param))


analyse_dxffile(FILENAME)


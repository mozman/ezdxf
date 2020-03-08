import ezdxf

dwg = ezdxf.readfile('perfil_77_curve.dxf')
msp = dwg.modelspace()

lwpolylines = msp.query('LWPOLYLINE')
print('Found {} LWPOLYLINE entities.'.format(len(lwpolylines)))

splines = msp.query('SPLINE')
print('Found {} SPLINE entities.'.format(len(splines)))


for spline in splines:
    print(str(spline))
    print("control points: {}".format(spline.dxf.n_control_points))
    print("fit points: {}".format(spline.dxf.n_fit_points))
    print('-'*40 + '\n')

# collect all control points
all_control_points = []
for spline in splines:
    all_control_points.extend(spline.get_control_points())

print('Found {} control points overall.'.format(len(all_control_points)))
print('First: {}'.format(all_control_points[0]))
print('Last: {}'.format(all_control_points[-1]))

# add LWPOLYLINE to existing doc
# remove z axis
points2d = [point[:2] for point in all_control_points]
msp.add_lwpolyline(points=points2d, dxfattribs={'color': 1, 'layer': 'LWPOLYLINE'})
dwg.saveas('perfil_77_curve_with_lwpolyline.dxf')


# create new doc with LWPOLYLINE
dwg2 = ezdxf.new('R2010')
msp2 = dwg2.modelspace()
msp2.add_lwpolyline(points=points2d, dxfattribs={'color': 2, 'layer': 'LWPOLYLINE'})
dwg2.saveas('perfil_77_lwpolyline.dxf')


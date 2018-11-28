# Purpose: open example files with big polyface models
# Created: 23.04.2014
# Copyright (c) 2014, Manfred Moitzi
# License: MIT License
import ezdxf
import time


def optimize_polyfaces(polyfaces):
    count = 0
    runtime = 0
    vertex_diff = 0
    print("start optimizing...")
    for polyface in polyfaces:
        count += 1
        start_vertex_count = len(polyface)
        start_time = time.time()
        polyface.optimize()
        end_time = time.time()
        end_vertex_count = len(polyface)
        runtime += end_time - start_time
        vertex_diff += start_vertex_count - end_vertex_count
    print("removed {vd} vertices in {rt:.2f} seconds.".format(rt=runtime, vd=vertex_diff))


def optimize(filename, new_filename):
    print('opening DXF file: {}'.format(filename))
    start_time = time.time()
    dwg = ezdxf.readfile(filename)
    end_time = time.time()
    print('time for reading: {:.1f} seconds'.format(end_time - start_time))
    print("DXF version: {}".format(dwg.dxfversion))
    print("Database contains {} entities.".format(len(dwg.entitydb)))
    polyfaces = (polyline for polyline in dwg.entities.query('POLYLINE') if polyline.is_poly_face_mesh)
    optimize_polyfaces(polyfaces)

    print('saving DXF file: {}'.format(new_filename))
    start_time = time.time()
    dwg.saveas(new_filename)
    end_time = time.time()
    print('time for saving: {:.1f} seconds'.format(end_time - start_time))

if __name__ == '__main__':
    optimize(r'D:\Source\dxftest\fanuc-430-arm.dxf', r'D:\Source\dxftest\fanuc-430-arm-optimized.dxf')
    optimize(r'D:\Source\dxftest\cnc machine.dxf', r'D:\Source\dxftest\cnc machine-optimized.dxf')

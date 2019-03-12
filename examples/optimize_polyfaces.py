# Purpose: open example files with big polyface models
# Created: 23.04.2014
# Copyright (c) 2014-2019, Manfred Moitzi
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
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    end_time = time.time()
    print('time for reading: {:.1f} seconds'.format(end_time - start_time))
    print("DXF version: {}".format(doc.dxfversion))
    print("Database contains {} entities.".format(len(doc.entitydb)))
    polyfaces = (polyline for polyline in msp.query('POLYLINE') if polyline.is_poly_face_mesh)
    optimize_polyfaces(polyfaces)

    print('saving DXF file: {}'.format(new_filename))
    start_time = time.time()
    doc.saveas(new_filename)
    end_time = time.time()
    print('time for saving: {:.1f} seconds'.format(end_time - start_time))


if __name__ == '__main__':
    optimize(r'D:\Source\dxftest\CADKitSamples\fanuc-430-arm.dxf', r'C:\Users\manfred\Desktop\Outbox\fanuc-430-arm-optimized.dxf')
    optimize(r'D:\Source\dxftest\CADKitSamples\cnc machine.dxf', r'C:\Users\manfred\Desktop\Outbox\cnc machine-optimized.dxf')

# New entity system
# D:\Source\ezdxf-new-entity-system\venv\Scripts\python.exe D:/Source/ezdxf-new-entity-system/examples/optimize_polyfaces.py
# opening DXF file: D:\Source\dxftest\CADKitSamples\fanuc-430-arm.dxf
# time for reading: 22.7 seconds
# DXF version: AC1018
# Database contains 193284 entities.
# start optimizing...
# removed 31538 vertices in 3.84 seconds.
# saving DXF file: C:\Users\manfred\Desktop\Outbox\fanuc-430-arm-optimized.dxf
# time for saving: 16.3 seconds
# opening DXF file: D:\Source\dxftest\CADKitSamples\cnc machine.dxf
# time for reading: 18.5 seconds
# DXF version: AC1018
# Database contains 152600 entities.
# start optimizing...
# removed 35174 vertices in 3.72 seconds.
# saving DXF file: C:\Users\manfred\Desktop\Outbox\cnc machine-optimized.dxf
# time for saving: 12.1 seconds

# Old entity system
# D:\Source\ezdxf-new-entity-system\venv\Scripts\python.exe D:/Source/ezdxf-new-entity-system/examples/optimize_polyfaces.py
# opening DXF file: D:\Source\dxftest\CADKitSamples\fanuc-430-arm.dxf
# time for reading: 14.6 seconds
# DXF version: AC1018
# Database contains 193275 entities.
# start optimizing...
# removed 31538 vertices in 9.67 seconds.
# saving DXF file: C:\Users\manfred\Desktop\Outbox\fanuc-430-arm-optimized.dxf
# time for saving: 6.0 seconds
# opening DXF file: D:\Source\dxftest\CADKitSamples\cnc machine.dxf
# time for reading: 12.3 seconds
# DXF version: AC1018
# Database contains 152591 entities.
# start optimizing...
# removed 35174 vertices in 8.51 seconds.
# saving DXF file: C:\Users\manfred\Desktop\Outbox\cnc machine-optimized.dxf
# time for saving: 4.5 seconds

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
    print(f"removed {vertex_diff} vertices in {runtime:.2f} seconds.")


def optimize(filename, new_filename):
    print(f'opening DXF file: {filename}')
    start_time = time.time()
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    end_time = time.time()
    print(f'time for reading: {end_time - start_time:.1f} seconds')
    print(f"DXF version: {doc.dxfversion}")
    print(f"Database contains {len(doc.entitydb)} entities.")
    polyfaces = (polyline for polyline in msp.query('POLYLINE') if polyline.is_poly_face_mesh)
    optimize_polyfaces(polyfaces)

    print(f'saving DXF file: {new_filename}')
    start_time = time.time()
    doc.saveas(new_filename)
    end_time = time.time()
    print(f'time for saving: {end_time - start_time:.1f} seconds')


if __name__ == '__main__':
    optimize(r'D:\Source\dxftest\CADKitSamples\fanuc-430-arm.dxf', r'C:\Users\manfred\Desktop\Outbox\fanuc-430-arm-optimized.dxf')
    optimize(r'D:\Source\dxftest\CADKitSamples\cnc machine.dxf', r'C:\Users\manfred\Desktop\Outbox\cnc machine-optimized.dxf')

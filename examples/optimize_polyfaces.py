# Purpose: open example files with big polyface models
# Copyright (c) 2014-2021, Manfred Moitzi
# License: MIT License
import time
import pathlib

import ezdxf
from ezdxf.render import MeshVertexMerger

SRCDIR = pathlib.Path(ezdxf.EZDXF_TEST_FILES) / "CADKitSamples"
OUTDIR = pathlib.Path('~/Desktop/Outbox').expanduser()


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


def optimize(name: str):
    filename = SRCDIR / name
    new_filename = OUTDIR / ('optimized_' + name)
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


def save_as(name):
    filename = SRCDIR / name

    print(f'opening DXF file: {filename}')
    start_time = time.time()
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    end_time = time.time()
    print(f'time for reading: {end_time - start_time:.1f} seconds')
    print(f"DXF version: {doc.dxfversion}")
    print(f"Database contains {len(doc.entitydb)} entities.")
    polyfaces = (polyline for polyline in msp.query('POLYLINE') if polyline.is_poly_face_mesh)

    # create a new documents
    doc1 = ezdxf.new()
    msp1 = doc1.modelspace()
    doc2 = ezdxf.new()
    msp2 = doc2.modelspace()
    for polyface in polyfaces:
        b = MeshVertexMerger.from_polyface(polyface)
        b.render_mesh(msp1, dxfattribs={
            'layer': polyface.dxf.layer,
            'color': polyface.dxf.color,
        })
        b.render_polyface(msp2, dxfattribs={
            'layer': polyface.dxf.layer,
            'color': polyface.dxf.color,
        })

    new_filename = OUTDIR / ('mesh_' + name)
    print(f'saving as mesh DXF file: {new_filename}')
    start_time = time.time()
    doc1.saveas(new_filename)
    end_time = time.time()
    print(f'time for saving: {end_time - start_time:.1f} seconds')

    new_filename = OUTDIR / ('recreated_polyface_' + name)
    print(f'saving as polyface DXF file: {new_filename}')
    start_time = time.time()
    doc2.saveas(new_filename)
    end_time = time.time()
    print(f'time for saving: {end_time - start_time:.1f} seconds')


if __name__ == '__main__':
    optimize('fanuc-430-arm.dxf')
    optimize('cnc machine.dxf')
    save_as('fanuc-430-arm.dxf')
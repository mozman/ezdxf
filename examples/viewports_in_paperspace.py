# Purpose: viewports in paperspace
# Created: 11.10.2015
# Copyright (c) 2015, Manfred Moitzi
# License: MIT License
import math
import ezdxf

MESH_SIZE = 20


def build_cos_sin_mesh(mesh):
    height = 3.
    dx = 30
    dy = 30

    delta = math.pi / MESH_SIZE
    for x in range(MESH_SIZE):
        sinx = math.sin(float(x) * delta)
        for y in range(MESH_SIZE):
            cosy = math.cos(float(y) * delta)
            z = sinx * cosy * height
            # set the m,n vertex to 3d point x,y,z
            mesh.set_mesh_vertex((x, y), (dx + x, dy + y, z))


def create_2d_modelspace_content(layout):
    rect = layout.add_polyline2d([(5, 5), (10, 5), (10, 10), (5, 10)], dxfattribs={'color': 2})
    rect.close(True)

    layout.add_circle((10, 5), 2.5, dxfattribs={'color': 3})

    triangle = layout.add_polyline2d([(10, 7.5), (15, 5), (15, 10)], dxfattribs={'color': 4})
    triangle.close(True)


def create_3d_modelspace_content(modelspace):
    mesh = modelspace.add_polymesh((MESH_SIZE, MESH_SIZE), dxfattribs={'color': 6})
    build_cos_sin_mesh(mesh)


def create_viewports(paperspace, dxfversion):
    # Define viewports in paper space:
    # center, size=(width, height) defines the viewport in paper space.
    # view_center_point and view_height defines the area in model space
    # which is displayed in the viewport.
    paperspace.add_viewport(center=(2.5, 2.5), size=(5, 5), view_center_point=(7.5, 7.5), view_height=10)
    # scale is calculated by: height of model space (view_height=10) / height of viewport (height=5)
    paperspace.add_text("View of Rectangle Scale=1:2", dxfattribs={
        'insert': (0, 5.2),
        'height': 0.18,
        'color': 1,
    })

    paperspace.add_viewport(center=(8.5, 2.5), size=(5, 5), view_center_point=(10, 5), view_height=25)
    paperspace.add_text("View of Circle Scale=1:5", dxfattribs={
        'insert': (6, 5.2),
        'height': 0.18,
        'color': 1,
    })

    paperspace.add_viewport(center=(14.5, 2.5), size=(5, 5), view_center_point=(12.5, 7.5), view_height=5)
    paperspace.add_text("View of Triangle Scale=1:1", dxfattribs={
        'insert': (12, 5.2),
        'height': 0.18,
        'color': 1,
    })

    paperspace.add_viewport(center=(7.5, 10), size=(15, 7.5), view_center_point=(10, 6.25), view_height=7.5)
    paperspace.add_text("Overall View Scale=1:1", dxfattribs={
        'insert': (0, 14),
        'height': 0.18,
        'color': 1
    })

    paperspace.add_viewport(center=(16, 13.5), size=(0.3, 0.15), view_center_point=(10, 6.25), view_height=7.5)
    # scale = 7.5/0.15 = 50
    paperspace.add_text("Scale=1:50", dxfattribs={
        'height': 0.18,
        'color': 1,
    }).set_pos((16, 14), align='CENTER')

    vp = paperspace.add_viewport(center=(16, 10), size=(4, 4), view_center_point=(0, 0), view_height=30)
    vp.dxf.view_target_point = (40, 40, 0)
    vp.dxf.view_direction_vector = (-1, -1, 1)

    paperspace.add_text("Viewport to 3D Mesh", dxfattribs={
        'height': 0.18,
        'color': 1
    }).set_pos((16, 12.5), align='CENTER')


def main():
    def make(dxfversion, filename):
        dwg = ezdxf.new2(dxfversion)
        if 'VIEWPORTS' not in dwg.layers:
            vp_layer = dwg.layers.new('VIEWPORTS')
        else:
            vp_layer = dwg.layers.get('VIEWPORTS')
        # switch viewport layer off to hide the viewport border lines
        vp_layer.off()

        create_2d_modelspace_content(dwg.modelspace())
        create_3d_modelspace_content(dwg.modelspace())
        # IMPORTANT: DXF R12 supports only one paper space aka layout, every layout name returns the same layout
        layout = dwg.layout('Layout1')  # default layout
        layout.page_setup(size=(22, 17), margins=(1, 1, 1, 1), units='inch')
        create_viewports(layout, dxfversion)

        try:
            dwg.saveas(filename)
        except IOError:
            print("Can't write: '%s'" % filename)

    make('AC1009', 'viewports_in_paperspace_R12.dxf')
    make('AC1015', 'viewports_in_paperspace_R2000.dxf')
    make('AC1021', 'viewports_in_paperspace_R2007.dxf')


if __name__ == '__main__':
    main()

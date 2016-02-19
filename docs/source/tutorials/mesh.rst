.. _tut_mesh:

Tutorial for Mesh
=================

Create a simple mesh::

    import ezdxf

    dwg = ezdxf.new('AC1015')  # mesh requires the DXF 2000 or newer format

    # 8 corner vertices
    cube_vertices = [
        (0, 0, 0),
        (1, 0, 0),
        (1, 1, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 0, 1),
        (1, 1, 1),
        (0, 1, 1),
    ]

    # 6 cube faces
    cube_faces = [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [3, 2, 6, 7],
        [0, 3, 7, 4]
    ]

    msp = dwg.modelspace()
    mesh = msp.add_mesh()
    mesh.dxf.subdivision_levels = 0  # do not subdivide cube
    with mesh.edit_data() as mesh_data:
        mesh_data.vertices = cube_vertices
        mesh_data.faces = cube_faces

    dwg.saveas("cube_mesh.dxf")


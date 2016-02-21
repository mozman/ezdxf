.. _tut_mesh:

Tutorial for Mesh
=================

Create a cube mesh by direct access to base data structures::

    import ezdxf


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

    dwg = ezdxf.new('AC1015')  # mesh requires the DXF 2000 or newer format
    msp = dwg.modelspace()
    mesh = msp.add_mesh()
    mesh.dxf.subdivision_levels = 0  # do not subdivide cube, 0 is the default value
    with mesh.edit_data() as mesh_data:
        mesh_data.vertices = cube_vertices
        mesh_data.faces = cube_faces

    dwg.saveas("cube_mesh_1.dxf")

Create a cube mesh by method calls::

    import ezdxf


    # 8 corner vertices
    p = [
        (0, 0, 0),
        (1, 0, 0),
        (1, 1, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 0, 1),
        (1, 1, 1),
        (0, 1, 1),
    ]

    dwg = ezdxf.new('AC1015')  # mesh requires the DXF 2000 or newer format
    msp = dwg.modelspace()
    mesh = msp.add_mesh()

    with mesh.edit_data() as mesh_data:
        mesh_data.add_face([p[0], p[1], p[2], p[3]])
        mesh_data.add_face([p[4], p[5], p[6], p[7]])
        mesh_data.add_face([p[0], p[1], p[5], p[4]])
        mesh_data.add_face([p[1], p[2], p[6], p[5]])
        mesh_data.add_face([p[3], p[2], p[6], p[7]])
        mesh_data.add_face([p[0], p[3], p[7], p[4]])
        mesh_data.optimize()  # optional, minimizes vertex count

    dwg.saveas("cube_mesh_2.dxf")

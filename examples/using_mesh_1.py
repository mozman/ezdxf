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

polygon5_vertices = [
    (0, 0, 0),
    (2, 0, 0),
    (2, 2, 0),
    (1, 3, 1),
    (0, 2, 0),
]

polygon5_face = [
    [0, 1, 2, 3, 4]
]

dwg = ezdxf.new('AC1015')  # mesh requires the DXF 2000 or newer format
msp = dwg.modelspace()
mesh = msp.add_mesh()
with mesh.edit_data() as mesh_data:
    mesh_data.vertices = cube_vertices
    mesh_data.faces = cube_faces

mesh5 = msp.add_mesh()
with mesh5.edit_data() as mesh_data:
    mesh_data.vertices = polygon5_vertices
    mesh_data.faces = polygon5_face

dwg.saveas("cube_mesh_1.dxf")

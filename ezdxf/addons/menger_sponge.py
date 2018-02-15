# Author:  mozman <me@mozman.at>
# Purpose: menger sponge addon for ezdxf
# module belongs to package ezdxf
# Created: 06.12.2016
# License: MIT License

all_cubes_size_3_template = [
    (0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 0), (1, 1, 0), (2, 1, 0), (0, 2, 0), (1, 2, 0), (2, 2, 0),
    (0, 0, 1), (1, 0, 1), (2, 0, 1), (0, 1, 1), (1, 1, 1), (2, 1, 1), (0, 2, 1), (1, 2, 1), (2, 2, 1),
    (0, 0, 2), (1, 0, 2), (2, 0, 2), (0, 1, 2), (1, 1, 2), (2, 1, 2), (0, 2, 2), (1, 2, 2), (2, 2, 2),
]

original_menger_cubes = [
    (0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 0), (2, 1, 0), (0, 2, 0), (1, 2, 0), (2, 2, 0),
    (0, 0, 1), (2, 0, 1), (0, 2, 1), (2, 2, 1),
    (0, 0, 2), (1, 0, 2), (2, 0, 2), (0, 1, 2), (2, 1, 2), (0, 2, 2), (1, 2, 2), (2, 2, 2),
]

menger_v1 = [
    (0, 0, 0), (2, 0, 0), (1, 1, 0), (0, 2, 0), (2, 2, 0),
    (1, 0, 1), (0, 1, 1), (2, 1, 1), (1, 2, 1),
    (0, 0, 2), (2, 0, 2), (1, 1, 2), (0, 2, 2), (2, 2, 2),
]

menger_v2 = [
    (1, 0, 0), (0, 1, 0), (2, 1, 0), (1, 2, 0),
    (0, 0, 1), (2, 0, 1), (1, 1, 1), (0, 2, 1), (2, 2, 1),
    (1, 0, 2), (0, 1, 2), (2, 1, 2), (1, 2, 2),
]

jerusalem_cube = [
    (0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0), (0, 1, 0), (1, 1, 0), (3, 1, 0), (4, 1, 0), (0, 2, 0),
    (4, 2, 0), (0, 3, 0), (1, 3, 0), (3, 3, 0), (4, 3, 0), (0, 4, 0), (1, 4, 0), (2, 4, 0), (3, 4, 0), (4, 4, 0),
    (0, 0, 1), (1, 0, 1), (3, 0, 1), (4, 0, 1), (0, 1, 1), (1, 1, 1), (3, 1, 1), (4, 1, 1), (0, 3, 1), (1, 3, 1),
    (3, 3, 1), (4, 3, 1), (0, 4, 1), (1, 4, 1), (3, 4, 1), (4, 4, 1), (0, 0, 2), (4, 0, 2), (0, 4, 2), (4, 4, 2),
    (0, 0, 3), (1, 0, 3), (3, 0, 3), (4, 0, 3), (0, 1, 3), (1, 1, 3), (3, 1, 3), (4, 1, 3), (0, 3, 3), (1, 3, 3),
    (3, 3, 3), (4, 3, 3), (0, 4, 3), (1, 4, 3), (3, 4, 3), (4, 4, 3), (0, 0, 4), (1, 0, 4), (2, 0, 4), (3, 0, 4),
    (4, 0, 4), (0, 1, 4), (1, 1, 4), (3, 1, 4), (4, 1, 4), (0, 2, 4), (4, 2, 4), (0, 3, 4), (1, 3, 4), (3, 3, 4),
    (4, 3, 4), (0, 4, 4), (1, 4, 4), (2, 4, 4), (3, 4, 4), (4, 4, 4),
]

building_schemas = [
    original_menger_cubes,
    menger_v1,
    menger_v2,
    jerusalem_cube,
]

# subdivide level in order of building_schemas
cube_sizes = [3., 3., 3., 5.]

# 8 corner vertices
_cube_vertices = [
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
    [0, 3, 2, 1],
    [4, 5, 6, 7],
    [0, 1, 5, 4],
    [1, 2, 6, 5],
    [3, 7, 6, 2],
    [0, 4, 7, 3],
]


class MengerSponge:
    def __init__(self, location=(0., 0., 0.), length=1., level=1, kind=0):
        self.cubes = _menger_sponge(location=location, length=length, level=level, kind=kind)

    def vertices(self):
        for location, length in self.cubes:
            x, y, z = location
            yield [(x + xf * length, y + yf * length, z + zf * length) for xf, yf, zf in _cube_vertices]
    __iter__ = vertices

    @staticmethod
    def faces():
        return cube_faces

    def render(self, layout, merge=False, dxfattribs=None):
        for vertices in self:  # iterate over all cubes
            mesh = layout.add_mesh(dxfattribs=dxfattribs)
            with mesh.edit_data() as data:
                data.vertices = vertices
                data.faces = cube_faces


def _subdivide(location=(0., 0., 0.), length=1., kind=0):
    """
    Divides a cube in sub-cubes and keeps only cubes determined by the building schema.

    All sides are parallel to x-, y- and z-axis, location is a (x, y, z) tuple and represents the coordinates of the
    lower left corner (nearest to the axis origin) of the cube, length is the side-length of the cube

    Args:
        location: (x, y, z) tuple, coordinates of the lower left corner of the cube
        length: side length of the cube
        kind: int for 0: original menger sponge; 1: Variant XOX; 2: Variant OXO; 3: Jerusalem Cube;

    Returns: list of sub-cubes (location, length)

    """

    init_x, init_y, init_z = location
    step_size = float(length) / cube_sizes[kind]
    remaining_cubes = building_schemas[kind]

    def sub_location(indices):
        x, y, z = indices
        return (init_x + x * step_size,
                init_y + y * step_size,
                init_z + z * step_size)
    return [(sub_location(indices), step_size) for indices in remaining_cubes]


def _menger_sponge(location=(0., 0., 0.), length=1., level=1, kind=0):
    """
    Builds a menger sponge for given level.

    Args:
        location: (x, y, z) tuple, coordinates of the lower left corner of the cube
        length: side length of the cube
        level: level of menger sponge, has to be 1 or bigger
        kind: int for 0: original menger sponge; 1: Variant XOX; 2: Variant OXO; 3: Jerusalem Cube;

    Returns: list of cube vertices

    """
    kind = int(kind)
    if kind not in (0, 1, 2, 3):
        raise ValueError('kind has to be 0, 1, 2 or 3.')
    level = int(level)
    if level < 1:
        raise ValueError("level has to be 1 or bigger.")
    cubes = _subdivide(location, length, kind=kind)
    for _ in range(level-1):
        next_level_cubes = []
        for location, length in cubes:
            next_level_cubes.extend(_subdivide(location, length, kind=kind))
        cubes = next_level_cubes
    return cubes

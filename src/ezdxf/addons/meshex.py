#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
"""
This add-on provides functions to exchange meshes with other file formats like:

    - STL
    - PLY
    - OFF
    - OBJ

The source or target entity is always a :class:`~ezdxf.render.MeshBuilder`
instance and therefore the supported features are also limited by this class.
Only vertices and faces are exchanged, colors, textures and normals are lost.
To be clear: this add-on is not a replacement for a proper file format
interfaces for this data formats!

"""
from typing import Union, List
import os
from ezdxf.math import Vec3
from ezdxf.render import MeshTransformer, MeshVertexMerger


class UnsupportedFileFormat(Exception):
    pass


class ParsingError(Exception):
    pass


def stl_readfile(filename: Union[str, os.PathLike]) -> MeshTransformer:
    """Read ascii STL file content as :class:`ezdxf.render.MeshTransformer`
    instance.

    Raises:
        UnsupportedFileFormat: invalid data file or binary STL file
        ParsingError: vertex parsing error

    """
    with open(filename, "rt", encoding="ascii", errors="ignore") as fp:
        content = fp.read()
    if not content.startswith("solid"):
        raise UnsupportedFileFormat(
            "binary STL format not supported or invalid STL file"
        )
    return stl_loads(content)


def stl_loads(content: str) -> MeshTransformer:
    """Load a mesh from a STL content string as :class:`ezdxf.render.MeshTransformer`
    instance.

    Raises:
        ParsingError: vertex parsing error

    """
    # http://www.fabbers.com/tech/STL_Format#Sct_ASCII
    # This implementation is not very picky and grabs only lines which start
    # with "vertex" or "endloop" and ignores the rest.
    def parse_vertex(line: str) -> Vec3:
        data = line.split()
        return Vec3(float(data[1]), float(data[2]), float(data[3]))

    mesh = MeshVertexMerger()
    face: List[Vec3] = []
    for num, line in enumerate(content.split("\n"), start=1):
        line = line.lstrip()
        if line.startswith("vertex"):
            try:
                face.append(parse_vertex(line))
            except (IndexError, ValueError):
                raise ParsingError(f"STL parsing error in line {num}: {line}")
        elif line.startswith("endloop"):
            if len(face) == 3:
                mesh.add_face(face)
            face.clear()
    return MeshTransformer.from_builder(mesh)

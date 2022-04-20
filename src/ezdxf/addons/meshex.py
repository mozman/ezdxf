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
from typing import Union, List, Sequence
import os
import struct

from ezdxf.math import Vec3
from ezdxf.render import MeshTransformer, MeshVertexMerger


class UnsupportedFileFormat(Exception):
    pass


class ParsingError(Exception):
    pass


def stl_readfile(filename: Union[str, os.PathLike]) -> MeshTransformer:
    """Read ascii or binary STL file content as :class:`ezdxf.render.MeshTransformer`
    instance.

    Raises:
        ParsingError: vertex parsing error or invalid/corrupt data

    """
    with open(filename, "rb") as fp:
        buffer = fp.read()
    if buffer.startswith(b"solid"):
        s = buffer.decode("ascii", errors="ignore")
        return stl_loads(s)
    else:
        return stl_loadb(buffer)


def stl_loads(content: str) -> MeshTransformer:
    """Load a mesh from an ascii STL content string as :class:`ezdxf.render.MeshTransformer`
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
        line = line.strip(" \r")
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


def stl_loadb(buffer: bytes) -> MeshTransformer:
    """Load a mesh from a binary STL data :class:`ezdxf.render.MeshTransformer`
    instance.

    Raises:
        ParsingError: invalid/corrupt data or not a binary STL file

    """
    # http://www.fabbers.com/tech/STL_Format#Sct_ASCII
    index = 80
    n_faces = struct.unpack_from("<I", buffer, index)[0]
    index += 4

    mesh = MeshVertexMerger()
    for _ in range(n_faces):
        try:
            face = struct.unpack_from("<12fH", buffer, index)
        except struct.error:
            raise ParsingError("binary STL parsing error")
        index += 50
        v1 = Vec3(face[3:6])
        v2 = Vec3(face[6:9])
        v3 = Vec3(face[9:12])
        mesh.add_face((v1, v2, v3))
    return MeshTransformer.from_builder(mesh)


def off_readfile(filename: Union[str, os.PathLike]) -> MeshTransformer:
    """Read OFF file content as :class:`ezdxf.render.MeshTransformer`
    instance.

    Raises:
        ParsingError: vertex or face parsing error

    """
    with open(filename, "rt", encoding="ascii", errors="ignore") as fp:
        content = fp.read()
    return off_loads(content)


def off_loads(content: str) -> MeshTransformer:
    """Load a mesh from a OFF content string as :class:`ezdxf.render.MeshTransformer`
    instance.

    Raises:
        ParsingError: vertex or face parsing error

    """
    # https://en.wikipedia.org/wiki/OFF_(file_format)
    mesh = MeshVertexMerger()
    lines: List[str] = []
    for line in content.split("\n"):
        line = line.strip(" \n\r")
        # "OFF" in a single line
        if line.startswith("#") or line == "OFF" or line == "":
            continue
        lines.append(line)

    if len(lines) == 0:
        raise ParsingError(f"OFF format parsing error: no data")

    if lines[0].startswith("OFF"):
        # OFF v f e
        lines[0] = lines[0][4:]

    n = lines[0].split()
    try:
        n_vertices, n_faces = int(n[0]), int(n[1])
    except ValueError:
        raise ParsingError(f"OFF format parsing error: {lines[0]}")

    if len(lines) < n_vertices + n_faces:
        raise ParsingError(f"OFF format parsing error: invalid data count")

    for vertex in lines[1 : n_vertices + 1]:
        v = vertex.split()
        try:
            vtx = Vec3(float(v[0]), float(v[1]), float(v[2]))
        except (ValueError, IndexError):
            raise ParsingError(f"OFF format vertex parsing error: {vertex}")
        mesh.vertices.append(vtx)

    index = n_vertices + 1
    face_indices = []
    for face in lines[index : index + n_faces]:
        f = face.split()
        try:
            vertex_count = int(f[0])
        except ValueError:
            raise ParsingError(f"OFF format face parsing error: {face}")
        for index in range(vertex_count):
            try:
                face_indices.append(int(f[1 + index]))
            except (ValueError, IndexError):
                raise ParsingError(
                    f"OFF format face index parsing error: {face}"
                )
        mesh.faces.append(tuple(face_indices))
        face_indices.clear()
    return MeshTransformer.from_builder(mesh)


def obj_readfile(filename: Union[str, os.PathLike]) -> List[MeshTransformer]:
    """Read OBJ file content as list of :class:`ezdxf.render.MeshTransformer`
    instances.

    Raises:
        ParsingError: vertex or face parsing error

    """
    with open(filename, "rt", encoding="ascii", errors="ignore") as fp:
        content = fp.read()
    return obj_loads(content)


def obj_loads(content: str) -> List[MeshTransformer]:
    """Load one or more meshes from an OBJ content string as list of
    :class:`ezdxf.render.MeshTransformer` instances.

    Raises:
        ParsingError: vertex parsing error

    """
    # https://en.wikipedia.org/wiki/Wavefront_.obj_file
    # This implementation is not very picky and grabs only lines which start
    # with "v", "g" or "f" and ignores the rest.
    def parse_vertex(l: str) -> Vec3:
        v = l.split()
        return Vec3(float(v[0]), float(v[1]), float(v[2]))

    def parse_face(l: str) -> Sequence[int]:
        return tuple(int(s.split("/")[0]) for s in l.split())

    vertices: List[Vec3] = [Vec3()]  # 1-indexed
    meshes: List[MeshTransformer] = []
    mesh = MeshVertexMerger()
    for num, line in enumerate(content.split("\n"), start=1):
        line = line.strip(" \r")
        if line.startswith("v"):
            try:
                vtx = parse_vertex(line[2:])
            except (IndexError, ValueError):
                raise ParsingError(
                    f"OBJ vertex parsing error in line {num}: {line}"
                )
            vertices.append(vtx)
        elif line.startswith("f"):
            try:
                mesh.add_face(vertices[i] for i in parse_face(line[2:]))
            except ValueError:
                raise ParsingError(
                    f"OBJ face parsing error in line {num}: {line}"
                )
            except IndexError:
                raise ParsingError(
                    f"OBJ face index error (n={len(vertices)}) in line {num}: {line}"
                )

        elif line.startswith("g"):
            meshes.append(MeshTransformer.from_builder(mesh))
            mesh = MeshVertexMerger()

    if len(mesh.vertices) > 0:
        meshes.append(MeshTransformer.from_builder(mesh))
    return meshes

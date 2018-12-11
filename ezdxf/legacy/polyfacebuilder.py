# Created: 04.04.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List
from ezdxf.lldxf.const import VERTEXNAMES

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFVertex
    from .facemixins import FaceProxy


class PolyfaceBuilder:
    def __init__(self, faces: Iterable['FaceProxy'], precision: int = 6):
        self.precision = precision
        self.faces = []
        self.vertices = []
        self.index_mapping = {}
        self.build(faces)

    @property
    def nvertices(self) -> int:
        return len(self.vertices)

    @property
    def nfaces(self) -> int:
        return len(self.faces)

    def get_vertices(self) -> List['DXFVertex']:
        vertices = self.vertices[:]
        vertices.extend(self.faces)
        return vertices

    def build(self, faces: Iterable['FaceProxy']) -> None:
        for face in faces:
            face_record = face.face_record
            for vertex, name in zip(face, VERTEXNAMES):
                index = self.add(vertex)
                # preserve sign of old index value
                sign = -1 if face_record.get_dxf_attrib(name, 0) < 0 else +1
                face_record.set_dxf_attrib(name, (index + 1) * sign)
            self.faces.append(face_record)

    def add(self, vertex: 'DXFVertex') -> int:
        def key(point):
            return tuple((round(coord, self.precision) for coord in point))

        location = key(vertex.dxf.location)
        try:
            return self.index_mapping[location]
        except KeyError:  # internal exception
            index = len(self.vertices)
            self.index_mapping[location] = index
            self.vertices.append(vertex)
            return index

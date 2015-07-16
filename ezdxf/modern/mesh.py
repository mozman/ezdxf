# Purpose: support for the Ac1015 MESH entity
# Created: 24.05.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager

from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.tags import DXFTag
from ..lldxf.classifiedtags import ClassifiedTags
from ..lldxf.const import DXFStructureError

_MESH_TPL = """  0
MESH
  5
0
330
1F
100
AcDbEntity
  8
0
100
AcDbSubDMesh
 71
2
 72
0
 91
0
 92
0
 93
0
 94
0
 95
0
"""

mesh_subclass = DefSubclass('AcDbSubDMesh', {
    'version': DXFAttr(71),
    'blend_crease': DXFAttr(72),  # 0 = off, 1 = on
    'subdivision_levels': DXFAttr(91),  # int >= 0
})


class Mesh(ModernGraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_MESH_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, mesh_subclass)

    @property
    def AcDbSubDMesh(self):
        return self.tags.subclasses[2]

    def get_data(self):
        return MeshData(self)

    def set_data(self, data):
        try:
            pos92 = self.AcDbSubDMesh.tag_index(92)
        except ValueError:
            raise DXFStructureError("Tag 92 (vertex count) in MESH entity not found.")
        pending_tags = self._remove_existing_data(pos92)
        self._append_vertices(data.vertices)
        self._append_faces(data.faces)
        self._append_edges(data.edges)
        self._append_edge_crease_values(data.edge_crease_values)
        self.AcDbSubDMesh.extend(pending_tags)

    def _remove_existing_data(self, insert_pos):
        tags = self.AcDbSubDMesh
        code = 95
        # search count tags 95, 94, 93 at least face list (93) should exist
        while True:
            try:
                count_tag = tags.tag_index(code)
            except ValueError:
                code -= 1
                if code == 92:
                    raise DXFStructureError("No count tag 93, 94 or 95 in MESH entity found.")
            else:
                break
        last_pos = count_tag + 1 + tags[count_tag].value
        pending_tags = tags[last_pos:]
        del tags[insert_pos:]
        return pending_tags

    def _append_vertices(self, vertices):
        # (92) vertex count
        tags = self.AcDbSubDMesh
        tags.append(DXFTag(92, len(vertices)))
        tags.extend(DXFTag(10, vertex) for vertex in vertices)

    def _append_faces(self, faces):
        # (93) count of face tags
        tags = []
        list_size = 0
        for face in faces:
            list_size += (len(face) + 1)
            tags.append(DXFTag(90, len(face)))
            for index in face:
                tags.append(DXFTag(90, index))
        tags.insert(0, DXFTag(93, list_size))
        self.AcDbSubDMesh.extend(tags)

    def _append_edges(self, edges):
        # (94) count of edge tags
        tags = self.AcDbSubDMesh
        tags.append(DXFTag(94, len(edges)*2))
        for edge in edges:
            tags.append(DXFTag(90, edge[0]))
            tags.append(DXFTag(90, edge[1]))

    def _append_edge_crease_values(self, values):
        # (95) edge crease count
        tags = self.AcDbSubDMesh
        tags.append(DXFTag(95, len(values)))
        tags.extend(DXFTag(140, value) for value in values)

    @contextmanager
    def edit_data(self):
        data = self.get_data()
        yield data
        self.set_data(data)

    def get_vertices(self):
        vertices = []
        try:
            pos = self.AcDbSubDMesh.tag_index(92)
        except ValueError:
            return vertices
        itags = iter(self.AcDbSubDMesh[pos+1:])
        while True:
            try:
                tag = next(itags)
            except StopIteration:  # premature end of tags, return what you got
                break
            if tag.code == 10:
               vertices.append(tag.value)
            else:  # end of vertex list
                break
        return vertices

    def get_faces(self):
        faces = []
        try:
            pos = self.AcDbSubDMesh.tag_index(93)
        except ValueError:
            return faces
        face = []
        itags = iter(self.AcDbSubDMesh[pos+1:])
        try:
            while True:
                tag = next(itags)
                # loop until first tag.code != 90
                if tag.code != 90:
                    break
                count = tag.value  # count of vertex indices
                while count > 0:
                    tag = next(itags)
                    face.append(tag.value)
                    count -= 1
                faces.append(tuple(face))
                del face[:]
        except StopIteration:  # premature end of tags, return what you got
            pass
        return faces

    def get_edges(self):
        edges = []
        try:
            pos = self.AcDbSubDMesh.tag_index(94)
        except ValueError:
            return edges
        start_index = None
        for index in Mesh.get_raw_list(self.AcDbSubDMesh, pos+1, code=90):
            if start_index is None:
                start_index = index
            else:
                edges.append((start_index, index))
                start_index = None
        return edges

    def get_edge_crease_values(self):
        try:
            pos = self.AcDbSubDMesh.tag_index(95)
        except ValueError:
            return []
        return Mesh.get_raw_list(self.AcDbSubDMesh, pos+1, code=140)

    @staticmethod
    def get_raw_list(tags, pos, code):
        raw_list = []
        itags = iter(tags[pos:])
        while True:
            try:
                tag = next(itags)
            except StopIteration:
                break
            if tag.code == code:
                raw_list.append(tag.value)
            else:
                break
        return raw_list


class MeshData(object):
    def __init__(self, mesh):
        self.vertices = mesh.get_vertices()
        self.faces = mesh.get_faces()
        self.edges = mesh.get_edges()
        self.edge_crease_values = mesh.get_edge_crease_values()

    def add_face(self, vertices):  # todo
        pass

    def add_edge(self, vertices):  # todo
        pass

    def optimize(self):  # todo
        pass

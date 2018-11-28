# Created: 24.05.2015
# Copyright (c) 2015-2018, Manfred Moitzi
# License: MIT License
from contextlib import contextmanager
import array
from itertools import chain

from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.const import DXFStructureError, DXFValueError
from ezdxf.lldxf.packedtags import TagArray, VertexArray, TagList
from ezdxf.tools import take2
from ezdxf.lldxf import loader

from .graphics import none_subclass, entity_subclass, ModernGraphicEntity


class MeshVertexArray(VertexArray):
    code = -92

    def dxftags(self):
        yield DXFTag(92, len(self))
        # python 2.7 compatible
        for tag in super(MeshVertexArray, self).dxftags():
            yield tag

    def set_data(self, vertices):
        self.value = array.array('d', chain.from_iterable(vertices))


def create_vertex_array(tags, start_index):
    vertex_tags = tags.collect_consecutive_tags(codes=(10,), start=start_index)
    return MeshVertexArray(data=chain.from_iterable(t.value for t in vertex_tags))


class FaceList(TagList):
    code = -93

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def dxftags(self):
        # count = count of tags not faces!
        yield DXFTag(93, self.tag_count())
        for face in self.value:
            yield DXFTag(90, len(face))
            for index in face:
                yield DXFTag(90, index)

    def tag_count(self):
        return len(self.value) + sum(len(f) for f in self.value)

    def set_data(self, faces):
        _faces = []
        for face in faces:
            _faces.append(face_to_array(face))
        self.value = _faces


def face_to_array(face):
    max_index = max(face)
    if max_index < 256:
        dtype = 'B'
    elif max_index < 65536:
        dtype = 'I'
    else:
        dtype = 'L'
    return array.array(dtype, face)


def create_face_list(tags, start_index):
    faces = FaceList()
    faces_list = faces.value
    face = []
    counter = 0
    for tag in tags.collect_consecutive_tags(codes=(90, ), start=start_index):
        if not counter:
            # leading counter tag
            counter = tag.value
            if face:
                # group code 90 = 32 bit integer
                faces_list.append(face_to_array(face))
                face = []
        else:
            # followed by count face tags
            counter -= 1
            face.append(tag.value)

    # add last face
    if face:
        # group code 90 = 32 bit integer
        faces_list.append(face_to_array(face))

    return faces


class EdgeArray(TagArray):
    code = -94
    VALUE_CODE = 90  # 32 bit integer
    DTYPE = 'L'

    def dxftags(self):
        # count = count of edges not tags!
        yield DXFTag(94, len(self.value)//2)
        # python 2.7 compatible
        for v in super(EdgeArray, self).dxftags():
            yield v

    def __len__(self):
        return len(self.value) // 2

    def __iter__(self):
        for edge in take2(self.value):
            yield edge

    def set_data(self, edges):
        self.value = array.array('L', chain.from_iterable(edges))


def create_edge_array(tags, start_index):
    return EdgeArray(data=collect_values(tags, start_index, code=90))


def collect_values(tags, start_index, code):
    values = tags.collect_consecutive_tags(codes=(code, ), start=start_index)
    return (t.value for t in values)


def create_crease_array(tags, start_index):
    return CreaseArray(data=collect_values(tags, start_index, code=140))


class CreaseArray(TagArray):
    code = -95
    VALUE_CODE = 140  # double precision
    DTYPE = 'd'

    def dxftags(self):
        yield DXFTag(95, len(self.value))
        # python 2.7 compatible
        for v in super(CreaseArray, self).dxftags():
            yield v

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def set_data(self, creases):
        self.value = array.array('d', creases)


COUNT_ERROR_MSG = "'MESH (#{}) without {} count.'"


def convert_and_replace_tags(tags, handle):
    def process_vertices():
        try:
            vertex_count_index = tags.tag_index(92)
        except DXFValueError:
            raise DXFStructureError(COUNT_ERROR_MSG.format(handle, 'vertex'))
        vertices = create_vertex_array(tags, vertex_count_index+1)
        # replace vertex count tag and all vertex tags by MeshVertexArray()
        end_index = vertex_count_index + 1 + len(vertices)
        tags[vertex_count_index:end_index] = [vertices]

    def process_faces():
        try:
            face_count_index = tags.tag_index(93)
        except DXFValueError:
            raise DXFStructureError(COUNT_ERROR_MSG.format(handle, 'face'))
        else:
            # replace face count tag and all face tags by FaceList()
            faces = create_face_list(tags, face_count_index+1)
            end_index = face_count_index + 1 + faces.tag_count()
            tags[face_count_index:end_index] = [faces]

    def process_edges():
        try:
            edge_count_index = tags.tag_index(94)
        except DXFValueError:
            raise DXFStructureError(COUNT_ERROR_MSG.format(handle, 'edge'))
        else:
            edges = create_edge_array(tags, edge_count_index+1)
            # replace edge count tag and all edge tags by EdgeArray()
            end_index = edge_count_index + 1 + len(edges.value)
            tags[edge_count_index:end_index] = [edges]

    def process_creases():
        try:
            crease_count_index = tags.tag_index(95)
        except DXFValueError:
            raise DXFStructureError(COUNT_ERROR_MSG.format(handle, 'crease'))
        else:
            creases = create_crease_array(tags, crease_count_index+1)
            # replace crease count tag and all crease tags by CreaseArray()
            end_index = crease_count_index + 1 + len(creases.value)
            tags[crease_count_index:end_index] = [creases]

    process_vertices()
    process_faces()
    process_edges()
    process_creases()


@loader.register('MESH', legacy=False)
def tag_processor(tags):
    subclass = tags.get_subclass('AcDbSubDMesh')
    handle = tags.get_handle()
    convert_and_replace_tags(subclass, handle)
    return tags


_MESH_TPL = """0
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
90
0
"""

mesh_subclass = DefSubclass('AcDbSubDMesh', {
    'version': DXFAttr(71),
    'blend_crease': DXFAttr(72),  # 0 = off, 1 = on
    'subdivision_levels': DXFAttr(91),  # int >= 0, 0 is no smoothing
    # 92: Vertex count of level 0
    # 10: Vertex position, multiple entries
    # 93: Size of face list of level 0
    # 90: Face list item, >=3 possible
    #     90: length of face list
    #     90: 1st vertex index
    #     90: 2nd vertex index ...
    # 94: Edge count of level 0
    #     90: Vertex index of 1st edge
    #     90: Vertex index of 2nd edge
    # 95: Edge crease count of level 0
    #     95 same as 94, or how is the 'edge create value' associated to edge index
    # 140: Edge create value
    #
    # Overriding properties: how does this work?
    # 90: Count of sub-entity which property has been overridden
    # 91: Sub-entity marker
    # 92: Count of property was overridden
    # 90: Property type
    #     0 = Color
    #     1 = Material
    #     2 = Transparency
    #     3 = Material mapper
})


class Mesh(ModernGraphicEntity):
    __slots__ = ()
    TEMPLATE = tag_processor(ExtendedTags.from_text(_MESH_TPL))
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, mesh_subclass)

    @property
    def AcDbSubDMesh(self):
        return self.tags.subclasses[2]

    @property
    def vertices(self):
        return self.AcDbSubDMesh.get_first_tag(MeshVertexArray.code)

    @property
    def faces(self):
        return self.AcDbSubDMesh.get_first_tag(FaceList.code)

    @property
    def edges(self):
        return self.AcDbSubDMesh.get_first_tag(EdgeArray.code)

    @property
    def creases(self):
        return self.AcDbSubDMesh.get_first_tag(CreaseArray.code)

    def get_data(self):
        return MeshData(self)

    def set_data(self, data):
        self.vertices.set_data(data.vertices)
        self.faces.set_data(data.faces)
        self.edges.set_data(data.edges)
        self.creases.set_data(data.edge_crease_values)

    @contextmanager
    def edit_data(self):
        data = self.get_data()
        yield data
        self.set_data(data)


class MeshData(object):
    def __init__(self, mesh):
        self.vertices = list(mesh.vertices)
        self.faces = list(mesh.faces)
        self.edges = list(mesh.edges)
        self.edge_crease_values = list(mesh.creases)

    def add_face(self, vertices):
        return self.add_entity(vertices, self.faces)

    def add_edge(self, vertices):
        if len(vertices) != 2:
            raise DXFValueError("Parameter vertices has to be a list/tuple of 2 vertices [(x1, y1, z1), (x2, y2, z2)].")
        return self.add_entity(vertices, self.edges)

    def add_entity(self, vertices, entity_list):
        indices = [self.add_vertex(vertex) for vertex in vertices]
        entity_list.append(indices)
        return indices

    def add_vertex(self, vertex):
        if len(vertex) != 3:
            raise DXFValueError('Parameter vertex has to be a 3-tuple (x, y, z).')
        index = len(self.vertices)
        self.vertices.append(vertex)
        return index

    def optimize(self, precision=6):
        def remove_doublette_vertices():
            def prepare_vertices():
                for index, vertex in enumerate(self.vertices):
                    x, y, z = vertex
                    yield round(x, precision), round(y, precision), round(z, precision), index

            sorted_vertex_list = list(sorted(prepare_vertices()))
            original_vertices = self.vertices
            self.vertices = []
            index_map = {}
            cmp_vertex = None
            index = 0
            while len(sorted_vertex_list):
                vertex_entry = sorted_vertex_list.pop()
                original_index = vertex_entry[3]
                vertex = original_vertices[original_index]
                if vertex != cmp_vertex:  # this is not a doublette
                    index = len(self.vertices)
                    self.vertices.append(vertex)
                    index_map[original_index] = index
                    cmp_vertex = vertex
                else:  # it is a doublette
                    index_map[original_index] = index
            return index_map

        def remap_faces(index_map):
            self.faces = remap_indices(self.faces, index_map)

        def remap_edges(index_map):
            self.edges = remap_indices(self.edges, index_map)

        def remap_indices(entity_list, index_map):
            mapped_indices = []
            for entity in entity_list:
                index_list = [index_map[index] for index in entity]
                mapped_indices.append(tuple(index_list))
            return mapped_indices

        index_map = remove_doublette_vertices()
        remap_faces(index_map)
        remap_edges(index_map)

#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import List, Iterator, Sequence, Optional
from ezdxf.render import MeshVertexMerger, MeshTransformer, MeshBuilder
from ezdxf.math import Matrix44, Vec3
from .entities import Body, Lump, NONE_REF, Face, Shell


def mesh_from_body(body: Body, merge_lumps=True) -> List[MeshTransformer]:
    """Returns a list of :class:`~ezdxf.render.MeshTransformer` instances from
    the given ACIS :class:`Body` entity.
    The list contains multiple meshes if `merge_lumps` is ``False`` or just a
    singe mesh if `merge_lumps` is ``True``.

    The ACIS format stores the faces in counter-clockwise orientation where the
    face-normal points outwards (away) from the solid body (material).

    .. note::

        This function returns meshes build up only from flat polygonal
        :class:`Face` entities, for a tessellation of more complex ACIS
        entities (spline surfaces, tori, cones, ...) is an ACIS kernel
        required which `ezdxf` does not provide.

    Args:
        body: ACIS entity of type :class:`Body`
        merge_lumps: returns all :class:`Lump` entities
            from a body as a single mesh if ``True`` otherwise each :class:`Lump`
            entity is a separated mesh

    Raises:
        TypeError: given `body` entity has invalid type

    """
    if not isinstance(body, Body):
        raise TypeError(f"expected a body entity, got: {type(body)}")

    meshes: List[MeshTransformer] = []
    builder = MeshVertexMerger()
    for faces in flat_polygon_faces_from_body(body):
        for face in faces:
            builder.add_face(face)
        if not merge_lumps:
            meshes.append(MeshTransformer.from_builder(builder))
            builder = MeshVertexMerger()
    if merge_lumps:
        meshes.append(MeshTransformer.from_builder(builder))
    return meshes


def flat_polygon_faces_from_body(
    body: Body,
) -> Iterator[List[Sequence[Vec3]]]:
    """Yields all flat polygon faces from all lumps in the given
    :class:`Body` entity.
    Yields a separated list of faces for each linked :class:`Lump` entity.

    Args:
        body: ACIS entity of type :class:`Body`

    Raises:
        TypeError: given `body` entity has invalid type

    """

    if not isinstance(body, Body):
        raise TypeError(f"expected a body entity, got: {type(body)}")
    lump = body.lump
    transform = body.transform

    m: Optional[Matrix44] = None
    if not transform.is_none:
        m = transform.matrix
    while not lump.is_none:
        yield list(flat_polygon_faces_from_lump(lump, m))
        lump = lump.next_lump


def flat_polygon_faces_from_lump(
    lump: Lump, m: Matrix44 = None
) -> Iterator[Sequence[Vec3]]:
    """Yields all flat polygon faces from the given :class:`Lump` entity as
    sequence of :class:`~ezdxf.math.Vec3` instances. Applies the transformation
    :class:`~ezdxf.math.Matrix44` `m` to all vertices if not ``None``.

    Args:
        lump: :class:`Lump` entity
        m: optional transformation matrix

    Raises:
        TypeError: `lump` has invalid ACIS type

    """
    if not isinstance(lump, Lump):
        raise TypeError(f"expected a lump entity, got: {type(lump)}")

    shell = lump.shell
    if shell.is_none:
        return  # not a shell
    vertices: List[Vec3] = []
    face = shell.face
    while not face.is_none:
        first_coedge = NONE_REF
        vertices.clear()
        if face.surface.type == "plane-surface":
            try:
                first_coedge = face.loop.coedge
            except AttributeError:  # loop is a none-entity
                pass
        coedge = first_coedge
        while not coedge.is_none:  # invalid coedge or face is not closed
            # the edge entity contains the vertices and the curve type
            edge = coedge.edge
            try:
                # only straight lines as face edges supported:
                if edge.curve.type != "straight-curve":
                    break
                # add the first edge vertex to the face vertices
                if coedge.sense:  # reversed sense of the underlying edge
                    vertices.append(edge.end_vertex.point.location)
                else:  # same sense as the underlying edge
                    vertices.append(edge.start_vertex.point.location)
            except AttributeError:
                # one of the involved entities is a none-entity or an
                # incompatible entity type -> ignore this face!
                break
            coedge = coedge.next_coedge
            if coedge is first_coedge:  # a valid closed face
                if m is not None:
                    yield tuple(m.transform_vertices(vertices))
                else:
                    yield tuple(vertices)
                break
        face = face.next_face


def body_from_mesh(mesh: MeshBuilder, precision: int = 6) -> Body:
    """Returns a :term:`ACIS` :class:`~ezdxf.acis.entities.Body` entity from a
    :class:`~ezdxf.render.MeshBuilder` instance.

    This entity can be assigned to a :class:`~ezdxf.entities.Solid3d` DXF entity
    as :term:`SAT` or :term:`SAB` data according to the version your DXF
    document uses (SAT for DXF R2000 to R2010 and SAB for DXF R2013 and later).

    If the `mesh` contains multiple separated meshes, each mesh will be a
    separated :class:`~ezdxf.acis.entities.Lump` node.
    If each mesh should get its own :class:`~ezdxf.acis.entities.Body` entity,
    separate the meshes beforehand by the method
    :class:`~ezdxf.render.MeshBuilder.separate_meshes`.

    A closed mesh creates a solid body and an open mesh creates an open (hollow)
    shell. The detection if the mesh is open or closed is based on the edges
    of the mesh: if **all** edges of mesh have two adjacent faces the mesh is
    closed.

    The current implementation applies automatically a vertex optimization,
    which merges coincident vertices into a single vertex.

    """
    mesh = mesh.optimize_vertices(precision)
    body = Body()
    for mesh in mesh.separate_meshes():
        # TODO: move mesh to origin and set transformation of body accordingly
        lump = lump_from_mesh(mesh)
        body.append_lump(lump)
    return body


def lump_from_mesh(mesh: MeshBuilder) -> Lump:
    """Returns a :class:`~ezdxf.acis.entities.Lump` entity from a
    :class:`~ezdxf.render.MeshBuilder` instance. The `mesh` has to be a single
    body or shell!
    """
    lump = Lump()
    shell = Shell()
    lump.append_shell(shell)
    face_builder = FaceBuilder(mesh)
    for face in face_builder.acis_faces():
        shell.append_face(face)
    return lump


class FaceBuilder:
    def __init__(self, mesh: MeshBuilder):
        self.vertices: List[Vec3] = mesh.vertices
        self.faces: List[Sequence[int]] = mesh.faces
        self.setup()

    def setup(self):
        pass

    def acis_faces(self) -> Iterator[Face]:
        pass

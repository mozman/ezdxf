#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List
from ezdxf._acis.abstract import AbstractEntity
from ezdxf._acis.parsing import body_planar_polygon_faces
from ezdxf.render import MeshVertexMerger, MeshTransformer


def body_to_mesh(body: AbstractEntity, merge_lumps=True) -> List[MeshTransformer]:
    """Returns a list of :class:`~ezdxf.render.MeshTransformer` instances from
    the given ACIS `body`_ entity. The list contains multiple meshes if
    `merge_lumps` is ``False`` or just a singe mesh if `merge_lumps` is ``True``.

    This function returns only meshes build up by planar polygonal faces stored
    in a `body`_ entity, for a conversion of more complex ACIS data structures is
    an ACIS kernel required.

    Args:
        body: ACIS entity of type `body`_
        merge_lumps: returns all `lump`_ entities from a body as a single mesh
            if ``True`` otherwise each `lump`_ entity is a separated mesh

    Raises:
        TypeError: `body` has invalid ACIS type

    """
    meshes: List[MeshTransformer] = []
    builder = MeshVertexMerger()
    for faces in body_planar_polygon_faces(body):
        for face in faces:
            builder.add_face(face)
        if not merge_lumps:
            meshes.append(MeshTransformer.from_builder(builder))
            builder = MeshVertexMerger()
    if merge_lumps:
        meshes.append(MeshTransformer.from_builder(builder))
    return meshes


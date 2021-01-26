Bounding Box
============

.. versionadded:: 0.16

.. module:: ezdxf.bbox

The :mod:`ezdxf.bbox` module provide tools to calculate bounding boxes for
many DXF entities, but not all. The bounding box calcualtion is based on the
:mod:`ezdxf.disassemble` module and therefore has the same limitation.

The base type for bounding boxes is the :class:`~ezdxf.math.BoundingBox` class
from the module :mod:`ezdxf.math`.

The `entities` iterable as input can be the whole modelspace, an entity
query or any iterable container of DXF entities.

The optional caching object :class:`Cache` has to be instantiated by the user,
this is only useful if the same entities will be processed multiple times.
This cache works only for entities which have a handle, virtual entities
( e.g block reference content) are created on the fly and do not have a handle
nor a fixed id, therefore caching is not possible.

Example usage with caching:

.. code-block:: Python

    from ezdxf import bbox

    msp = doc.modelspace()
    cache = bbox.Cache()
    # get overall bounding box
    first_bbox = bbox.extends(msp, cache)
    # bounding box of all LINE entities
    second_bbox = bbox.extend(msp.query("LINE"), cache)


.. autofunction:: extends(entities: Iterable[DXFEntity], cache: Cache=None) -> BoundingBox

.. autofunction:: multi_flat(entities: Iterable[DXFEntity] cache: Cache=None) -> Iterable[BoundingBox]

.. autofunction:: multi_recursive(entities: Iterable[DXFEntity] cache: Cache=None) -> Iterable[BoundingBox]

.. class:: Cache

    Caching object
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

.. autofunction:: extends(entities: Iterable[DXFEntity]) -> BoundingBox

.. autofunction:: multi_flat(entities: Iterable[DXFEntity]) -> Iterable[BoundingBox]

.. autofunction:: multi_recursive(entities: Iterable[DXFEntity]) -> Iterable[BoundingBox]


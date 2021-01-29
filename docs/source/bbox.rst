Bounding Box
============

.. versionadded:: 0.16

.. module:: ezdxf.bbox

The :mod:`ezdxf.bbox` module provide tools to calculate bounding boxes for
many DXF entities, but not all. The bounding box calculation is based on the
:mod:`ezdxf.disassemble` module and therefore has the same limitation.

.. warning::

    If accurate boundary boxes for text entities are important for you,
    read this first: :ref:`Text Boundary Calculation`.
    TL;DR: Boundary boxes for text entities are **not accurate!**

The base type for bounding boxes is the :class:`~ezdxf.math.BoundingBox` class
from the module :mod:`ezdxf.math`.

The `entities` iterable as input can be the whole modelspace, an entity
query or any iterable container of DXF entities.

The **optional** caching object :class:`Cache` has to be instantiated by the
user, this is only useful if the same entities will be processed multiple times.

Example usage with caching:

.. code-block:: Python

    from ezdxf import bbox

    msp = doc.modelspace()
    cache = bbox.Cache()
    # get overall bounding box
    first_bbox = bbox.extends(msp, cache)
    # bounding box of all LINE entities
    second_bbox = bbox.extend(msp.query("LINE"), cache)

Calculation Function
--------------------

.. autofunction:: extends(entities: Iterable[DXFEntity], cache: Cache=None) -> BoundingBox

.. autofunction:: multi_flat(entities: Iterable[DXFEntity] cache: Cache=None) -> Iterable[BoundingBox]

.. autofunction:: multi_recursive(entities: Iterable[DXFEntity] cache: Cache=None) -> Iterable[BoundingBox]

Caching Strategies
------------------

Because `ezdxf` is not a CAD application, `ezdxf` does not manage data
structures which are optimized for a usage by a CAD kernel. This means
that the content of complex entities like block references or leaders has
to be created on demand by DXF primitives on the fly. These temporarily
created entities are called virtual entities and have no handle and are not
stored in the entities database.

All this is required to calculate the bounding box of complex entities,
and it is therefore a very time consuming task. By using a :class:`Cache` object
it is possible to speedup this calculations, but this is not a magically feature
which requires an understanding of what is happening under the hood to achieve
any performance gains.

For a single bounding box calculation, without any reuse of entities it makes
no sense of using a :class:`Cache` object, e.g. calculation of the modelspace
extends:

.. code-block:: python

    from pathlib import Path
    import ezdxf
    from ezdxf import bbox

    CADKitSamples = Path(ezdxf.EZDXF_TEST_FILES) / 'CADKitSamples'

    doc = ezdxf.readfile(CADKitSamples / 'A_000217.dxf')
    cache = bbox.Cache()
    ext = bbox.extends(doc.modelspace(), cache)

    print(cache)

1226 cached objects and not a single cache hit::

    Cache(n=1226, hits=0, misses=3273)

The result for using UUIDs to cache virtual entities is not better::

    Cache(n=2206, hits=0, misses=3273)

Same count of hits and misses, but now the cache also references
~1000 virtual entities, which block your memory until the cache is deleted,
luckily this is a small DXF file (~838 kB).

Bounding box calculations for multiple entity queries, which have overlapping
entity results, using a :class:`Cache` object may speedup calculation.

TODO

Cache Class
-----------

.. autoclass:: Cache

    .. py:attribute:: hits

    .. py:attribute:: misses

    .. automethod:: invalidate

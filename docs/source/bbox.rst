Bounding Box
============

.. versionadded:: 0.16

.. module:: ezdxf.bbox

The :mod:`ezdxf.bbox` module provide tools to calculate bounding boxes for
many DXF entities, but not for all. The bounding box calculation is based on the
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
    first_bbox = bbox.extents(msp, cache)
    # bounding box of all LINE entities
    second_bbox = bbox.extend(msp.query("LINE"), cache)

Functions
---------

.. autofunction:: extents(entities: Iterable[DXFEntity], cache: Cache=None) -> BoundingBox

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
extents:

.. code-block:: python

    from pathlib import Path
    import ezdxf
    from ezdxf import bbox

    CADKitSamples = Path(ezdxf.EZDXF_TEST_FILES) / 'CADKitSamples'

    doc = ezdxf.readfile(CADKitSamples / 'A_000217.dxf')
    cache = bbox.Cache()
    ext = bbox.extents(doc.modelspace(), cache)

    print(cache)

1226 cached objects and not a single cache hit::

    Cache(n=1226, hits=0, misses=3273)

The result for using UUIDs to cache virtual entities is not better::

    Cache(n=2206, hits=0, misses=3273)

Same count of hits and misses, but now the cache also references
~1000 virtual entities, which block your memory until the cache is deleted,
luckily this is a small DXF file (~838 kB).

Bounding box calculations for multiple entity queries, which have overlapping
entity results, using a :class:`Cache` object may speedup the calculation:

.. code-block:: python

    doc = ezdxf.readfile(CADKitSamples / 'A_000217.dxf.dxf')
    msp = doc.modelspace()
    cache = bbox.Cache(uuid=False)

    ext = bbox.extents(msp, cache)
    print(cache)

    # process modelspace again
    ext = bbox.extents(msp, cache)
    print(cache)

Processing the same data again leads some hits::

    1st run: Cache(n=1226, hits=0, misses=3273)
    2nd run: Cache(n=1226, hits=1224, misses=3309)

Using :code:`uuid=True` leads not to more hits, but more cache entries::

    1st run: Cache(n=2206, hits=0, misses=3273)
    2nd run: Cache(n=2206, hits=1224, misses=3309)

Creating stable virtual entities by disassembling the entities at
first leads to more hits:

.. code-block:: Python

    from ezdxf import disassemble

    entities = list(disassemble.recursive_decompose(msp))
    cache = bbox.Cache(uuid=False)

    bbox.extents(entities, cache)
    print(cache)

    bbox.extents(entities, cache)
    print(cache)

First without UUID for stable virtual entities::

    1st run: Cache(n=1037, hits=0, misses=4074)
    2nd run: Cache(n=1037, hits=1037, misses=6078)

Using UUID for stable virtual entities leads to more hits::

    1st run: Cache(n=2019, hits=0, misses=4074)
    2nd run: Cache(n=2019, hits=2018, misses=4116)

But caching virtual entities needs also more memory.

In conclusion: Using a cache is only useful, if you often process
**nearly the same data**; only then can a performance gain be expected.

Cache Class
-----------

.. autoclass:: Cache

    .. py:attribute:: hits

    .. py:attribute:: misses

    .. automethod:: invalidate

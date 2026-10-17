.. module:: ezdxf.addons.geometry_batch

Batched LINE Geometry
=====================

The experimental :class:`LineBatch` addon processes many zero-thickness LINE
entities together. It supports affine transformations, XYZ extents and XY
bounding-box window selection. It does not modify the original DXF entities or
accelerate file parsing, text layout, curve flattening or drawing backends.

NumPy with double precision is the default and needs no additional dependencies.
For CUDA or Apple MPS install ``ezdxf[gpu]`` with a PyTorch build supporting your
hardware. An explicitly requested unavailable GPU raises an error.

.. code-block:: python

    import ezdxf
    from ezdxf.addons.geometry_batch import LineBatch
    from ezdxf.math import Matrix44

    doc = ezdxf.readfile("drawing.dxf")
    lines = list(doc.modelspace().query("LINE[thickness==0]"))
    batch = LineBatch.from_entities(lines)  # NumPy, float64
    # CUDA: backend="cuda", precision="float64"
    # Apple MPS: backend="mps", precision="float32"
    moved = batch.transformed(Matrix44.translate(10, 0, 0))
    selected_indices = moved.select_window((0, 0), (100, 100))
    selected_originals = [lines[i] for i in selected_indices]
    bounds = moved.extents()

Snapshots preserve input order and do not follow later entity edits. Unsupported
entity types and nonzero LINE thickness raise ``ValueError``. Selection uses
inclusive, axis-aligned bounding boxes; overlap can include lines which do not
actually cross the window.

Precision and performance
-------------------------

MPS does not support float64, so it requires explicit ``precision="float32"``.
Single precision can erase small features at large world coordinates and change
selection decisions at boundaries. Use it for approximate preview or analysis,
and keep the authoritative DXF coordinates in double precision. CUDA supports
either precision; its double-precision speed depends on the GPU.

GPU batches retain arrays and cached bounds on the device. Reuse a batch for
multiple operations: packing Python entities, allocation, device transfers and
small kernel launches can cost more than the computation. NumPy can outperform a
GPU even for large batches. No automatic device selection or speedup is implied.
Returning arrays or extents synchronizes results with the host; use
:meth:`LineBatch.synchronize` when timing operations returning another batch.
Transformations also check for overflow and synchronize this validity check.
See ``profiling/geometry_batch.py`` for a reproducible comparison including
packing, upload, computation and download, plus resident-batch measurements.

.. autoclass:: LineBatch
    :members:

"""Reproducible LINE batch benchmark, including transfer and packing costs.

Example: python profiling/geometry_batch.py --gpu mps --output mps.json
For CUDA: --gpu cuda. Use an otherwise idle machine. Times are wall-clock medians
after warm-up, synchronized through host outputs; this is not GPU kernel timing.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

import numpy as np

import ezdxf
from ezdxf.addons.geometry_batch import LineBatch
from ezdxf.math import Matrix44


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpu", choices=["mps", "cuda"])
    parser.add_argument(
        "--sizes", nargs="+", type=int, default=[10_000, 100_000, 1_000_000]
    )
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "platform": platform.platform(),
        "python": sys.version,
        "numpy": np.__version__,
        "ezdxf": ezdxf.__version__,
        "native_extensions": ezdxf.options.use_c_ext,
        "thread_environment": {
            name: os.environ.get(name)
            for name in (
                "OPENBLAS_NUM_THREADS",
                "OMP_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS",
            )
        },
        "measurements": [],
    }
    backends = [("numpy", "float64"), ("numpy", "float32")]
    if args.gpu:
        import torch

        result["torch"] = torch.__version__
        result["device"] = (
            torch.cuda.get_device_name(0) if args.gpu == "cuda" else "Apple MPS"
        )
        backends.append((args.gpu, "float32"))
        if args.gpu == "cuda":
            backends.append((args.gpu, "float64"))
    matrix = Matrix44.chain(Matrix44.z_rotate(0.3), Matrix44.translate(1, 2, 3))

    def pipeline(batch):
        moved = batch.transformed(matrix)
        extent = moved.extents()
        mask = moved.window_mask((-20, -20), (20, 20))
        return np.array((tuple(extent.extmin), tuple(extent.extmax))), mask

    def measure(name, size, backend, precision, operation):
        operation()
        samples = []
        for _ in range(args.repeat):
            gc.collect()
            start = time.perf_counter()
            operation()
            samples.append((time.perf_counter() - start) * 1000)
        row = dict(
            operation=name,
            lines=size,
            backend=backend,
            precision=precision,
            median_ms=statistics.median(samples),
            samples_ms=samples,
        )
        result["measurements"].append(row)
        print(
            f"{size:>8} {backend:>5} {precision} {name}: {row['median_ms']:.3f} ms",
            flush=True,
        )

    for size in args.sizes:
        rng = np.random.default_rng(20261017)
        starts = rng.uniform(-1000, 1000, (size, 3))
        vertices = np.stack((starts, starts + rng.uniform(-5, 5, (size, 3))), axis=1)
        reference_extents, reference_mask = pipeline(LineBatch(vertices))
        for backend, precision in backends:

            def construct():
                batch = LineBatch(vertices, backend=backend, precision=precision)
                batch.synchronize()
                return batch

            resident = construct()
            extents, mask = pipeline(resident)
            error = float(np.abs(extents - reference_extents).max())
            mismatch = int(np.count_nonzero(mask != reference_mask))
            result.setdefault("parity", []).append(
                dict(
                    lines=size,
                    backend=backend,
                    precision=precision,
                    max_extent_abs_error=error,
                    mask_mismatches=mismatch,
                )
            )
            if precision == "float64":
                np.testing.assert_allclose(
                    extents, reference_extents, rtol=1e-12, atol=1e-12
                )
                np.testing.assert_array_equal(mask, reference_mask)
            measure("construct_upload", size, backend, precision, construct)
            measure(
                "host_array_pipeline",
                size,
                backend,
                precision,
                lambda: pipeline(construct()),
            )
            measure(
                "resident_pipeline",
                size,
                backend,
                precision,
                lambda: pipeline(resident),
            )
            resident.window_mask((-20, -20), (20, 20))  # populate cached device bounds
            measure(
                "resident_cached_window",
                size,
                backend,
                precision,
                lambda: resident.window_mask((-20, -20), (20, 20)),
            )
        del vertices, starts, resident
        gc.collect()

    doc = ezdxf.new()
    lines = [
        doc.modelspace().add_line((i % 200, i // 200), (i % 200 + 0.8, i // 200 + 0.5))
        for i in range(20_000)
    ]
    for backend, precision in backends:
        measure(
            "entities_pack_pipeline",
            len(lines),
            backend,
            precision,
            lambda: pipeline(
                LineBatch.from_entities(lines, backend=backend, precision=precision)
            ),
        )
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

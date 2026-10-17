# License: MIT License
"""Optional NumPy, CUDA and Apple MPS processing of batches of LINE endpoints.

This module does not change DXF entities. Double precision NumPy is the default;
GPU use is explicit and requires the optional ``gpu`` dependency. MPS requires
explicit single precision, which is unsuitable for exact CAD boundary decisions.
"""

from __future__ import annotations

import importlib
from typing import Any, Iterable, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ezdxf.entities import DXFEntity
from ezdxf.math import BoundingBox, Matrix44


class LineBatch:
    """An owned snapshot of endpoints with shape ``(line_count, 2, 3)``.

    Supported backends are ``numpy``, ``cuda`` (or ``cuda:N``), and ``mps``.
    Precision is ``float64`` by default, or explicitly ``float32`` for approximate
    processing. Arrays remain on the selected device between operations. Methods
    returning NumPy arrays or a bounding box synchronize device results with the
    host. All geometry is in the coordinate system supplied by the caller.
    """

    def __init__(
        self, vertices: ArrayLike, *, backend: str = "numpy", precision: str = "float64"
    ) -> None:
        if precision not in ("float64", "float32"):
            raise ValueError("precision must be 'float64' or 'float32'")
        if backend not in ("numpy", "cuda", "mps") and not (
            backend.startswith("cuda:") and backend[5:].isdigit()
        ):
            raise ValueError("backend must be 'numpy', 'cuda', 'cuda:N', or 'mps'")
        if backend == "mps" and precision != "float32":
            raise ValueError("MPS requires explicit precision='float32' (approximate)")
        data = np.array(vertices, dtype=precision, order="C", copy=True)
        if data.ndim != 3 or data.shape[1:] != (2, 3):
            raise ValueError("vertices must have shape (line_count, 2, 3)")
        if not np.isfinite(data).all():
            raise ValueError(
                "vertices must be finite and representable in the precision"
            )
        self._backend = backend
        self._precision = precision
        self._torch: Any = None
        self._bounds: Any = None
        self._data: Any = data
        if backend != "numpy":
            try:
                torch = importlib.import_module("torch")
            except ImportError as exc:
                raise ImportError(
                    "GPU batches require PyTorch: pip install 'ezdxf[gpu]'"
                ) from exc
            if backend == "mps":
                available = torch.backends.mps.is_available()
            else:
                available = torch.cuda.is_available()
            if not available:
                raise RuntimeError(f"requested GPU backend is unavailable: {backend}")
            self._torch = torch
            self._data = torch.from_numpy(data).to(device=backend)

    @classmethod
    def from_entities(
        cls,
        entities: Iterable[DXFEntity],
        *,
        backend: str = "numpy",
        precision: str = "float64",
    ) -> LineBatch:
        """Snapshot zero-thickness LINE entities, preserving their input order.

        Reject other entity types and nonzero thickness: only endpoints are
        represented. Entity edits after construction do not update this snapshot.
        """
        vertices = []
        for entity in entities:
            if entity.dxftype() != "LINE" or entity.dxf.get("thickness", 0.0) != 0.0:
                raise ValueError("expected only LINE entities with zero thickness")
            vertices.append((tuple(entity.dxf.start), tuple(entity.dxf.end)))
        data = np.asarray(vertices, dtype=np.float64).reshape((-1, 2, 3))
        return cls(data, backend=backend, precision=precision)

    @property
    def backend(self) -> str:
        return self._backend

    @property
    def precision(self) -> str:
        return self._precision

    def __len__(self) -> int:
        return len(self._data)

    def _host(self, data: Any) -> NDArray:
        if self._torch is None:
            return np.array(data, copy=True)
        return data.detach().cpu().numpy().copy()

    def to_numpy(self) -> NDArray:
        """Return an independent copy of the endpoints in host memory."""
        return self._host(self._data)

    def to_backend(self, backend: str, *, precision: str | None = None) -> LineBatch:
        """Copy the snapshot through host memory to another backend/precision."""
        return LineBatch(
            self.to_numpy(), backend=backend, precision=precision or self.precision
        )

    def transformed(self, matrix: Matrix44) -> LineBatch:
        """Return a new snapshot after an affine transform; retain its backend."""
        values = np.asarray(tuple(matrix), dtype=np.float64).reshape((4, 4))
        if not np.isfinite(values).all() or not np.array_equal(
            values[:, 3], (0, 0, 0, 1)
        ):
            raise ValueError("matrix must be finite and affine")
        values = values.astype(self.precision)
        if not np.isfinite(values).all():
            raise ValueError("matrix must be representable in the selected precision")
        # Matrix44 uses row vectors and stores translation in the last row.
        if self._torch is None:
            # One matrix product avoids a separate tiny product for every line.
            # The result owns its data, so translation can be applied in place.
            data = self._data.reshape((-1, 3)) @ values[:3, :3]
            data += values[3, :3]
            data = data.reshape((-1, 2, 3))
        else:
            tensor = self._torch.from_numpy(values).to(device=self._data.device)
            data = self._data @ tensor[:3, :3] + tensor[3, :3]
        finite = (
            np.isfinite(data).all()
            if self._torch is None
            else self._torch.isfinite(data).all().item()
        )
        if not finite:
            raise ValueError("transformation produced non-finite coordinates")
        result = object.__new__(LineBatch)
        result._backend = self.backend
        result._precision = self.precision
        result._torch = self._torch
        result._data = data
        result._bounds = None
        return result

    def _get_bounds(self) -> Any:
        if self._bounds is None:
            if self._torch is None:
                # Exactly two endpoints: pairwise ufuncs avoid tiny reductions
                # per line, and output views avoid two full-size temporaries.
                bounds = np.empty_like(self._data)
                np.minimum(self._data[:, 0], self._data[:, 1], out=bounds[:, 0])
                np.maximum(self._data[:, 0], self._data[:, 1], out=bounds[:, 1])
                self._bounds = bounds
            else:
                self._bounds = self._torch.stack(
                    (self._data.amin(dim=1), self._data.amax(dim=1)), dim=1
                )
        return self._bounds

    def bounds(self) -> NDArray:
        """Return per-line minimum/maximum XYZ coordinates, shape ``(N, 2, 3)``."""
        return self._host(self._get_bounds())

    def extents(self) -> BoundingBox:
        """Return aggregate XYZ extents, or an empty box for an empty batch."""
        if not len(self):
            return BoundingBox()
        bounds = self._get_bounds()
        if self._torch is None:
            corners = np.array(
                [
                    [bounds[:, 0, axis].min() for axis in range(3)],
                    [bounds[:, 1, axis].max() for axis in range(3)],
                ],
                dtype=self.precision,
            )
        else:
            corners = self._torch.stack(
                (bounds[:, 0].amin(dim=0), bounds[:, 1].amax(dim=0))
            )
        return BoundingBox(self._host(corners))

    def window_mask(
        self, p1: Sequence[float], p2: Sequence[float], *, mode: str = "overlap"
    ) -> NDArray[np.bool_]:
        """Return an inclusive XY bounding-box selection mask in input order.

        ``overlap`` tests box overlap, not exact line/rectangle intersection.
        ``inside`` requires the entire box inside; ``outside`` means no overlap.
        Window corners may be supplied in either order. Z is ignored.
        """
        if mode not in ("overlap", "inside", "outside"):
            raise ValueError("mode must be 'overlap', 'inside', or 'outside'")
        corners = np.asarray((tuple(p1)[:2], tuple(p2)[:2]), dtype=self.precision)
        if corners.shape != (2, 2) or not np.isfinite(corners).all():
            raise ValueError("window corners must contain finite XY coordinates")
        low, high = corners.min(axis=0), corners.max(axis=0)
        if self._torch is not None:
            low = self._torch.from_numpy(low).to(device=self._data.device)
            high = self._torch.from_numpy(high).to(device=self._data.device)
        bounds = self._get_bounds()
        if self._torch is None:
            lower, upper = (0, 1) if mode == "inside" else (1, 0)
            # Four one-dimensional comparisons avoid an (N, 2) temporary and
            # its per-row reduction. The returned mask is independently owned.
            selected = bounds[:, lower, 0] >= low[0]
            selected &= bounds[:, lower, 1] >= low[1]
            selected &= bounds[:, upper, 0] <= high[0]
            selected &= bounds[:, upper, 1] <= high[1]
            if mode == "outside":
                np.logical_not(selected, out=selected)
            return selected
        if mode == "inside":
            axes = (bounds[:, 0, :2] >= low) & (bounds[:, 1, :2] <= high)
        else:
            axes = (bounds[:, 1, :2] >= low) & (bounds[:, 0, :2] <= high)
        selected = axes.all(dim=1)
        if mode == "outside":
            selected = ~selected
        return self._host(selected)

    def select_window(
        self, p1: Sequence[float], p2: Sequence[float], *, mode: str = "overlap"
    ) -> NDArray[np.intp]:
        """Return selected input indices; use them with the original entity list."""
        return np.flatnonzero(self.window_mask(p1, p2, mode=mode))

    def synchronize(self) -> None:
        """Wait for pending device work, useful when measuring resident operations."""
        if self._torch is not None:
            if self.backend == "mps":
                self._torch.mps.synchronize()
            else:
                self._torch.cuda.synchronize(self._data.device)

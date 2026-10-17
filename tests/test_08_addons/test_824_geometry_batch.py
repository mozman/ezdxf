import numpy as np
import pytest

import ezdxf
from ezdxf.addons.geometry_batch import LineBatch
from ezdxf.math import BoundingBox, Matrix44


@pytest.fixture(
    params=[
        ("numpy", "float64"),
        ("numpy", "float32"),
        ("mps", "float32"),
        ("cuda", "float64"),
        ("cuda", "float32"),
    ]
)
def backend(request):
    name, precision = request.param
    if name != "numpy":
        torch = pytest.importorskip("torch")
        available = (
            torch.backends.mps.is_available()
            if name == "mps"
            else torch.cuda.is_available()
        )
        if not available:
            pytest.skip(f"{name} unavailable")
    return name, precision


def make_batch(vertices, backend):
    return LineBatch(vertices, backend=backend[0], precision=backend[1])


def test_transform_bounds_and_selection_match_scalar_reference(backend):
    rng = np.random.default_rng(693)
    vertices = rng.uniform(-50, 50, (1000, 2, 3))
    matrix = Matrix44.chain(
        Matrix44.scale(2, -3, 0.5),
        Matrix44.z_rotate(0.7),
        Matrix44.translate(2, 7, -11),
    )
    original = make_batch(vertices, backend)
    transformed = original.transformed(matrix)
    expected = np.array(
        [tuple(matrix.transform(v)) for v in vertices.reshape(-1, 3)]
    ).reshape(-1, 2, 3)
    tolerance = 3e-5 if backend[1] == "float32" else 1e-12
    np.testing.assert_allclose(
        transformed.to_numpy(), expected, rtol=tolerance, atol=tolerance
    )
    bounds = np.stack((expected.min(axis=1), expected.max(axis=1)), axis=1)
    np.testing.assert_allclose(
        transformed.bounds(), bounds, rtol=tolerance, atol=tolerance
    )
    extent = BoundingBox(expected.reshape(-1, 3))
    np.testing.assert_allclose(
        tuple(transformed.extents().extmin), tuple(extent.extmin), atol=tolerance
    )
    np.testing.assert_allclose(
        tuple(transformed.extents().extmax), tuple(extent.extmax), atol=tolerance
    )
    overlap = ((bounds[:, 1, :2] >= (-10, -20)) & (bounds[:, 0, :2] <= (30, 40))).all(
        axis=1
    )
    inside = ((bounds[:, 0, :2] >= (-10, -20)) & (bounds[:, 1, :2] <= (30, 40))).all(
        axis=1
    )
    np.testing.assert_array_equal(
        transformed.window_mask((30, 40), (-10, -20)), overlap
    )
    np.testing.assert_array_equal(
        transformed.window_mask((-10, -20), (30, 40), mode="inside"), inside
    )
    np.testing.assert_array_equal(
        transformed.window_mask((-10, -20), (30, 40), mode="outside"), ~overlap
    )
    np.testing.assert_array_equal(
        transformed.select_window((-10, -20), (30, 40)), np.flatnonzero(overlap)
    )
    np.testing.assert_allclose(
        original.to_numpy(), vertices, rtol=tolerance, atol=tolerance
    )
    assert transformed.backend == backend[0]
    assert transformed.precision == backend[1]
    transformed.synchronize()


def test_empty_and_degenerate_batches(backend):
    empty = make_batch(np.empty((0, 2, 3)), backend)
    assert len(empty) == 0
    assert empty.bounds().shape == (0, 2, 3)
    assert empty.window_mask((0, 0), (1, 1)).shape == (0,)
    assert not empty.extents().has_data
    assert len(empty.transformed(Matrix44())) == 0
    point = make_batch([[(1, 1, 7), (1, 1, 7)]], backend)
    assert point.window_mask((0, 0), (1, 1)).tolist() == [True]
    assert point.window_mask((1, 1), (1, 1), mode="inside").tolist() == [True]


def test_snapshot_ownership_and_transfer(backend):
    vertices = np.arange(12, dtype=np.float64).reshape(2, 2, 3)
    expected = vertices.copy()
    batch = make_batch(vertices, backend)
    vertices[:] = 0
    output = batch.to_numpy()
    output[:] = 0
    bounds = batch.bounds()
    bounds[:] = 0
    np.testing.assert_array_equal(batch.to_numpy(), expected)
    assert batch.bounds().sum() != 0
    copied = batch.to_backend("numpy", precision="float64")
    np.testing.assert_array_equal(copied.to_numpy(), expected)
    assert copied.backend == "numpy"
    assert copied.precision == "float64"


def test_entities_are_snapshots_in_input_order(backend):
    doc = ezdxf.new()
    msp = doc.modelspace()
    first = msp.add_line((2, 3, 4), (5, 6, 7))
    second = msp.add_line((20, 30, 40), (50, 60, 70))
    batch = LineBatch.from_entities(
        iter([second, first]), backend=backend[0], precision=backend[1]
    )
    first.dxf.start = (99, 99, 99)
    assert batch.to_numpy()[1, 0].tolist() == [2, 3, 4]
    assert batch.select_window((0, 0), (10, 10)).tolist() == [1]
    with pytest.raises(ValueError, match="zero thickness"):
        LineBatch.from_entities(
            [msp.add_line((0, 0), (1, 1), dxfattribs={"thickness": 2})]
        )
    with pytest.raises(ValueError, match="LINE"):
        LineBatch.from_entities([msp.add_circle((0, 0), 1)])
    assert len(LineBatch.from_entities([])) == 0


@pytest.mark.parametrize(
    "vertices",
    [
        [],
        np.zeros((2, 3)),
        np.zeros((2, 2, 2)),
        [[[np.nan, 0, 0], [0, 0, 0]]],
        [[[0, 0, 0], [np.inf, 0, 0]]],
    ],
)
def test_invalid_vertices(vertices):
    with pytest.raises(ValueError):
        LineBatch(vertices)


def test_explicit_precision_and_validation():
    vertices = [[(1e8, 0, 0), (1e8 + 1, 1, 0)]]
    exact = LineBatch(vertices)
    approximate = LineBatch(vertices, precision="float32")
    assert exact.to_numpy()[0, 1, 0] - exact.to_numpy()[0, 0, 0] == 1
    assert approximate.to_numpy()[0, 1, 0] - approximate.to_numpy()[0, 0, 0] == 0
    # float32 can turn a disjoint window into an apparent boundary contact.
    assert exact.window_mask((1e8 + 2, -1), (1e8 + 3, 2)).tolist() == [False]
    assert approximate.window_mask((1e8 + 2, -1), (1e8 + 3, 2)).tolist() == [True]
    with pytest.raises(ValueError, match="explicit"):
        LineBatch(vertices, backend="mps")
    with pytest.raises(ValueError, match="precision"):
        LineBatch(vertices, precision="float16")
    with pytest.raises(ValueError, match="backend"):
        LineBatch(vertices, backend="automatic")
    with pytest.raises(ValueError, match="mode"):
        exact.window_mask((0, 0), (1, 1), mode="invalid")
    with pytest.raises(ValueError, match="finite"):
        exact.window_mask((np.nan, 0), (1, 1))
    with pytest.raises(ValueError, match="affine"):
        exact.transformed(Matrix44.perspective_projection(-1, 1, -1, 1, 1, 10))
    with pytest.raises(ValueError, match="finite"):
        exact.transformed(Matrix44.translate(np.inf, 0, 0))


def test_numpy_does_not_import_torch():
    import subprocess
    import sys

    script = (
        "from ezdxf.addons.geometry_batch import LineBatch; import sys; "
        "LineBatch([[(0,0,0),(1,1,1)]]).extents(); assert 'torch' not in sys.modules"
    )
    subprocess.run([sys.executable, "-c", script], check=True)


def test_affine_validation_precedes_precision_conversion():
    batch = LineBatch([[(0, 0, 0), (1, 1, 1)]], precision="float32")
    matrix = Matrix44()
    matrix[3, 3] = 1.00000001
    with pytest.raises(ValueError, match="affine"):
        batch.transformed(matrix)


def test_transform_overflow_is_rejected(backend):
    large = 2e38 if backend[1] == "float32" else 1e308
    batch = make_batch([[(large, 0, 0), (large, 1, 0)]], backend)
    with np.errstate(over="ignore", invalid="ignore"):
        with pytest.raises(ValueError, match="non-finite"):
            batch.transformed(Matrix44.scale(4))


def test_cuda_batch_retains_its_original_device():
    torch = pytest.importorskip("torch")
    if torch.cuda.device_count() < 2:
        pytest.skip("requires two CUDA devices")
    with torch.cuda.device(0):
        batch = LineBatch([[(0, 0, 0), (1, 1, 1)]], backend="cuda")
    with torch.cuda.device(1):
        result = batch.transformed(Matrix44.translate(2, 0, 0))
        assert result.window_mask((2, 0), (3, 1)).tolist() == [True]
        result.synchronize()

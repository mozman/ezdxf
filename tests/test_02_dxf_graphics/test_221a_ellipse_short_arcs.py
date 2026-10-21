import math

import numpy as np
import pytest

import ezdxf
from ezdxf.math import Matrix44


@pytest.mark.parametrize("start,span", [(0.3, 1e-10), (5.0, 4e-9), (6.28, 4e-9)])
@pytest.mark.parametrize(
    "matrix",
    [Matrix44(), Matrix44.translate(37, -18, 9), Matrix44.scale(2, 0.5, 1.5)],
)
def test_transform_preserves_short_ellipse_arc(tmp_path, start, span, matrix):
    doc = ezdxf.new("R2018")
    ellipse = doc.modelspace().add_ellipse(
        (3, -4, 5),
        major_axis=(1e6 * math.cos(0.3), 1e6 * math.sin(0.3), 0),
        ratio=0.7,
        start_param=start,
        end_param=start + span,
    )
    original = ellipse.construction_tool()
    expected = np.array(
        list(matrix.transform_vertices(original.vertices(original.params(9))))
    )
    ellipse.transform(matrix)
    tool = ellipse.construction_tool()
    actual = np.array(list(tool.vertices(tool.params(9))))
    error = min(
        np.max(np.linalg.norm(actual - expected, axis=1)),
        np.max(np.linalg.norm(actual[::-1] - expected, axis=1)),
    )
    assert error < 1e-7

    filename = tmp_path / "short_ellipse.dxf"
    doc.saveas(filename)
    restored = ezdxf.readfile(filename).modelspace().query("ELLIPSE").first
    assert restored.dxf.start_param == ellipse.dxf.start_param
    assert restored.dxf.end_param == ellipse.dxf.end_param


@pytest.mark.parametrize("start", [0, 0.3, 5.0])
@pytest.mark.parametrize("span", [math.tau, -math.tau, 0.0])
def test_transform_keeps_full_ellipse(start, span):
    ellipse = (
        ezdxf.new()
        .modelspace()
        .add_ellipse(
            (0, 0),
            major_axis=(5, 1),
            ratio=0.7,
            start_param=start,
            end_param=start + span,
        )
    )
    ellipse.transform(Matrix44.scale(2, 0.5, 1))
    assert ellipse.dxf.start_param == 0.0
    assert ellipse.dxf.end_param == math.tau

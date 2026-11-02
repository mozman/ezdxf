#  License: MIT License
import pytest

import math
import ezdxf
from ezdxf.math import Matrix44

ARC = dict(
    major_axis=(0.0077, 0.0184, 0), ratio=0.2741, start_param=1e-10, end_param=0.2618
)


def count(e):
    return len(list(e.flattening(0.01)))


def test_flattening_at_origin():
    doc = ezdxf.new()
    msp = doc.modelspace()

    at_origin = msp.add_ellipse(center=(0, 0), **ARC)
    assert count(at_origin) == 9


def test_flattening_far_from_center():
    doc = ezdxf.new()
    msp = doc.modelspace()

    far = msp.add_ellipse(center=(179269.58, 666945.74), **ARC)
    assert count(far) == 9


def test_flattening_at_origin_wrapped():
    doc = ezdxf.new()
    msp = doc.modelspace()

    wrapped = msp.add_ellipse(
        center=(0, 0),
        major_axis=(150, 0, 0),
        ratio=0.5,
        start_param=1.5 * math.pi,
        end_param=3.5 * math.pi,
    )
    assert count(wrapped) == 309


def test_flattening_at_origin_wrapped_near_tau():
    doc = ezdxf.new()
    msp = doc.modelspace()

    near_tau = msp.add_ellipse(
        center=(0, 0),
        major_axis=(150, 0, 0),
        ratio=0.5,
        start_param=0.0,
        end_param=math.tau + 5e-14,
    )
    assert count(near_tau) == 309


def test_flattening_translated_wrapped_near_tau():
    doc = ezdxf.new()
    msp = doc.modelspace()
    end_param = math.tau + 5e-14
    near_tau = msp.add_ellipse(
        center=(0, 0),
        major_axis=(150, 0, 0),
        ratio=0.5,
        start_param=0.0,
        end_param=end_param,
    )
    translated = near_tau.transform(Matrix44.translate(1, 0, 0))
    assert pytest.approx(translated.dxf.start_param) == 0
    assert pytest.approx(translated.dxf.start_param) == end_param % math.tau
    assert count(translated) == 9


if __name__ == "__main__":
    pytest.main([__file__])

# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License

from typing import Iterable
import pathlib
import math
import ezdxf
from ezdxf import zoom
from ezdxf.math import (
    Vec3,
    estimate_tangents,
    linspace,
    estimate_end_tangent_magnitude,
)
from ezdxf.math import (
    local_cubic_bspline_interpolation,
    global_bspline_interpolation,
    fit_points_to_cad_cv,
)

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def sine_wave(count: int, scale: float = 1.0) -> Iterable[Vec3]:
    for t in linspace(0, math.tau, count):
        yield Vec3(t * scale, math.sin(t) * scale)


def main(method="5-p"):
    """

    Args:
        method: tangent estimation method

    """
    doc = ezdxf.new()
    msp = doc.modelspace()

    # Calculate 8 points on sine wave as interpolation data
    data = list(sine_wave(count=8, scale=2.0))

    # --------------------------------------------------------------------------
    # Reference curve as approximation
    msp.add_lwpolyline(
        sine_wave(count=800, scale=2.0),
        dxfattribs={"color": 1, "layer": "Reference curve (LWPolyline)"},
    )

    # Add spline as fit-points: control point calculation by AutoCAD/BricsCAD
    msp.add_spline(data, dxfattribs={"layer": "BricsCAD B-spline", "color": 2})

    # --------------------------------------------------------------------------
    # estimated curve tangents
    # docs: https://ezdxf.mozman.at/docs/math/core.html#ezdxf.math.estimate_tangents
    # disable normalization for better results of the tangent visualization
    tangents = estimate_tangents(data, method, normalize=False)

    # display tangents
    for p, t in zip(data, tangents):
        msp.add_line(
            p,
            p + t,
            dxfattribs={"color": 5, "layer": f"Estimated tangents ({method})"},
        )

    # --------------------------------------------------------------------------
    # local interpolation with estimated curve tangents
    # a normalized tangent vector for each data point is required
    # docs: https://ezdxf.mozman.at/docs/math/core.html#ezdxf.math.local_cubic_bspline_interpolation
    s = local_cubic_bspline_interpolation(
        data, tangents=[t.normalize() for t in tangents]
    )

    # alternative: set argument 'method' for automatic tangent estimation,
    # default method is'5-points' interpolation
    # s = local_cubic_bspline_interpolation(data, method=method)

    msp.add_spline(
        dxfattribs={"color": 3, "layer": f"Local interpolation ({method})"}
    ).apply_construction_tool(s)

    # --------------------------------------------------------------------------
    # global interpolation: take first and last vector from 'tangents' as start-
    # and end tangent
    # docs: https://ezdxf.mozman.at/docs/math/core.html#ezdxf.math.global_bspline_interpolation
    m1, m2 = estimate_end_tangent_magnitude(data, method="chord")
    s = global_bspline_interpolation(
        data, tangents=(tangents[0].normalize(m1), tangents[-1].normalize(m2))
    )
    msp.add_spline(
        dxfattribs={"color": 4, "layer": f"Global interpolation ({method})"}
    ).apply_construction_tool(s)

    # --------------------------------------------------------------------------
    # fit_points_to_cad_cv(): this function tries to replicate the control-vertices
    # calculation of CAD applications. Works perfect if the start and end-tangent
    # is defined, but diverges from the CAD result to some degree otherwise.
    #
    # docs: https://ezdxf.mozman.at/docs/math/core.html#ezdxf.math.fit_points_to_cad_cv
    s = fit_points_to_cad_cv(data)
    msp.add_spline(
        dxfattribs={"color": 6, "layer": f"recreate CAD calculation"}
    ).apply_construction_tool(s)

    zoom.extents(msp, factor=1.1)
    doc.saveas(CWD / f"sine-wave-{method}.dxf")


if __name__ == "__main__":
    main()

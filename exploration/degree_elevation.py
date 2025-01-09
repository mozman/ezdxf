# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
import math
from pathlib import Path
import numpy as np

import ezdxf
from ezdxf.math import BSpline
from ezdxf.math.linalg import binomial_coefficient

OUTBOX = Path("~/Desktop/Outbox").expanduser()
if not OUTBOX.exists():
    OUTBOX = Path(".")

CONTROL_POINTS = [(0, 0), (1, -1), (2, 0), (3, 2), (4, 0), (5, -2)]


def degree_elevation(spline: BSpline, times: int) -> BSpline:
    # Piegl & Tiller: Algorithm A5.9
    # Degree elevate a curve t times
    # n: count of control points
    # p: degree of B-spline
    # Pw control points
    # U: knot vector
    t = int(times)
    if t < 1:
        return spline

    p = spline.degree
    if spline.is_rational:
        dim = 4
        # rational splines: (x, y, z, w)
        Pw = np.array(
            [v.x, v.y, v.z, w] for v, w in zip(spline.control_points, spline.weights())
        )
    else:
        dim = 3
        # non-rational splines: (x, y, z)
        Pw = np.array(spline.control_points)

    U = np.array(spline.knots())
    n = len(Pw) - 1  # text book n+1 == count of control points!
    m = n + p + 1
    ph = p + t
    ph2 = ph // 2

    # control points of the elevated B-spline
    Qw = np.zeros(shape=((n + 1) * (2 + t), dim))  # size not known yet???

    # knot vector of the elevated B-spline
    Uh = np.zeros(m * (2 + t))  # size not known yet???

    # coefficients for degree elevating the Bezier segments
    bezalfs = np.zeros(shape=(p + t + 1, p + 1))

    # This algorithm run for each axis: x, y, z
    # Bezier control points of the current segment
    bpts = np.zeros(shape=(p + 1, dim))

    # (p+t)th-degree Bezier control points of the current segment
    ebpts = np.zeros(shape=(p + t + 1, dim))

    # leftmost control points of the next Bezier segment
    Nextbpts = np.zeros(shape=(p - 1, dim))

    # knot insertion alphas
    alfs = np.zeros(p - 1)
    bezalfs[0, 0] = 1.0
    bezalfs[ph, p] = 1.0
    for i in range(1, ph2 + 1):
        inv = 1.0 / binomial_coefficient(ph, i)
        mpi = min(p, i)
        for j in range(max(0, i - t), mpi + 1):
            bezalfs[i, j] = (
                inv * binomial_coefficient(p, j) * binomial_coefficient(t, i - j)
            )
    for i in range(ph2 + 1, ph):
        mpi = min(p, i)
        for j in range(max(0, i - t), mpi + 1):
            bezalfs[i, j] = bezalfs[ph - i, p - j]
    mh = ph
    kind = ph + 1
    r = -1
    a = p
    b = p + 1
    cind = 1
    ua = U[0]
    Qw[0] = Pw[0]
    for i in range(0, ph + 1):
        Uh[i] = ua

    for i in range(0, p + 1):
        bpts[i] = Pw[i]  # initialize first Bezier segment

    while b < m:  # big loop thru knot vector
        i = b
        while (b < m) and (math.isclose(U[b], U[b + 1])):
            b += 1
        mul = b - i + 1
        mh = mh + mul + t
        ub = U[b]
        oldr = r
        r = p - mul
        # insert knot u(b) r-times
        if oldr > 0:
            lbz = (oldr + 2) // 2
        else:
            lbz = 1
        if r > 0:
            rbz = ph - (r + 1) // 2
        else:
            rbz = ph
        if r > 0:
            # insert knot to get Bezier segment
            numer = ub - ua
            for k in range(p, mul, -1):
                alfs[k - mul - 1] = numer / (U[a + k] - ua)
            for j in range(1, r + 1):
                save = r - j
                s = mul + j
                for k in range(p, s - 1, -1):
                    bpts[k] = alfs[k - s] * bpts[k] + (1.0 - alfs[k - s]) * bpts[k - 1]
                Nextbpts[save] = bpts[p]
            # end of insert knot
        for i in range(lbz, ph + 1):
            # degree elevate bezier
            # only points lbz, .. ,ph are used below
            ebpts[i] = 0.0
            mpi = min(p, i)
            for j in range(max(0, i - t), mpi + 1):
                ebpts[i] = ebpts[i] + bezalfs[i, j] * bpts[j]
            # end degree elevate bezier
        if oldr > 1:
            # must remove knot u=U[a] oldr times
            first = kind - 2
            last = kind
            den = ub - ua
            bet = (ub - Uh[kind - 1]) / den
            for tr in range(1, oldr):
                # knot removal loop
                i = first
                j = last
                kj = j - kind + 1
                while j - i > tr:
                    # loop and compute new control points for one removal step
                    if i < cind:
                        alf = (ub - Uh[i]) / (ua - Uh[i])
                        Qw[i] = alf * Qw[i] + (1.0 - alf) * Qw[i - 1]
                    if j >= lbz:
                        if j - tr <= kind - ph + oldr:
                            gam = (ub - Uh[j - tr]) / den
                            ebpts[kj] = gam * ebpts[kj] + (1.0 - gam) * ebpts[kj + 1]
                        else:
                            ebpts[kj] = bet * ebpts[kj] + (1.0 - bet) * ebpts[kj + 1]
                    i += 1
                    j -= 1
                    kj -= 1
                first -= 1
                last += 1
            # end of removing knot, u=U[a]
        if a != p:
            # load the knot ua
            for i in range(0, ph - oldr):
                Uh[kind] = ua
                kind = kind + 1
        for j in range(lbz, rbz + 1):
            # load control points into Qw
            Qw[cind] = ebpts[j]
            cind = cind + 1
        if b < m:
            # set up for next pass thru loop
            # np: bpts[:r] = Nextbpts[:r]
            for j in range(0, r):
                bpts[j] = Nextbpts[j]

            # np: bpts[r : p+1] = Pw[b-p+r : b+1]
            for j in range(r, p + 1):
                bpts[j] = Pw[b - p + j]
            a = b
            b += 1
            ua = ub
        else:  # end knot
            # np: Uh[kind : kind+ph+1] = ub
            for i in range(0, ph + 1):
                Uh[kind + i] = ub

    nh = mh - ph - 1
    count_cpts = nh + 1  # text book n+1 == count of control points
    order = ph + 1

    weights = []
    cpoints = Qw[:count_cpts, :3]
    if dim == 4:
        weights = Qw[:count_cpts, 3]
    return BSpline(
        cpoints, order=order, weights=weights, knots=Uh[: count_cpts + order]
    )


def test_algorithm_runs():
    spline = BSpline(CONTROL_POINTS)
    result = degree_elevation(spline, 1)

    assert result.degree == 4
    assert spline.control_points[0].isclose(result.control_points[0])
    assert spline.control_points[-1].isclose(result.control_points[-1])


def export_splines():
    spline = BSpline(CONTROL_POINTS)
    result = degree_elevation(spline, 1)

    doc = ezdxf.new()
    msp = doc.modelspace()
    s1 = msp.add_spline(dxfattribs={"layer": "original", "color": 1})
    s2 = msp.add_spline(dxfattribs={"layer": "elevated", "color": 2})
    s1.apply_construction_tool(spline)
    s2.apply_construction_tool(result)
    doc.saveas(OUTBOX / "degree_elevation.dxf")


if __name__ == "__main__":
    export_splines()

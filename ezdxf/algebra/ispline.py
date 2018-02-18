#coding:utf-8
# source: https://github.com/thibauts/b-spline
# author js code: thibauts (https://github.com/thibauts)
# License: MIT License


def interpolate_bspline(t, order, points, knots=None, weights=None):
    """
    B-spline interpolation of control points of any dimensionality using de Boor's algorithm.

    The interpolator can take an optional weight vector, making the resulting curve a Non-Uniform Rational B-Spline
    (NURBS) curve if you wish so.

    The knot vector is optional too, and when not provided an unclamped uniform knot vector will be generated internally.

    Args:
        t: position along the curve in the [0, 1] range
        order: order of the curve. Must be less than or equal to the number of control points. 2 is linear, 3 is
               quadratic, 4 is cubic, and so on.
        points: control points that will be interpolated. Can be vectors of any dimensionality ([x, y],
                [x, y, z], ...)
        knots: optional knot vector. Allow to modulate the control points interpolation spans on t. Must be a
               non-decreasing sequence of number of points + order length values.
        weights: optional control points weights. Must be the same length as the control point array.

    Returns:
        tuple (x, y[, z]), same dimension as points
    """
    if not (0. <= t <= 1.):
        raise ValueError('t is out of range [0, 1]')
    pcount = len(points)  # points count
    dimension = len(points[0])  # point dimensionality

    if order < 2:
        raise ValueError('order must be at least 2 (linear)')
    if order > pcount:
        raise ValueError('order must be less than point count')

    if weights is None:  # build weight vector
        weights = (1.,) * pcount
    elif len(weights) != pcount:
        raise ValueError('bad weight vector length')

    if knots is None:  # build knot vector
        knots = list(range(pcount+order))
    elif len(knots) != pcount+order:
        raise ValueError('bad knot vector length')

    domain = (order-1, len(knots)-order)

    # remap t to the domain where the spline is defined
    low = knots[domain[0]]
    high = knots[domain[1]]
    t = t * (high - low) + low

    for s in range(domain[0], domain[1]):
        if knots[s] <= t <= knots[s+1]:
            break

    # convert points to homogeneous coordinates
    v = []
    for i in range(pcount):
        w = []
        for j in range(dimension):
            w.append(points[i][j] * weights[i])
        w.append(weights[i])
        v.append(w)

    # level goes from 1 to the curve order
    for level in range(1, order+1):
        # build level l of the pyramid
        for i in range(s, s-order+level, -1):
            a = (t - knots[i]) / (knots[i+order-level] - knots[i])

            # interpolate each component
            for j in range(dimension+1):
                v[i][j] = (1 - a) * v[i-1][j] + a * v[i][j]

    # convert back to cartesian and return
    result = []
    for i in range(dimension):
        result.append(v[s][i] / v[s][dimension])

    return tuple(result)


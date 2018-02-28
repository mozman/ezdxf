# Purpose: 2d/3d spline defined by fit points
# Created: 26.03.2010
# License: MIT License
# Source: http://www-lehre.informatik.uni-osnabrueck.de/~cg/2000/skript/7_2_Splines.html
from ezdxf.algebra.vector import distance, Vector


def distance_t_array(points, func=lambda x: x):
    def distances():
        for p1, p2 in zip(points, points[1:]):
            yield distance(p1, p2)

    t = [0.]
    for d in distances():
        t.append(t[-1] + func(d))
    return t


def uniform_t_array(points):
    return list(range(len(points)))


class CubicSpline(object):
    """
    2d/3d cubic spline interpolation through fit points.

    2d in -> 2d out
    3d in -> 3d out

    Args:
        points: list of 2d/3d points as tuples (x, y[, z])
        method: 'uniform', 'distance' or lambda function with one argument, argument is point distance

    """
    def __init__(self, points, method='distance'):
        self.spatial = any(len(point) > 2 for point in points)  # 2d or 3d
        self.fit_points = [Vector(p) for p in points]  # Vector() has always 3 axis
        if method == 'uniform':
            self.t_array = uniform_t_array(self.fit_points)
        elif method == 'distance':
            self.t_array = distance_t_array(self.fit_points, func=lambda x: x)
        else:
            self.t_array = distance_t_array(self.fit_points, func=method)

    @property
    def count(self):
        return len(self.fit_points)

    def approximate(self, count):
        """
        Approximate spline curve with count vertices.

        Generates count 2d/3d points

        """
        def axis(index):
            return [p[index] for p in self.fit_points]

        if self.spatial:
            return zip(
                self._cubic_spline(axis(0), count),  # x-axis
                self._cubic_spline(axis(1), count),  # y-axis
                self._cubic_spline(axis(2), count),  # z-axis
            )
        else:
            return zip(
                self._cubic_spline(axis(0), count),  # x-axis
                self._cubic_spline(axis(1), count),  # y-axis
            )

    def _create_array(self):
        return [0.] * self.count

    def _cubic_spline(self, axis_vector, count):
        def get_delta_t_D(f):
            delta_t = self._create_array()
            D = self._create_array()
            for i in nrange:
                delta_t[i] = t[i] - t[i-1]
                D[i] = (f[i] - f[i-1])/delta_t[i]
            delta_t[0] = t[2] - t[0]
            return delta_t, D

        def get_k_m(D, delta_t):
            m = self._create_array()
            k = self._create_array()
            h = delta_t[1]
            m[0] = delta_t[2]
            k[0] = ((h + 2 * delta_t[0]) * D[1] * delta_t[2] + h * h * D[2]) / delta_t[0]
            for i in nrange[1:-1]:
                h = -delta_t[i+1] / m[i-1]
                k[i] = h * k[i-1] + 3 * (delta_t[i] * D[i+1] + delta_t[i+1] * D[i])
                m[i] = h * delta_t[i-1] + 2 * (delta_t[i] + delta_t[i+1])

            h = t[n-1] - t[n-3]
            dh = delta_t[n-1]
            k[n-1] = ((dh + h + h) * D[n-1] * delta_t[n-2] + dh * dh * D[n-2]) / h
            h = -h / m[n-2]
            m[n-1] = (h + 1.) * delta_t[n-2]
            return k, m

        def get_a(k, m, delta_t):
            a = self._create_array()
            h = (t[n-1] - t[n-3]) / -m[n-2]
            a[n-1] = (h * k[n-2] + k[n-1]) / m[n-1]
            for i in reversed(nrange[:-1]):
                a[i] = (k[i] - delta_t[i] * a[i+1]) / m[i]
            return a

        def get_b_c(a, D, delta_t):
            b = self._create_array()
            c = self._create_array()
            for i in nrange[1:]:
                dh = D[i]
                bh = delta_t[i]
                e = a[i-1] + a[i] - 2. * dh
                b[i-1] = 2. * (dh - a[i-1] - e) / bh
                c[i-1] = 6. * e / (bh * bh)
            return b, c

        n = self.count
        t = self.t_array

        nrange = list(range(n))

        delta_t, D = get_delta_t_D(axis_vector)
        k, m = get_k_m(D, delta_t)
        a = get_a(k, m, delta_t)
        b, c = get_b_c(a, D, delta_t)

        wt = 0.
        j = 0
        dt = t[-1] / float(count - 1)
        for _ in range(count - 1):
            while (j <= n) and (t[j+1] < wt):
                j += 1
            h = wt - t[j]
            yield axis_vector[j] + h * (a[j] + h * (b[j] + h * c[j] / 3.) / 2.)
            wt += dt
        yield axis_vector[-1]

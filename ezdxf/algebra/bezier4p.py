# Purpose: Bezier Curve optimized for 4 control points
# Created: 26.03.2010
# License: MIT License


class Bezier4P(object):
    """
    Implements an optimized Cubic Bezier Curve with 4 control points.

    Special behavior: 2D in -> 2D out and 3D in -> 3D out!

    """
    def __init__(self, control_points):
        if len(control_points) == 4:
            dim = max([len(p) for p in control_points])
            if dim < 3:
                self.math = D2D  # use 2d math module
            else:
                self.math = D3D  # use 3d math module
            self._cpoints = [self.math.tovector(vector) for vector in control_points]
        else:
            raise ValueError("Four control points required.")

    @property
    def breakpoints(self):
        return self._cpoints

    def get_tangent(self, position):
        self._check(position)
        return self._get_curve_tangent(position)

    def get_point(self, position):
        self._check(position)
        return self._get_curve_point(position)

    def approximate(self, segments):
        delta_t = 1. / segments
        yield self._cpoints[0]
        for segment in range(1, segments):
            yield self.get_point(delta_t*segment)
        yield self._cpoints[3]

    def _check(self, position):
        if not(0 <= position <= 1.):
            raise ValueError("position not in range [0 to 1]")

    def _get_curve_point(self, t):
        """
        Implementation optimized for 4 control points.

        """
        b1, b2, b3, b4 = self._cpoints
        one_minus_t = 1. - t
        m = self.math
        B = m.vmul_scalar(b1, one_minus_t**3)
        B = m.vadd(B, m.vmul_scalar(b2, 3. * one_minus_t**2 * t))
        B = m.vadd(B, m.vmul_scalar(b3, 3. * one_minus_t * t**2))
        B = m.vadd(B, m.vmul_scalar(b4, t**3))
        return B

    def _get_curve_tangent(self, t):
        """
        Implementation optimized for 4 control points.

        Returns a vector T which defines the direction of the tangent.
        example: slope of tangent = (y) T[1]/ (x) T[0]
        position of tangent point is defined by the parameter t -> get_curve_point_by_parameter()
        """
        b1, b2, b3, b4 = self._cpoints
        m = self.math
        B = m.vmul_scalar(b1, -3. * (1. - t)**2)
        B = m.vadd(B, m.vmul_scalar(b2, 3. * (1. - 4. * t + 3. * t**2)))
        B = m.vadd(B, m.vmul_scalar(b3, 3. * t * (2. - 3. * t)))
        B = m.vadd(B, m.vmul_scalar(b4, 3. * t**2))
        return B

    def approximated_length(self, segments=100):
        length = 0.
        point_gen = self.approximate(segments)
        prev_point = next(point_gen)
        distance = self.math.distance
        for point in point_gen:
            length += distance(prev_point, point)
            prev_point = point
        return length


class D2D(object):
    @staticmethod
    def vadd(vector1, vector2):
        """ Add vectors """
        return vector1[0]+vector2[0], vector1[1]+vector2[1]

    @staticmethod
    def vmul_scalar(vector, scalar):
        """ Mul vector with scalar """
        return vector[0]*scalar, vector[1]*scalar

    @staticmethod
    def tovector(vector):
        """ Return a 2d point """
        return float(vector[0]), float(vector[1])

    @staticmethod
    def distance(point1, point2):
        """ calc distance between two 2d points """
        return ((point1[0]-point2[0])**2 +
                (point1[1]-point2[1])**2)**0.5


class D3D(object):
    @staticmethod
    def vadd(vector1, vector2):
        """ Add vectors """
        return vector1[0]+vector2[0], vector1[1]+vector2[1], vector1[2]+vector2[2]

    @staticmethod
    def vmul_scalar(vector, scalar):
        """ Mul vector with scalar """
        return vector[0]*scalar, vector[1]*scalar, vector[2]*scalar

    @staticmethod
    def tovector(vector):
        """ Return a 3d point """
        return float(vector[0]), float(vector[1]), float(vector[2])

    @staticmethod
    def distance(point1, point2):
        """Calc distance between two 3d points """
        return ((point1[0]-point2[0])**2 +
                (point1[1]-point2[1])**2 +
                (point1[2]-point2[2])**2)**0.5

# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.math import (
    is_planar_face,
    Vec3,
    Vec2,
    subdivide_face,
    intersection_ray_ray_3d,
    normal_vector_3p,
    NULLVEC,
    X_AXIS,
    Y_AXIS,
    Z_AXIS,
    subdivide_ngons,
    distance_point_line_3d,
    best_fit_normal,
    Matrix44,
    BarycentricCoordinates,
    linear_vertex_spacing,
)

from ezdxf.render.forms import square, circle

REGULAR_FACE = Vec3.list([(0, 0, 0), (1, 0, 1), (1, 1, 1), (0, 1, 0)])
IRREGULAR_FACE = Vec3.list([(0, 0, 0), (1, 0, 1), (1, 1, 0), (0, 1, 0)])
REGULAR_FACE_WRONG_ORDER = Vec3.list(
    [(0, 0, 0), (1, 1, 1), (1, 0, 1), (0, 1, 0)]
)


def test_face_count():
    assert is_planar_face(REGULAR_FACE[:3]) is True
    assert is_planar_face(REGULAR_FACE[:2]) is False


def test_regular_face():
    assert is_planar_face(REGULAR_FACE) is True


def test_irregular_face():
    assert is_planar_face(IRREGULAR_FACE) is False


def test_does_not_detect_wrong_order():
    assert is_planar_face(REGULAR_FACE_WRONG_ORDER) is True


def test_subdivide_square_in_quads():
    b = square(2)
    result = list(subdivide_face(b, quads=True))
    assert len(result) == 4
    assert result[0] == ((0, 0), (1, 0), (1, 1), (0, 1))


def test_subdivide_square_in_triangles():
    b = square(2)
    result = list(subdivide_face(b, quads=False))
    assert len(result) == 8
    assert result[0] == ((0, 1), (0, 0), (1, 1))
    assert result[1] == ((0, 0), (1, 0), (1, 1))


def test_subdivide_triangle():
    t = Vec3.list([(0, 0), (2, 0), (1, 2)])
    assert len(list(subdivide_face(t, quads=True))) == 3
    assert len(list(subdivide_face(t, quads=False))) == 6


def test_subdivide_ngons():
    hexagon = list(circle(6))
    result = list(subdivide_ngons([hexagon]))
    assert len(result) == 6


def test_subdivide_vec2_square_in_quads():
    b = Vec2.list(square(2))
    result = list(subdivide_face(b, quads=True))
    assert len(result) == 4
    assert result[0] == ((0, 0), (1, 0), (1, 1), (0, 1))


def test_intersection_ray_ray_3d_1():
    ray1 = (Vec3(0, 0, 0), Vec3(1, 0, 0))
    ray2 = (Vec3(0, 0, 0), Vec3(0, 0, 1))

    # parallel rays return a 0-tuple
    result = intersection_ray_ray_3d(ray1, ray1)
    assert len(result) == 0
    assert bool(result) is False

    # intersecting rays return a 1-tuple
    result = intersection_ray_ray_3d(ray1, ray2)
    assert len(result) == 1
    assert bool(result) is True
    assert result == (Vec3(0, 0, 0),)

    # not intersecting and not parallel rays return a 2-tuple
    line3 = (Vec3(0, 0, 1), Vec3(0, 1, 1))
    result = intersection_ray_ray_3d(ray1, line3)
    assert len(result) == 2
    assert bool(result) is True
    # returns points of closest approach on each ray
    assert Vec3(0, 0, 1) in result
    assert Vec3(0, 0, 0) in result


def test_intersection_ray_ray_3d_2():
    ray1 = (Vec3(1, 0, 0), Vec3(1, 1, 0))
    ray2 = (Vec3(0, 0.5, 0), Vec3(1, 0.5, 0))
    result = intersection_ray_ray_3d(ray1, ray2)
    assert len(result) == 1


def test_intersection_ray_ray_3d_random():
    for _ in range(5):
        intersection_point = Vec3.random(5)
        ray1 = (intersection_point, intersection_point + Vec3.random())
        ray2 = (intersection_point, intersection_point - Vec3.random())

        result = intersection_ray_ray_3d(ray1, ray2)
        assert len(result) == 1
        assert result[0].isclose(intersection_point)


RH_ORTHO = [
    (NULLVEC, X_AXIS, Y_AXIS, Z_AXIS),
    (NULLVEC, Y_AXIS, X_AXIS, -Z_AXIS),
    (NULLVEC, Z_AXIS, X_AXIS, Y_AXIS),
    (NULLVEC, X_AXIS, Z_AXIS, -Y_AXIS),
    (NULLVEC, Y_AXIS, Z_AXIS, X_AXIS),
    (NULLVEC, Z_AXIS, Y_AXIS, -X_AXIS),
]


@pytest.mark.parametrize("a,b,c,r", RH_ORTHO)
def test_normal_vector_for_3_points(a, b, c, r):
    assert normal_vector_3p(a, b, c) == r


@pytest.mark.parametrize(
    "points, expected",
    [
        ([(10, 3), (0, 0), (1, 0)], 3),  # left of line
        ([(-10, 0), (0, 0), (1, 0)], 0),  # on line
        ([(2, -4), (0, 0), (1, 0)], 4),  # right of line
        ([(5, 0), (0, 5), (0, 2)], 5),
        ([(1, 0, 1), (1, 1, 1), (0, 0, 0)], 0.8164965809277259),
    ],
)
def test_distance_point_line_3d(points, expected):
    p, a, b = Vec3.generate(points)
    assert distance_point_line_3d(p, a, b) == pytest.approx(expected)


@pytest.mark.parametrize("x", [1e-99, 1e-9, 0, 1e9, 1e99])
def test_distance_point_line_3d_no_line(x):
    """Start point is equal or close to end point."""
    s = Vec3(1, 0, x)
    e = Vec3(1, 0, x)
    with pytest.raises(ZeroDivisionError):
        distance_point_line_3d(Vec3(1, 0, 0), s, e)


class TestBestFitNormal:
    @pytest.mark.parametrize("a,b,c,r", RH_ORTHO)
    def test_if_returns_right_handed_normals(self, a, b, c, r):
        assert best_fit_normal((a, b, c)) == r

    @pytest.fixture(scope="class")
    def vertices(self):
        return Vec3.list([(0, 0), (3, 0), (3, 4), (4, 8), (1, 5), (0, 2)])

    @pytest.fixture(scope="class")
    def matrix(self):
        return Matrix44.chain(
            Matrix44.x_rotate(0.75),
            Matrix44.translate(2, 3, 4),
        )

    def test_transformed_counter_clockwise_vertices_ccw(self, vertices, matrix):
        v = matrix.transform_vertices(vertices)
        normal = matrix.transform_direction(Z_AXIS)
        assert best_fit_normal(v).isclose(normal)

    def test_transformed_clockwise_vertices(self, vertices, matrix):
        v = matrix.transform_vertices(reversed(vertices))
        normal = matrix.transform_direction(-Z_AXIS)
        assert best_fit_normal(v).isclose(normal)


class TestBarycentricCoords:
    @pytest.fixture
    def bc(self):
        return BarycentricCoordinates((0, 0, 0), (5, 0, 0), (5, 4, 0))

    def test_basic_coords(self, bc):
        assert bc.from_cartesian(bc.a) == (1, 0, 0)
        assert bc.from_cartesian(bc.b) == (0, 1, 0)
        assert bc.from_cartesian(bc.c) == (0, 0, 1)

    def test_center_of_mass_property(self, bc):
        p = (bc.a + bc.b + bc.c) / 3
        b = bc.from_cartesian(p)
        assert b.isclose((1 / 3.0, 1 / 3.0, 1 / 3.0))

    @pytest.mark.parametrize("p", [(0, 4, 0), (0, -1, 0), (7, 0, 0)])
    def test_point_outside_triangle(self, bc, p):
        p = Vec3(p)
        b = bc.from_cartesian(p)
        assert any(b0 < 0 for b0 in b) is True
        assert sum(b) == pytest.approx(1.0)
        assert p.isclose(bc.to_cartesian(b))

    @pytest.mark.parametrize(
        "p",
        [
            # tests the normal projection of p onto (a, b, c)
            (4, 1, 0),
            (4, 1, 1),
            (4, 1, -1),
        ],
    )
    def test_point_inside_triangle(self, bc, p):
        b = bc.from_cartesian(p)
        assert all(0 <= b0 <= 1 for b0 in b) is True
        assert sum(b) == pytest.approx(1.0)


class TestLinearVertexSpacing:
    @pytest.mark.parametrize("count", [-1, 0, 1, 2, 3])
    def test_returns_always_two_or_more_vertices(self, count):
        assert len(linear_vertex_spacing(Vec3(), Vec3(1, 0), count)) >= 2

    def test_works_if_start_is_equal_to_end(self):
        assert len(linear_vertex_spacing(Vec3(), Vec3(), 5)) == 5

    @pytest.mark.parametrize("count", [2, 3, 4, 5])
    def test_correct_spacing_in_Q1(self, count):
        x = count - 1
        vertices = linear_vertex_spacing(Vec3(), Vec3(x, x, x), count)
        assert len(vertices) == count
        for x in range(count):
            assert vertices[x].isclose((x, x, x))

    @pytest.mark.parametrize("count", [2, 3, 4, 5])
    def test_correct_spacing_in_Q3(self, count):
        x = count - 1
        vertices = linear_vertex_spacing(Vec3(), Vec3(-x, -x, -x), count)
        assert len(vertices) == count
        for x in range(count):
            assert vertices[x].isclose((-x, -x, -x))


if __name__ == "__main__":
    pytest.main([__file__])

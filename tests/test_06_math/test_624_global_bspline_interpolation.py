from typing import List
import pytest
import ezdxf
import math
from math import isclose
from ezdxf.math import Vec3, global_bspline_interpolation, close_vectors
from ezdxf.math.parametrize import (
    uniform_t_vector, distance_t_vector, centripetal_t_vector, arc_t_vector,
    arc_distances, estimate_tangents,
)
from ezdxf.math.bspline import (
    knots_from_parametrization, required_knot_values,
    averaged_knots_unconstrained, natural_knots_constrained,
    averaged_knots_constrained,
    natural_knots_unconstrained, double_knots, create_t_vector, normalize_knots,
)

POINTS1 = Vec3.list([(1, 1), (2, 4), (4, 1), (7, 6)])
POINTS2 = Vec3.list([(1, 1), (2, 4), (4, 1), (7, 6), (5, 8), (3, 3), (1, 7)])


@pytest.fixture(params=[POINTS1, POINTS2])
def fit_points(request):
    return request.param


def test_uniform_t_array(fit_points):
    t_vector = list(uniform_t_vector(len(fit_points)))
    assert len(t_vector) == len(fit_points)
    assert t_vector[0] == 0.
    assert t_vector[-1] == 1.
    for t1, t2 in zip(t_vector, t_vector[1:]):
        assert t1 <= t2


def test_chord_length_t_array(fit_points):
    t_vector = list(distance_t_vector(fit_points))
    assert len(t_vector) == len(fit_points)
    assert t_vector[0] == 0.
    assert t_vector[-1] == 1.
    for t1, t2 in zip(t_vector, t_vector[1:]):
        assert t1 <= t2


def test_centripetal_length_t_array(fit_points):
    t_vector = list(centripetal_t_vector(fit_points))
    assert len(t_vector) == len(fit_points)
    assert t_vector[0] == 0.
    assert t_vector[-1] == 1.
    for t1, t2 in zip(t_vector, t_vector[1:]):
        assert t1 <= t2


def test_arc_distances():
    p = Vec3.list([(0, 0), (2, 2), (4, 0), (6, -2), (8, 0)])
    # p[1]..p[3] are a straight line, radius calculation fails and
    # a straight line from p[1] to p[2] is used as replacement
    # for the second arc
    radius = 2.0
    arc_length = math.pi * 0.5 * radius
    diagonal = math.sqrt(2.0) * radius
    distances = list(arc_distances(p))
    assert len(distances) == 4
    assert isclose(distances[0], arc_length)
    assert isclose(distances[1], diagonal)  # replacement for arc
    assert isclose(distances[2], arc_length)
    assert isclose(distances[3], arc_length)


def test_arc_length_t_array(fit_points):
    t_vector = list(arc_t_vector(fit_points))
    assert len(t_vector) == len(fit_points)
    assert t_vector[0] == 0.
    assert t_vector[-1] == 1.
    for t1, t2 in zip(t_vector, t_vector[1:]):
        assert t1 <= t2


def test_invalid_order_count_combination():
    count = 4
    order = 5
    with pytest.raises(ezdxf.DXFValueError):
        required_knot_values(count, order)
    with pytest.raises(ezdxf.DXFValueError):
        list(knots_from_parametrization(n=count - 1, p=order - 1, t=[]))


def check_knots(count: int, order: int, knots: List[float]):
    assert len(knots) == required_knot_values(count, order)
    assert len(set(knots[:order])) == 1, 'first order elements have to be equal'
    assert len(set(knots[-order:])) == 1, 'last order elements have to be equal'
    for k1, k2 in zip(knots, knots[1:]):
        assert k1 <= k2


@pytest.mark.parametrize('p', (2, 3, 4))
@pytest.mark.parametrize('method', ('average', 'natural'))
def test_knot_generation(p, method):
    fit_points = Vec3.list(
        [(0, 0), (0, 10), (10, 10), (20, 10), (20, 0), (30, 0), (30, 10),
         (40, 10), (40, 0)])
    count = len(fit_points)
    n = count - 1
    order = p + 1
    t_vector = distance_t_vector(fit_points)
    knots = list(knots_from_parametrization(n, p, t_vector, method))
    check_knots(n + 1, p + 1, knots)


@pytest.fixture
def fit_points_2():
    return Vec3.list(
        [(0, 0), (0, 10), (10, 10), (20, 10), (20, 0), (30, 0), (30, 10),
         (40, 10), (40, 0)])


@pytest.mark.parametrize('p', (2, 3, 4, 5))
def test_unconstrained_averaged_knots(p, fit_points_2):
    t_vector = list(distance_t_vector(fit_points_2))
    n = len(fit_points_2) - 1

    knots = averaged_knots_unconstrained(n, p, t_vector)
    check_knots(n + 1, p + 1, knots)


@pytest.mark.parametrize('p', (2, 3, 4, 5))
def test_constrained_averaged_knots(p, fit_points_2):
    t_vector = list(distance_t_vector(fit_points_2))
    n = len(fit_points_2) - 1

    # add 2 knots for tangents
    knots = averaged_knots_constrained(n + 2, p, t_vector)
    check_knots(n + 3, p + 1, knots)


@pytest.mark.parametrize('p', (2, 3, 4, 5))
def test_unconstrained_natural_knots(p, fit_points_2):
    t_vector = list(distance_t_vector(fit_points_2))
    n = len(fit_points_2) - 1

    # add 2 knots for tangents
    knots = natural_knots_unconstrained(n, p, t_vector)
    check_knots(n + 1, p + 1, knots)


@pytest.mark.parametrize('p', (2, 3, 4, 5))
def test_constrained_natural_knots(p, fit_points_2):
    t_vector = list(distance_t_vector(fit_points_2))
    n = len(fit_points_2) - 1

    # add 2 knots for tangents
    knots = natural_knots_constrained(n + 2, p, t_vector)
    check_knots(n + 3, p + 1, knots)


@pytest.mark.parametrize('p', (2, 3, 4, 5))
def test_double_knots(p, fit_points_2):
    t_vector = list(distance_t_vector(fit_points_2))
    n = len(fit_points_2) - 1

    # create knots for each control point and 1st derivative
    knots = double_knots(n, p, t_vector)
    check_knots((n + 1) * 2, p + 1, knots)



def test_bspline_interpolation(fit_points):
    spline = global_bspline_interpolation(fit_points, degree=3, method='chord')
    assert len(spline.control_points) == len(fit_points)

    t_array = list(create_t_vector(fit_points, 'chord'))
    assert t_array[0] == 0.
    assert t_array[-1] == 1.
    assert len(t_array) == len(fit_points)

    t_points = [spline.point(t) for t in t_array]
    assert close_vectors(t_points, fit_points)


def test_bspline_interpolation_first_derivatives(fit_points):
    tangents = estimate_tangents(fit_points)
    spline = global_bspline_interpolation(fit_points, degree=3,
                                          tangents=tangents)
    assert len(spline.control_points) == 2 * len(fit_points)


expected = [
    (0.0, 0.0),
    (0.010310831479728222, 0.32375901937484741),
    (0.030277278274297714, 0.6140977144241333),
    (0.059526983648538589, 0.87245100736618042),
    (0.097687594592571259, 1.1002539396286011),
    (0.14438676834106445, 1.2989413738250732),
    (0.19925214350223541, 1.469948410987854),
    (0.26191136240959167, 1.6147100925445557),
    (0.33199205994606018, 1.7346612215042114),
    (0.40912193059921265, 1.8312369585037231),
    (0.49292856454849243, 1.9058722257614136),
    (0.58303964138031006, 1.9600019454956055),
    (0.67908281087875366, 1.9950611591339111),
    (0.78068572282791138, 2.0124847888946533),
    (0.88747602701187134, 2.0137078762054443),
    (0.9990813136100769, 2.0001654624938965),
    (1.1151292324066162, 1.973292350769043),
    (1.2352476119995117, 1.9345237016677856),
    (1.3590638637542725, 1.8852944374084473),
    (1.4862056970596313, 1.8270395994186401),
    (1.6163008213043213, 1.761194109916687),
    (1.7489768266677856, 1.6891928911209106),
    (1.8838614225387573, 1.6124709844589233),
    (2.0205821990966797, 1.532463550567627),
    (2.1587669849395752, 1.4506052732467651),
    (2.2980430126190186, 1.3683313131332397),
    (2.4380383491516113, 1.2870765924453735),
    (2.5783803462982178, 1.2082761526107788),
    (2.7186968326568604, 1.1333650350570679),
    (2.8586153984069824, 1.0637780427932739),
    (2.9977638721466064, 1.0009502172470093),
    (3.1357693672180176, 0.94631654024124146),
    (3.2722601890563965, 0.90131211280822754),
    (3.4068636894226074, 0.86737185716629028),
    (3.5392072200775146, 0.84593069553375244),
    (3.6689188480377197, 0.83842372894287109),
    (3.795626163482666, 0.84628582000732422),
    (3.9189567565917969, 0.87095201015472412),
    (4.0385379791259766, 0.91385728120803833),
    (4.1539978981018066, 0.97643661499023438),
    (4.2649641036987305, 1.0601249933242798),
    (4.3710641860961914, 1.1663573980331421),
    (4.4719257354736328, 1.2965688705444336),
    (4.567176342010498, 1.4521942138671875),
    (4.6564435958862305, 1.6346687078475952),
    (4.7393555641174316, 1.8454270362854004),
    (4.8155393600463867, 2.0859043598175049),
    (4.8846230506896973, 2.3575356006622314),
    (4.9462337493896484, 2.6617558002471924),
    (5.0, 3.0)
]


def test_check_values():
    test_points = [(0., 0.), (1., 2.), (3., 1.), (5., 3.)]
    spline = global_bspline_interpolation(test_points, degree=3,
                                          method='distance')
    result = list(spline.approximate(49))
    assert len(result) == 50
    for p1, p2 in zip(result, expected):
        assert isclose(p1[0], p2[0], abs_tol=1e-6)
        assert isclose(p1[1], p2[1], abs_tol=1e-6)

import pytest
import ezdxf
from ezdxf.algebra.bspline import bspline_control_frame
from ezdxf.algebra.bspline import uniform_t_vector, distance_t_vector, centripetal_t_vector
from ezdxf.algebra.bspline import control_frame_knots, required_knot_values
from ezdxf.algebra.base import equals_almost

POINTS1 = [(1, 1), (2, 4), (4, 1), (7, 6)]
POINTS2 = [(1, 1), (2, 4), (4, 1), (7, 6), (5, 8), (3, 3), (1, 7)]


@pytest.fixture(params=[POINTS1, POINTS2])
def fit_points(request):
    return request.param


def test_uniform_t_array(fit_points):
    t_vector = list(uniform_t_vector(fit_points))
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


def test_invalid_order_count_combination():
    count = 4
    order = 5
    with pytest.raises(ezdxf.DXFValueError):
        required_knot_values(count, order)
    with pytest.raises(ezdxf.DXFValueError):
        list(control_frame_knots(n=count-1, p=order-1, t_vector=[]))


def test_control_frame_knot_values(fit_points):
    count = len(fit_points)
    n = count - 1
    degrees = (2, 3, 4) if len(fit_points) > 4 else (2, 3)
    for p in degrees:  # degree
        order = p + 1
        t_vector = uniform_t_vector(fit_points)
        knots = list(control_frame_knots(n, p, t_vector))
        assert len(knots) == required_knot_values(count, order)
        assert len(set(knots[:order])) == 1, 'first order elements have to be equal'
        assert len(set(knots[-order:])) == 1, 'last order elements have to be equal'
        for k1, k2 in zip(knots, knots[1:]):
            assert k1 <= k2


def test_control_frame(fit_points):
    spline = bspline_control_frame(fit_points, degree=3)
    assert len(spline.control_points) == len(fit_points)
    assert spline.t_array[0] == 0.
    assert spline.t_array[-1] == 1.
    assert len(spline.t_array) == len(fit_points)

    t_points = [spline.point(t) for t in spline.t_array]
    for p1, p2 in zip(t_points, fit_points):
        assert p1 == p2


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
    spline = bspline_control_frame(test_points, degree=3, method='distance')
    result = list(spline.approximate(49))
    assert len(result) == 50
    for p1, p2 in zip(result, expected):
        assert equals_almost(p1[0], p2[0], 4)
        assert equals_almost(p1[1], p2[1], 4)

# Author:  mozman
# Purpose: test convex_hull_2d
# Created: 28.02.2010
# License: MIT License
import pytest
from ezdxf.math.convexhull import convex_hull_2d
from io import StringIO


def import_asc_coords(file_obj):
    """ Import allplan asc-format point file.

    returns: a dictionary of Coordinates ('name': Coordinate)
    """
    points = dict()
    lines = file_obj.readlines()
    for line in lines:
        name, x, y, z, code = line.split()
        x = float(x)
        y = float(y)
        z = float(z)
        try:
            points[name] = (x, y, z)
        except ValueError:
            pass
    return points


def test_convex_hull_raises():
    with pytest.raises(ValueError):
        _ = convex_hull_2d([])
    with pytest.raises(ValueError):
        _ = convex_hull_2d([(0., 0.), (0., 0.)])
    with pytest.raises(ValueError):
        _ = convex_hull_2d([(0., 0.), (0., 0.), (0., 0.), (0., 0.)])


def test_convex_hull_set1():
    set1 = import_asc_coords(StringIO(cx_set1))
    hull = convex_hull_2d(set1.values())
    result_keys = ["3", "18", "19", "1", "7", "8", "2", "16", "17"]
    for result, result_key in zip(hull, result_keys):
        assert result == set1[result_key]


def test_convex_hull_set2():
    set2 = import_asc_coords(StringIO(cx_set2))
    hull = convex_hull_2d(set2.values())
    result_keys = ["1", "2", "8", "15"]
    for result, result_key in zip(hull, result_keys):
        assert result == set2[result_key]


def test_convex_hull_set3():
    set3 = import_asc_coords(StringIO(cx_set3))
    hull = convex_hull_2d(set3.values())
    result_keys = ["1", "7", "13"]
    for result, result_key in zip(hull, result_keys):
        assert result == set3[result_key]


# inline data files
cx_set1 = """                  1      4.000       8.000       0.000      0
                  2      9.000       3.000       0.000      0
                  3      1.000       4.000       0.000      0
                  4      5.000       5.000       0.000      0
                  5      3.000       7.000       0.000      0
                  6      2.000       5.000       0.000      0
                  7      7.000       7.000       0.000      0
                  8      9.000       5.000       0.000      0
                  9      5.000       3.000       0.000      0
                 10      6.000       6.000       0.000      0
                 11      3.000       6.000       0.000      0
                 12      7.000       4.000       0.000      0
                 13      8.000       3.000       0.000      0
                 14      6.000       2.000       0.000      0
                 15      4.000       2.000       0.000      0
                 16      7.000       1.000       0.000      0
                 17      4.000       1.000       0.000      0
                 18      1.000       5.000       0.000      0
                 19      2.000       7.000       0.000      0
"""
cx_set2 = """                  1     -7.000       1.000       0.000      0
                  2     -7.000       8.000       0.000      0
                  3      4.000       5.000       0.000      0
                  4     -6.128       4.000       0.000      0
                  5     -3.605       6.559       0.000      0
                  6     -3.672       4.781       0.000      0
                  7      1.645       4.680       0.000      0
                  8      5.000       8.000       0.000      0
                  9      1.543       6.356       0.000      0
                 10     -2.335       4.341       0.000      0
                 11     -3.757       2.648       0.000      0
                 12      2.559       2.000       0.000      0
                 13     -2.673       5.442       0.000      0
                 14      3.203       6.627       0.000      0
                 15      5.000       1.000       0.000      0
                 16     -2.910       1.000       0.000      0
                 17     -2.555       8.000       0.000      0
                 18      5.000       5.000       0.000      0
                 19     -7.000       6.000       0.000      0
                 20     -4.841       3.410       0.000      0
                 21     -5.349       6.221       0.000      0
                 22      0.375       4.460       0.000      0
"""
cx_set3 = """                  1     -8.000       8.000       0.000      0
                  2     -3.244       6.443       0.000      0
                  3      1.646       6.443       0.000      0
                  4     -6.000       8.000       0.000      0
                  5      2.000       8.000       0.000      0
                  6      5.000       8.000       0.000      0
                  7      7.000       8.000       0.000      0
                  8      4.000       6.000       0.000      0
                  9     -2.566       5.406       0.000      0
                 10      1.688       5.406       0.000      0
                 11      3.500       4.500       0.000      0
                 12      1.442       2.442       0.000      0
                 13      0.000       1.000       0.000      0
                 14     -1.936       4.488       0.000      0
                 15      0.383       4.521       0.000      0
                 16      1.445       3.480       0.000      0
                 17     -0.484       2.483       0.000      0
                 18     -1.936       3.632       0.000      0
                 19     -3.429       4.000       0.000      0
                 20     -5.714       6.000       0.000      0
                 21     -7.315       7.401       0.000      0
                 22     -4.915       7.506       0.000      0
                 23     -5.335       6.531       0.000      0
                 24     -2.287       7.452       0.000      0
"""

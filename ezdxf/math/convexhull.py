# Author:  mozman
# Purpose: convex hull algorithm
# Created: 28.02.2010
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List
from ezdxf.math.base import left_of_line

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


def convex_hull_2d(points: Iterable['Vertex'])->List['Vertex']:
    def _convexhull(hull):
        while len(hull) > 2:
            start_point, check_point, destination_point = hull[-3:]  # the last three points
            if not left_of_line(check_point, start_point, destination_point):  # curve not turns right
                del hull[-2]  # remove the penultimate point
            else:
                break
        return hull

    points = sorted(set(points))  # remove duplicate points

    if len(points) < 3:
        raise ValueError("ConvexHull(): Less than 3 unique points given!")

    upper_hull = points[:2]  # first two points
    for next_point in points[2:]:
        upper_hull.append(next_point)
        upper_hull = _convexhull(upper_hull)
    lower_hull = [points[-1], points[-2]]  # last two points

    for next_point in reversed(points[:-2]):
        lower_hull.append(next_point)
        lower_hull = _convexhull(lower_hull)
    upper_hull.extend(lower_hull[1:-1])
    return upper_hull

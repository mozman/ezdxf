#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import random
import time
import pathlib
import ezdxf

from ezdxf.math import Vec2, convex_hull_2d, is_point_left_of_line

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

SIZE = 100
ROUNDS = 2000


def old_convex_hull_2d(points):
    """Returns 2D convex hull for `points`.

    Args:
        points: iterable of points as :class:`Vec3` compatible objects,
            z-axis is ignored

    """

    def _convexhull(hull):
        while len(hull) > 2:
            # the last three points
            start_point, check_point, destination_point = hull[-3:]
            # curve not turns right
            if not is_point_left_of_line(
                check_point, start_point, destination_point
            ):
                # remove the penultimate point
                del hull[-2]
            else:
                break
        return hull

    points = sorted(set(Vec2.generate(points)))  # remove duplicate points

    if len(points) < 3:
        raise ValueError(
            "Convex hull calculation requires 3 or more unique points."
        )

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


def random_points(n: int):
    return [
        Vec2(random.random() * SIZE, random.random() * SIZE) for _ in range(n)
    ]


def profile(func, points) -> float:
    t0 = time.perf_counter()
    for _ in range(ROUNDS):
        func(points)
    t1 = time.perf_counter()
    return t1 - t0


def export_dxf(points):
    doc = ezdxf.new()
    msp = doc.modelspace()
    for p in points:
        msp.add_point(p, dxfattribs={"color": 1, "layer": "points"})
    hull = old_convex_hull_2d(points)
    msp.add_lwpolyline(hull, dxfattribs={"color": 2, "layer": "old_hull"})
    hull = convex_hull_2d(points)
    msp.add_lwpolyline(hull, dxfattribs={"color": 6, "layer": "new_hull"})
    doc.saveas(CWD / "convexhull.dxf")


def main():
    points = random_points(200)
    old = profile(old_convex_hull_2d, points)
    print(f"old convex hull function: {old:.3f}s")
    new = profile(convex_hull_2d, points)
    print(f"new convex hull function: {new:.3f}s")
    print(f"ratio old/new: {old/new:.3f}")
    export_dxf(points)


if __name__ == "__main__":
    main()

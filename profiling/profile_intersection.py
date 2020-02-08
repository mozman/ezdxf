import time

from ezdxf.math import intersection_line_line_2d, ConstructionRay, Vec2

P1 = Vec2((0, 0))
P2 = Vec2((10, 10))
P3 = Vec2((0, 10))
P4 = Vec2((10, 10))
COUNT = 300000


def profile_construction_ray(count=COUNT):
    for _ in range(count):
        ray1 = ConstructionRay(p1=P1, p2=P2)
        ray2 = ConstructionRay(p1=P3, p2=P4)
        ray1.intersect(ray2)


def profile_construction_ray_init_once(count=COUNT):
    ray1 = ConstructionRay(p1=P1, p2=P2)
    ray2 = ConstructionRay(p1=P3, p2=P4)
    for _ in range(count):
        ray1.intersect(ray2)


def profile_intersection_line_line_xy(count=COUNT):
    for _ in range(count):
        intersection_line_line_2d(line1=(P1, P2), line2=(P3, P4))


def profile(text, func):
    t0 = time.perf_counter()
    func()
    t1 = time.perf_counter()
    print(f'{text} {t1 - t0:.3f}s')


profile('intersect ConstructionRay: ', profile_construction_ray)
profile('intersect ConstructionRay init once: ', profile_construction_ray_init_once)
profile('intersect line line xy: ', profile_intersection_line_line_xy)

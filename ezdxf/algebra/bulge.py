# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
# source: http://www.lee-mac.com/bulgeconversion.html
# source: http://www.afralisp.net/archive/lisp/Bulges1.htm
from .vector import Vector

# polar signature: (polar pt ang dist) - Returns the UCS 3D point at a specified angle and distance from a point
# angle signature: (angle pt1 pt2) - Returns an angle in radians of a line defined by two endpoints


def arc_to_bulge():
    """
    ;; Arc to Bulge  -  Lee Mac
    ;; c     - center
    ;; a1,a2 - start, end angle
    ;; r     - radius
    ;; Returns: (<vertex> <bulge> <vertex>)

    (defun LM:arc->bulge ( c a1 a2 r )
        (list
            (polar c a1 r)
            (   (lambda ( a ) (/ (sin a) (cos a)))
                (/ (rem (+ pi pi (- a2 a1)) (+ pi pi)) 4.0)
            )
            (polar c a2 r)
        )
    )
    """
    pass


def bulge_3_points():
    """
    ;; 3-Points to Bulge  -  Lee Mac

    (defun LM:3p->bulge ( pt1 pt2 pt3 )
        ((lambda ( a ) (/ (sin a) (cos a))) (/ (+ (- pi (angle pt2 pt1)) (angle pt2 pt3)) 2))
    )
    """


def bulge_to_arc1():
    """
    ;; Bulge to Arc  -  Lee Mac
    ;; p1 - start vertex
    ;; p2 - end vertex
    ;; b  - bulge
    ;; Returns: (<center> <start angle> <end angle> <radius>)

    (defun LM:Bulge->Arc ( p1 p2 b / a c r )
        (setq a (* 2 (atan b))
              r (/ (distance p1 p2) 2 (sin a))
              c (polar p1 (+ (- (/ pi 2) a) (angle p1 p2)) r)
        )
        (if (minusp b)
            (list c (angle c p2) (angle c p1) (abs r))
            (list c (angle c p1) (angle c p2) (abs r))
        )
    )
    """


def bulge_to_arc2():
    """
    ;; Bulge to Arc  -  Lee Mac
    ;; p1 - start vertex
    ;; p2 - end vertex
    ;; b  - bulge
    ;; Returns: (<center> <start angle> <end angle> <radius>)

    (defun LM:Bulge->Arc ( p1 p2 b / c r )
        (setq r (/ (* (distance p1 p2) (1+ (* b b))) 4 b)
              c (polar p1 (+ (angle p1 p2) (- (/ pi 2) (* 2 (atan b)))) r)
        )
        (if (minusp b)
            (list c (angle c p2) (angle c p1) (abs r))
            (list c (angle c p1) (angle c p2) (abs r))
        )
    )
    """


def bulge_center(p1, p2, bulge):
    """
    Returns the center of the arc described by the given bulge and vertices

    Based on  Bulge Center by Lee Mac.

    Args:
        p1: start vertex as (x, y) tuple
        p2: end vertex as (x, y) tuple
        bulge: bulge value as float

    (defun LM:BulgeCenter ( p1 p2 b )
        (polar p1
            (+ (angle p1 p2) (- (/ pi 2) (* 2 (atan b))))
            (/ (* (distance p1 p2) (1+ (* b b))) 4 b)
        )
    )
    """


def bulge_radius(p1, p2, bulge):
    """
    Returns the radius of the arc described by the given bulge and vertices.

    Based on Bulge Radius by Lee Mac

    Args:
        p1: start vertex as (x, y) tuple
        p2: end vertex as (x, y) tuple
        bulge: bulge value as float

    """
    return Vector(p1).distance(p2) * (1. + (bulge * bulge)) / 4. / abs(bulge)


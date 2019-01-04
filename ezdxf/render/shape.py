# Created: 2019-01-04
# Copyright (c) 2019 Manfred Moitzi
# License: MIT License

from ezdxf.algebra import Vector


class Shape:
    """
    Geometry object as vertices list which can be moved, rotated and scaled.
    """
    def __init__(self, vertices):
        self.vertices = Vector.list(vertices)
# License
# Copyright (c) 2011 Evan Wallace (http://madebyevan.com/), under the MIT license.
# Python port Copyright (c) 2012 Tim Knip (http://www.floorplanner.com), under the MIT license.
# Additions by Alex Pletzer (Pennsylvania State University)
# Adaptation as ezdxf add-on, Copyright (c) 2020, Manfred Moitzi, MIT License.
from typing import List, Optional
import math
import operator
from functools import reduce

from ezdxf.math import Vector
from ezdxf.render import MeshVertexMerger, MeshBuilder, MeshTransformer
from ezdxf.render.forms import cube, sphere

__doc__ = """
Constructive Solid Geometry (CSG) is a modeling technique that uses Boolean
operations like union and intersection to combine 3D solids. This library
implements CSG operations on meshes elegantly and concisely using BSP trees,
and is meant to serve as an easily understandable implementation of the
algorithm. All edge cases involving overlapping coplanar polygons in both
solids are correctly handled.

Example usage::

    from csg.core import CSG
    
    cube = CSG.cube()
    sphere = CSG.sphere({'radius': 1.3})
    polygons = cube.subtract(sphere).to_polygons()

## Implementation Details

All CSG operations are implemented in terms of two functions, `clip_to()` and
`invert()`, which remove parts of a BSP tree inside another BSP tree and swap
solid and empty space, respectively. To find the union of `a` and `b`, we
want to remove everything in `a` inside `b` and everything in `b` inside `a`,
then combine polygons from `a` and `b` into one solid::

    a.clip_to(b)
    b.clip_to(a)
    a.build(b.all_polygons())

The only tricky part is handling overlapping coplanar polygons in both trees.
The code above keeps both copies, but we need to keep them in one tree and
remove them in the other tree. To remove them from `b` we can clip the
inverse of `b` against `a`. The code for union now looks like this::

    a.clip_to(b)
    b.clip_to(a)
    b.invert()
    b.clip_to(a)
    b.invert()
    a.build(b.all_polygons())

Subtraction and intersection naturally follow from set operations. If
union is `A | B`, subtraction is `A - B = ~(~A | B)` and intersection is
`A & B = ~(~A | ~B)` where `~` is the complement operator.

"""

COPLANAR = 0  # all the vertices are within EPSILON distance from plane
FRONT = 1  # all the vertices are in front of the plane
BACK = 2  # all the vertices are at the back of the plane
SPANNING = 3  # some vertices are in front, some in the back


class Plane:
    """ Represents a plane in 3D space.  """
    """
    `Plane.EPSILON` is the tolerance used by `split_polygon()` to decide if a
    point is on the plane.
    """
    EPSILON = 1.e-5
    __slots__ = ('normal', 'w')

    def __init__(self, normal: Vector, w: float):
        self.normal = normal
        # w is the (perpendicular) distance of the plane from (0, 0, 0)
        self.w = w

    @classmethod
    def from_points(cls, a: Vector, b: Vector, c: Vector) -> 'Plane':
        n = (b - a).cross(c - a).normalize()
        return Plane(n, n.dot(a))

    def clone(self) -> 'Plane':
        return Plane(self.normal, self.w)

    def flip(self):
        self.normal = -self.normal
        self.w = -self.w

    def __repr__(self) -> str:
        return f'Plane({self.normal}, {self.w})'

    def split_polygon(self, polygon: 'Polygon',
                      coplanar_front: List['Polygon'], coplanar_back: List['Polygon'],
                      front: List['Polygon'], back: List['Polygon']):
        """
        Split `polygon` by this plane if needed, then put the polygon or polygon
        fragments in the appropriate lists. Coplanar polygons go into either
        `coplanarFront` or `coplanarBack` depending on their orientation with
        respect to this plane. Polygons in front or in back of this plane go into
        either `front` or `back`
        """

        # Classify each point as well as the entire polygon into one of the above
        # four classes.
        polygon_type = 0
        vertex_locations = []

        num_vertices = len(polygon.vertices)
        for i in range(num_vertices):
            t = self.normal.dot(polygon.vertices[i]) - self.w
            if t < -Plane.EPSILON:
                loc = BACK
            elif t > Plane.EPSILON:
                loc = FRONT
            else:
                loc = COPLANAR
            polygon_type |= loc
            vertex_locations.append(loc)

        # Put the polygon in the correct list, splitting it when necessary.
        if polygon_type == COPLANAR:
            normal_dot_plane_normal = self.normal.dot(polygon.plane.normal)
            if normal_dot_plane_normal > 0:
                coplanar_front.append(polygon)
            else:
                coplanar_back.append(polygon)
        elif polygon_type == FRONT:
            front.append(polygon)
        elif polygon_type == BACK:
            back.append(polygon)
        elif polygon_type == SPANNING:
            f = []
            b = []
            for i in range(num_vertices):
                j = (i + 1) % num_vertices
                ti = vertex_locations[i]
                tj = vertex_locations[j]
                vi = polygon.vertices[i]
                vj = polygon.vertices[j]
                if ti != BACK:
                    f.append(vi)
                if ti != FRONT:
                    if ti != BACK:
                        b.append(vi)
                    else:
                        b.append(vi)
                if (ti | tj) == SPANNING:
                    # interpolation weight at the intersection point
                    t = (self.w - self.normal.dot(vi)) / self.normal.dot(vj - vi)
                    # intersection point on the plane
                    v = vi.lerp(vj, t)
                    f.append(v)
                    b.append(v)
            if len(f) >= 3:
                front.append(Polygon(f))
            if len(b) >= 3:
                back.append(Polygon(b))


class Polygon:
    """
    Represents a convex polygon. The vertices used to initialize a polygon must
    be coplanar and form a convex loop. They do not have to be `Vertex`
    instances but they must behave similarly (duck typing can be used for
    customization).

    """

    def __init__(self, vertices: List[Vector]):
        self.vertices = vertices
        self.plane = Plane.from_points(vertices[0], vertices[1], vertices[2])

    def clone(self):
        return Polygon(list(self.vertices))

    def flip(self):
        self.vertices.reverse()
        self.plane.flip()

    def __repr__(self):
        return reduce(lambda x, y: x + y, ['Polygon(['] + [repr(v) + ', ' for v in self.vertices] + ['])'], '')


class BSPNode:
    """
    Holds a node in a BSP tree. A BSP tree is built from a collection of polygons
    by picking a polygon to split along. That polygon (and all other coplanar
    polygons) are added directly to that node and the other polygons are added to
    the front and/or back subtrees. This is not a leafy BSP tree since there is
    no distinction between internal and leaf nodes.
    """

    def __init__(self, polygons: List[Polygon] = None):
        self.plane = None  # type: Optional[Plane]
        self.front = None  # type: Optional[BSPNode]
        self.back = None  # type: Optional[BSPNode]
        self.polygons = []  # type: List[Polygon]
        if polygons:
            self.build(polygons)

    def clone(self):
        node = BSPNode()
        if self.plane:
            node.plane = self.plane.clone()
        if self.front:
            node.front = self.front.clone()
        if self.back:
            node.back = self.back.clone()
        node.polygons = [p.clone() for p in self.polygons]
        return node

    def invert(self):
        """ Convert solid space to empty space and empty space to solid space. """
        for poly in self.polygons:
            poly.flip()
        self.plane.flip()
        if self.front:
            self.front.invert()
        if self.back:
            self.back.invert()
        temp = self.front
        self.front = self.back
        self.back = temp

    def clip_polygons(self, polygons: List['Polygon']):
        """ Recursively remove all polygons in `polygons` that are inside this BSP tree. """
        if not self.plane:
            return polygons[:]

        front = []
        back = []
        for poly in polygons:
            self.plane.split_polygon(poly, front, back, front, back)

        if self.front:
            front = self.front.clip_polygons(front)

        if self.back:
            back = self.back.clip_polygons(back)
        else:
            back = []

        front.extend(back)
        return front

    def clip_to(self, bsp):
        """ Remove all polygons in this BSP tree that are inside the other BSP tree `bsp`. """
        self.polygons = bsp.clip_polygons(self.polygons)
        if self.front:
            self.front.clip_to(bsp)
        if self.back:
            self.back.clip_to(bsp)

    def all_polygons(self):
        """ Return a list of all polygons in this BSP tree. """
        polygons = self.polygons[:]
        if self.front:
            polygons.extend(self.front.all_polygons())
        if self.back:
            polygons.extend(self.back.all_polygons())
        return polygons

    def build(self, polygons: List[Polygon]):
        """
        Build a BSP tree out of `polygons`. When called on an existing tree, the
        new polygons are filtered down to the bottom of the tree and become new
        nodes there. Each set of polygons is partitioned using the first polygon
        (no heuristic is used to pick a good split).
        """
        if len(polygons) == 0:
            return
        if not self.plane:
            self.plane = polygons[0].plane.clone()
        # add polygon to this node
        self.polygons.append(polygons[0])
        front = []
        back = []
        # split all other polygons using the first polygon's plane
        for poly in polygons[1:]:
            # coplanar front and back polygons go into self.polygons
            self.plane.split_polygon(poly, self.polygons, self.polygons, front, back)
        # recursively build the BSP tree
        if len(front) > 0:
            if not self.front:
                self.front = BSPNode()
            self.front.build(front)
        if len(back) > 0:
            if not self.back:
                self.back = BSPNode()
            self.back.build(back)


class CSG:
    """
    Constructive Solid Geometry (CSG) is a modeling technique that uses Boolean
    operations like union and intersection to combine 3D solids. This library
    implements CSG operations on meshes elegantly and concisely using BSP trees,
    and is meant to serve as an easily understandable implementation of the
    algorithm. All edge cases involving overlapping coplanar polygons in both
    solids are correctly handled.
    
    """

    def __init__(self):
        self.polygons = []  # type: List[Polygon]

    @classmethod
    def from_polygons(cls, polygons) -> 'CSG':
        csg = CSG()
        csg.polygons = polygons
        return csg

    @classmethod
    def from_mesh_builder(cls, mesh: MeshBuilder) -> 'CSG':
        """ Create :class:`CSG` object from :class:`ezdxf.render.MeshBuilder' object. """
        polygons = []
        for face in mesh.faces_as_vertices():
            polygons.append(Polygon(face))
        return CSG.from_polygons(polygons)

    def to_mesh_builder(self) -> MeshTransformer:
        """ Return :class:`ezdxf.render.MeshTransformer' object. """
        mesh = MeshVertexMerger()
        for face in self.polygons:
            mesh.add_face(face.vertices)
        return MeshTransformer.from_builder(mesh)

    def clone(self):
        csg = CSG()
        csg.polygons = [p.clone() for p in self.polygons]
        return csg

    def refine(self):
        """
        Return a refined CSG. To each polygon, a middle point is added to each edge and to the center 
        of the polygon
        """
        new_csg = CSG()
        for poly in self.polygons:

            verts = poly.vertices
            num_verts = len(verts)

            if num_verts == 0:
                continue

            mid_pos = reduce(operator.add, [v for v in verts]) / float(num_verts)
            new_verts = verts + [verts[i].lerp(verts[(i + 1) % num_verts], 0.5) for i in range(num_verts)] + [mid_pos]

            i = 0
            vs = [new_verts[i], new_verts[i + num_verts], new_verts[2 * num_verts], new_verts[2 * num_verts - 1]]
            new_poly = Polygon(vs)
            new_poly.plane = poly.plane
            new_csg.polygons.append(new_poly)

            for i in range(1, num_verts):
                vs = [new_verts[i], new_verts[num_verts + i], new_verts[2 * num_verts], new_verts[num_verts + i - 1]]
                new_poly = Polygon(vs)
                new_csg.polygons.append(new_poly)

        return new_csg

    def union(self, csg):
        """
        Return a new CSG solid representing space in either this solid or in the
        solid `csg`. Neither this solid nor the solid `csg` are modified::
        
            A.union(B)
        
            +-------+            +-------+
            |       |            |       |
            |   A   |            |       |
            |    +--+----+   =   |       +----+
            +----+--+    |       +----+       |
                 |   B   |            |       |
                 |       |            |       |
                 +-------+            +-------+
        """
        a = BSPNode(self.clone().polygons)
        b = BSPNode(csg.clone().polygons)
        a.clip_to(b)
        b.clip_to(a)
        b.invert()
        b.clip_to(a)
        b.invert()
        a.build(b.all_polygons())
        return CSG.from_polygons(a.all_polygons())

    __add__ = union

    def subtract(self, csg):
        """
        Return a new CSG solid representing space in this solid but not in the
        solid `csg`. Neither this solid nor the solid `csg` are modified.::
        
            A.subtract(B)
        
            +-------+            +-------+
            |       |            |       |
            |   A   |            |       |
            |    +--+----+   =   |    +--+
            +----+--+    |       +----+
                 |   B   |
                 |       |
                 +-------+
        """
        a = BSPNode(self.clone().polygons)
        b = BSPNode(csg.clone().polygons)
        a.invert()
        a.clip_to(b)
        b.clip_to(a)
        b.invert()
        b.clip_to(a)
        b.invert()
        a.build(b.all_polygons())
        a.invert()
        return CSG.from_polygons(a.all_polygons())

    __sub__ = subtract

    def intersect(self, csg):
        """
        Return a new CSG solid representing space both this solid and in the
        solid `csg`. Neither this solid nor the solid `csg` are modified.::
        
            A.intersect(B)
        
            +-------+
            |       |
            |   A   |
            |    +--+----+   =   +--+
            +----+--+    |       +--+
                 |   B   |
                 |       |
                 +-------+
        """
        a = BSPNode(self.clone().polygons)
        b = BSPNode(csg.clone().polygons)
        a.invert()
        b.clip_to(a)
        b.invert()
        a.clip_to(b)
        b.clip_to(a)
        a.build(b.all_polygons())
        a.invert()
        return CSG.from_polygons(a.all_polygons())

    __mul__ = intersect

    def inverse(self):
        """
        Return a new CSG solid with solid and empty space switched. This solid is
        not modified.
        """
        csg = self.clone()
        for p in csg.polygons:
            p.flip()
        return csg

    @staticmethod
    def cube(center=(0, 0, 0), scale=(1, 1, 1)):
        builder = cube()
        if isinstance(scale, (tuple, list)):
            sx, sy, sz = scale
        else:
            sx, sy, sz = scale, scale, scale

        builder.scale(sx, sy, sz)
        center = Vector(center)
        if center:
            builder.translate(*center.xyz)
        return CSG.from_mesh_builder(builder)

    @staticmethod
    def sphere(center=(0, 0, 0), radius: float = 1, slices: int = 16, stacks: int = 8):
        mesh = sphere(radius, slices, stacks)
        mesh.translate(*Vector(center).xyz)
        return CSG.from_mesh_builder(mesh)

    @staticmethod
    def cylinder(start=(0, -1, 0), end=(0, 1, 0), radius: float = 1, slices: int = 16):
        return CSG.from_mesh_builder(cylinder(start, end, radius, slices))

    @staticmethod
    def cone(start=(0, -1, 0), end=(0, 1, 0), radius: float = 1.0, slices: int = 16):
        return CSG.from_mesh_builder(cone(start, end, radius, slices))


def cylinder(start=(0, -1, 0), end=(0, 1, 0), radius: float = 1, slices: int = 16) -> MeshTransformer:
    """ Returns a cylinder.
    """
    start = Vector(start)
    end = Vector(end)
    radius = float(radius)
    slices = int(slices)
    ray = end - start

    z_axis = ray.normalize()
    is_y = (math.fabs(z_axis.y) > 0.5)
    x_axis = Vector(float(is_y), float(not is_y), 0).cross(z_axis).normalize()
    y_axis = x_axis.cross(z_axis).normalize()
    mesh = MeshVertexMerger()

    def vertex(stack, angle):
        out = (x_axis * math.cos(angle)) + (y_axis * math.sin(angle))
        return start + (ray * stack) + (out * radius)

    dt = math.pi * 2 / float(slices)
    for i in range(0, slices):
        t0 = i * dt
        i1 = (i + 1) % slices
        t1 = i1 * dt
        mesh.add_face([start, vertex(0, t0), vertex(0, t1)])
        mesh.add_face([vertex(0, t1), vertex(0, t0), vertex(1, t0), vertex(1, t1)])
        mesh.add_face([end, vertex(1, t1), vertex(1, t0)])
    return MeshTransformer.from_builder(mesh)


def cone(start=(0, -1, 0), end=(0, 1, 0), radius: float = 1.0, slices: int = 16) -> MeshTransformer:
    """ Returns a cone. """
    start = Vector(start)
    end = Vector(end)
    ray = end - start
    z_axis = ray.normalize()
    is_y = (math.fabs(z_axis.y) > 0.5)
    x_axis = Vector(float(is_y), float(not is_y), 0).cross(z_axis).normalize()
    y_axis = x_axis.cross(z_axis).normalize()
    mesh = MeshVertexMerger()

    def vertex(angle) -> Vector:
        # radial direction pointing out
        out = x_axis * math.cos(angle) + y_axis * math.sin(angle)
        return start + out * radius

    dt = math.pi * 2.0 / float(slices)
    for i in range(0, slices):
        t0 = i * dt
        i1 = (i + 1) % slices
        t1 = i1 * dt
        # coordinates and associated normal pointing outwards of the cone's
        # side
        p0 = vertex(t0)
        p1 = vertex(t1)
        # polygon on the low side (disk sector)
        mesh.add_face([start, p0, p1])
        # polygon extending from the low side to the tip
        mesh.add_face([p0, end, p1])

    return MeshTransformer.from_builder(mesh)

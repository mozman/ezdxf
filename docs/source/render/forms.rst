.. module:: ezdxf.render.forms

Forms
=====

    This module provides functions to create 2D and 3D forms as vertices or mesh objects.

    2D Forms

    - :meth:`circle`
    - :meth:`square`
    - :meth:`box`
    - :meth:`ellipse`
    - :meth:`euler_spiral`
    - :meth:`ngon`
    - :meth:`star`
    - :meth:`gear`

    3D Forms

    - :meth:`cube`
    - :meth:`cylinder`
    - :meth:`cylinder_2p`
    - :meth:`cone`
    - :meth:`cone_2p`
    - :meth:`sphere`

    3D Form Builder

    - :meth:`extrude`
    - :meth:`from_profiles_linear`
    - :meth:`from_profiles_spline`
    - :meth:`rotation_form`

2D Forms
--------

    Basic 2D shapes as iterable of :class:`~ezdxf.math.Vector`.


.. autofunction:: circle(count: int, radius: float = 1, elevation: float = 0, close: bool = False) -> Iterable[Vector]

.. autofunction:: square(size: float = 1.) -> Tuple[Vector, Vector, Vector, Vector]

.. autofunction:: box(sx: float = 1., sy: float = 1.) -> Tuple[Vector, Vector, Vector, Vector]

.. autofunction:: ellipse(count: int, rx: float = 1, ry: float = 1, start_param: float = 0, end_param: float = 2 * pi, elevation: float = 0) -> Iterable[Vector]

.. autofunction:: euler_spiral(count: int, length: float = 1, curvature: float = 1, elevation: float = 0) -> Iterable[Vector]

.. autofunction:: ngon(count: int, length: float = None, radius: float = None, rotation: float = 0., elevation: float = 0., close: bool = False) -> Iterable[Vector]

.. autofunction:: star(count: int, r1: float, r2: float, rotation: float = 0., elevation: float = 0., close: bool = False) -> Iterable[Vector]

.. autofunction:: gear(count: int, top_width: float, bottom_width: float, height: float, outside_radius: float, elevation: float = 0, close: bool = False) -> Iterable[Vector]


3D Forms
--------

Create 3D forms as :class:`~ezdxf.render.MeshTransformer` objects.

.. autofunction:: cube(center: bool = True) -> MeshTransformer

.. autofunction:: cylinder(count: int, radius: float = 1., top_radius: float = None, top_center: Vertex = (0, 0, 1), caps: bool = True) -> MeshTransformer

.. autofunction:: cylinder_2p(count: int = 16, radius: float = 1, base_center=(0, 0, 0), top_center=(0, 0, 1), ) -> MeshTransformer

.. autofunction:: cone(count: int, radius: float, apex: Vertex = (0, 0, 1), caps: bool = True) -> MeshTransformer

.. autofunction:: cone_2p(count: int, radius: float, apex: Vertex = (0, 0, 1)) -> MeshTransformer

.. autofunction:: sphere(count: int = 16, stacks: int = 8, radius: float = 1, quads = False) -> MeshTransformer

3D Form Builder
---------------

.. autofunction:: extrude(profile: Iterable[Vertex], path: Iterable[Vertex], close: bool = True) -> MeshTransformer

.. autofunction:: from_profiles_linear(profiles: Iterable[Iterable[Vertex]], close: bool = True, caps: bool = False) -> MeshTransformer

.. autofunction:: from_profiles_spline(profiles: Iterable[Iterable[Vertex]], subdivide: int = 4, close: bool = True, caps: bool = False) -> MeshTransformer

.. autofunction:: rotation_form(count: int, profile: Iterable[Vertex], angle: float = 2 * pi, axis: Vertex = (1, 0, 0)) -> MeshTransformer

.. _math utilities:

.. module:: ezdxf.math

Utility functions and classes located in module :mod:`ezdxf.math`.

Functions
=========

.. autofunction:: is_close_points

.. autofunction:: closest_point

.. autofunction:: convex_hull

.. autofunction:: bspline_control_frame

.. autofunction:: xround

.. _bulge_related_functions:

Bulge Related Functions
-----------------------

.. seealso::

    Description of the :ref:`bulge value`.

.. autofunction:: bulge_center

.. autofunction:: bulge_radius

.. autofunction:: arc_to_bulge

.. autofunction:: bulge_to_arc

.. autofunction:: bulge_3_points

Transformation Classes
======================

OCS Class
---------

.. autoclass:: OCS
    :members:


UCS Class
---------

.. autoclass:: UCS
    :members:

Vector
------

.. autoclass:: Vector
    :members:
    :special-members:

.. autoclass:: Vec2

Matrix44
--------

.. autoclass:: Matrix44
    :members:
    :special-members:

Curves
======

BSpline
-------

.. autoclass:: BSpline
    :members:

BSplineU
--------

.. autoclass:: BSplineU
    :members:

BSplineClosed
-------------

.. autoclass:: BSplineClosed
    :members:


DBSpline
--------

.. autoclass:: DBSpline
    :members:

DBSplineU
---------

.. autoclass:: DBSplineU
    :members:

DBSplineClosed
--------------

.. autoclass:: DBSplineClosed
    :members:

EulerSpiral
-----------

.. autoclass:: EulerSpiral
    :members:

Construction Tools
==================

BoundingBox
-----------

.. autoclass:: BoundingBox
    :members:

BoundingBox2d
-------------

.. autoclass:: BoundingBox2d
    :members:

ConstructionRay
---------------

.. autoclass:: ConstructionRay
    :members:

ConstructionLine
----------------

.. autoclass:: ConstructionLine
    :members:

ConstructionCircle
------------------

.. autoclass:: ConstructionCircle
    :members:

ConstructionArc
---------------

.. autoclass:: ConstructionArc
    :members:

ConstructionBox
---------------

.. autoclass:: ConstructionBox
    :members:


.. _Curve Global Interpolation: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html
.. _uniform: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-uniform.html
.. _chord length: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-chord-length.html
.. _centripetal: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-centripetal.html
.. _knot: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-knot-generation.html
.. _clamped curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve.html
.. _open curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-open.html
.. _closed curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-closed.html
.. _basis: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-basis.html

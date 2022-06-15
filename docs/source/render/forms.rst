.. module:: ezdxf.render.forms

Forms
=====

    This module provides functions to create 2D and 3D forms as vertices or mesh objects.

    2D Forms

    - :func:`circle`
    - :func:`square`
    - :func:`box`
    - :func:`ellipse`
    - :func:`euler_spiral`
    - :func:`ngon`
    - :func:`star`
    - :func:`gear`

    3D Forms

    - :func:`cube`
    - :func:`cylinder`
    - :func:`cylinder_2p`
    - :func:`cone`
    - :func:`cone_2p`
    - :func:`sphere`

    3D Form Builder

    - :func:`extrude`
    - :func:`extrude_twist_scale`
    - :func:`from_profiles_linear`
    - :func:`from_profiles_spline`
    - :func:`sweep`
    - :func:`rotation_form`


2D Forms
--------

    Basic 2D shapes as iterable of :class:`~ezdxf.math.Vec3`.


.. autofunction:: circle

.. autofunction:: square

.. autofunction:: box

.. autofunction:: ellipse

.. autofunction:: euler_spiral

.. autofunction:: ngon

.. autofunction:: star

.. autofunction:: gear


3D Forms
--------

Create 3D forms as :class:`~ezdxf.render.MeshTransformer` objects.

.. autofunction:: cube

.. autofunction:: cylinder

.. autofunction:: cylinder_2p

.. autofunction:: cone

.. autofunction:: cone_2p

.. autofunction:: sphere

.. autofunction:: torus

3D Form Builder
---------------

.. autofunction:: extrude

.. autofunction:: extrude_twist_scale

.. autofunction:: from_profiles_linear

.. autofunction:: from_profiles_spline

.. autofunction:: sweep

.. autofunction:: rotation_form

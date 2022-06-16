.. module:: ezdxf.render.forms

Forms
=====

    This module provides functions to create 2D and 3D forms as vertices or
    mesh objects.

    2D Forms

    - :func:`box`
    - :func:`circle`
    - :func:`ellipse`
    - :func:`euler_spiral`
    - :func:`gear`
    - :func:`ngon`
    - :func:`square`
    - :func:`star`

    3D Forms

    - :func:`cone_2p`
    - :func:`cone`
    - :func:`cube`
    - :func:`cylinder`
    - :func:`cylinder_2p`
    - :func:`helix`
    - :func:`sphere`
    - :func:`torus`

    3D Form Builder

    - :func:`extrude`
    - :func:`extrude_twist_scale`
    - :func:`from_profiles_linear`
    - :func:`from_profiles_spline`
    - :func:`rotation_form`
    - :func:`sweep`


2D Forms
--------

    Basic 2D shapes as iterable of :class:`~ezdxf.math.Vec3`.


.. autofunction:: box

.. autofunction:: circle

.. autofunction:: ellipse

.. autofunction:: euler_spiral

.. autofunction:: gear

.. autofunction:: ngon

.. autofunction:: square

.. autofunction:: star


3D Forms
--------

Create 3D forms as :class:`~ezdxf.render.MeshTransformer` objects.

.. autofunction:: cube

.. autofunction:: cone

.. autofunction:: cone_2p

.. autofunction:: cylinder

.. autofunction:: cylinder_2p

.. autofunction:: helix

.. autofunction:: sphere

.. autofunction:: torus

3D Form Builder
---------------

.. autofunction:: extrude

.. autofunction:: extrude_twist_scale

.. autofunction:: from_profiles_linear

.. autofunction:: from_profiles_spline

.. autofunction:: rotation_form

.. autofunction:: sweep

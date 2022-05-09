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

3D Form Builder
---------------

.. autofunction:: extrude

.. autofunction:: from_profiles_linear

.. autofunction:: from_profiles_spline

.. autofunction:: rotation_form

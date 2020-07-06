.. _render:

.. module:: ezdxf.render

Rendering
=========

The :mod:`ezdxf.render` subpackage provides helpful utilities to create complex forms, but `ezdxf` is still not a
rendering engine in the sense of true graphical rendering for screen or paper.

    - create complex meshes as :class:`~ezdxf.entities.Mesh` entity.
    - render complex curves like bezier curves, euler spirals or splines as :class:`~ezdxf.entities.Polyline` entity
    - vertex generators for simple and complex forms like circle, ellipse or euler spiral

.. rubric:: Content


.. toctree::
    :maxdepth: 1

    curves
    forms
    mesh
    trace

Zoom Layouts
============

.. module:: ezdxf.zoom

These functions mimic the ZOOM commands in CAD applications.

Zooming means resetting the current viewport limits to new values.
The coordinates for the functions :func:`center` and :func:`window` are
drawing units for the model space and paper space units for paper space layouts.
The modelspace units in :attr:`Drawing.units` are ignored.

The extents detection for the functions :func:`entities` and :func:`extents`
is done by the :mod:`ezdxf.bbox` module. Read the associated documentation to
understand the limitations of the :mod:`ezdxf.bbox` module.
Tl;dr The extents detection is **slow** and **not accurate**.

Because the ZOOM operations in CAD applications are not that precise, then
zoom functions of this module uses the fast bounding box calculation mode
of the :mod:`bbox` module, which means the argument `flatten` is always
``False`` for :func:`~ezdxf.bbox.extents` function calls.

The region displayed by CAD applications also depends on the aspect ratio of
the application window, which is not available to `ezdxf`, therefore the
viewport size is just an educated guess of an aspect ratio of 2:1 (16:9 minus
top toolbars and the bottom status bar).

.. warning::

    All zoom functions replace the current viewport configuration by a single
    window configuration.

Example to reset the main CAD viewport of the model space to the extents of its
entities:

.. code-block:: Python

    import ezdxf
    from ezdxf import zoom

    doc = ezdxf.new()
    msp = doc.modelspace()
    ... # add your DXF entities

    zoom.extents(msp)
    doc.saveas("your.dxf")

.. autofunction:: center

.. autofunction:: objects

.. autofunction:: extents

.. autofunction:: window

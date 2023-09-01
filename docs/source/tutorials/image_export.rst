.. _tut_image_export:

Tutorial for Image Export
=========================

.. contents::
    :local:

Introduction
------------

This tutorial shows how to export DXF content of the modelspace or a paperspace as
images by the :mod:`~ezdxf.addons.drawing` add-on.

The tutorial covers the new added backends in `ezdxf` version 1.1:

- :class:`ezdxf.addons.drawing.svg.SVGBackend` class for SVG export
- :class:`ezdxf.addons.drawing.pymupdf.PyMuPdfBackend` class for PDF and PNG export
- :class:`ezdxf.addons.drawing.hpgl2.PlotterBackend` class for PLT/HPGL2 export
- :class:`ezdxf.addons.drawing.dxf.DXFBackend` class for flattened DXF export

The tutorial **does not cover** the :class:`~ezdxf.addons.drawing.matplotlib.MatplotlibBackend`
and :class:`~ezdxf.addons.drawing.pyqt.PyQtBackend`, for information about these
backends see:

- Howtos for the :ref:`how_to_drawing_addon`
- FAQs at github: https://github.com/mozman/ezdxf/discussions/550

Common Basics
-------------

The rendering process is divided into multiple steps. The frontend resolves the DXF
properties and breaks down complex DXF entities into simple drawing primitives which
are send to the backend that renders the output format.

.. literalinclude:: src/export/basic_svg.py
    :lines: 4-

The exported SVG shows a spiral centered on an A4 page with a margin of 20mm, notice
the background has a dark color like the usual background of the modelspace:

.. image:: gfx/image_export_01.png
    :align: center


Frontend Configuration
~~~~~~~~~~~~~~~~~~~~~~

The :class:`~ezdxf.addons.drawing.config.Configuration` object configures the rendering
process. This example changes the background color from dark grey to white and renders
all lines black.

Add the :mod:`config` module to imports:

.. literalinclude:: src/export/change_bg_color.py
    :lines: 5

Create a new configuration and override the background and color policy between the
2nd and the 3rd step:

.. literalinclude:: src/export/change_bg_color.py
    :lines: 31-39

The new exported SVG has a white background and all lines are black:

.. image:: gfx/image_export_02.png
    :align: center

There are many configuration options:

    - :class:`~ezdxf.addons.drawing.config.LineweightPolicy` - relative, absolute or relative fixed lineweight
    - :class:`~ezdxf.addons.drawing.config.LinePolicy` - solid or accurate linetypes
    - :class:`~ezdxf.addons.drawing.config.HatchPolicy` - normal, ignore, only outlines or always solid fill
    - :class:`~ezdxf.addons.drawing.config.ColorPolicy` - color, black, white, monochrome, ...
    - :class:`~ezdxf.addons.drawing.config.BackgroundPolicy` - default, black, white, off (transparent) and custom
    - :class:`~ezdxf.addons.drawing.config.TextPolicy` - filling, outline, ignore, ...
    - :class:`~ezdxf.addons.drawing.config.ProxyGraphicPolicy` - ignore, show, prefer
    - lineweight scaling factor
    - minimal lineweight
    - `max_flattening_distance` for curve approximation
    - and more ...

All configuration options are documented here: :class:`~ezdxf.addons.drawing.config.Configuration`.

Page Layout
~~~~~~~~~~~

The :class:`~ezdxf.addons.drawing.layout.Page` object defines the output page for some
backends (SVG, PDF, PNG, PLT).

A page is defined by width and height in a given length unit. The supported length
units are millimeters (mm), inch (in), point (1 pt is 1/72 in) and pixels (1 px is 1/96
in).

It's possible to autodetect the page size from the content or fit the content onto the
page. In both cases the margin values are used to create space between the content and
the page borders. The content is centered in the remaining space without margins.

.. important::

    None of the backends crop the content automatically, the margin values are just
    calculation values!

Autodetect Page Size
~~~~~~~~~~~~~~~~~~~~

The required page size is auto-detected by setting the width and/or height to 0.
By default the scaling factor is 1, so 1 drawing unit is 1 page unit.
The content is fit to page by default and the outcome is shown in the previous examples.

This example shows the output when the scale should be 1:1, 1 drawing unit is 1 page
unit (mm):

.. literalinclude:: src/export/page_auto_detect.py
    :lines: 44-49

The page has a size of 14x14mm, a content size of 10x10mm and 2mm margins on all sides.

.. image:: gfx/image_export_03.png
    :align: center

Scaling Content
~~~~~~~~~~~~~~~

Scaling the content by factor 10 means, 10 page units represent 1 drawing unit, which is
a scale of 10:1 and only uniform scaling is supported.

.. literalinclude:: src/export/page_auto_detect.py
    :lines: 54-59

The page has a size of 104x104mm, a content size of 100x100mm and 2mm margins on all
sides.

.. image:: gfx/image_export_04.png
    :align: center

Limit Page Size
~~~~~~~~~~~~~~~

The page arguments `max_width` and `max_height` can limit the page size in
auto-detection mode, e.g. most plotter devices can only print upto a width of 900mm.

.. seealso::

    - :class:`~ezdxf.addons.drawing.layout.Page` class
    - :class:`~ezdxf.addons.drawing.layout.Margins` class
    - :class:`~ezdxf.addons.drawing.layout.Settings` class


SVG Export
----------

PDF Export
----------

PNG Export
----------

PLT/HPGL2 Export
----------------

DXF Export
----------

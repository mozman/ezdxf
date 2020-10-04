.. module:: ezdxf.addons.drawing

Drawing / Export Addon
======================

This add-on provides the functionality to render a DXF document to produce a rasterized or vector-graphic image which
can be saved to a file or viewed interactively depending on the backend being used.

The module provides two example scripts in the folder ``examples/addons/drawing`` which can be run to save rendered
images to files or view an interactive visualisation

.. code-block::

    $ ./draw_cad.py --supported_formats
    # will list the file formats supported by the matplotlib backend.
    # Many formats are supported including vector graphics formats
    # such as pdf and svg

    $ ./draw_cad.py <my_file.dxf> --out image.png

    # draw a layout other than the model space
    $ ./draw_cad.py <my_file.dxf> --layout Layout1 --out image.png

    # opens a GUI application to view CAD files
    $ ./cad_viewer.py


Example for the usage of the :mod:`matplotlib` backend:

.. code-block:: Python

    import sys
    import matplotlib.pyplot as plt
    from ezdxf import recover
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    # Safe loading procedure (requires ezdxf v0.14):
    try:
        doc, auditor = recover.readfile('your.dxf')
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file.')
        sys.exit(2)

    # The auditor.errors attribute stores severe errors,
    # which may raise exceptions when rendering.
    if not auditor.has_errors:
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(doc.modelspace(), finalize=True)
        fig.savefig('your.png', dpi=300)

Simplified render workflow but with less control:

.. code-block:: Python

    from ezdxf import recover
    from ezdxf.addons.drawing import matplotlib

    # Exception handling left out for compactness:
    doc, auditor = recover.readfile('your.dxf')
    if not auditor.has_errors:
        matplotlib.qsave(doc.modelspace(), 'your.png')

.. autofunction:: ezdxf.addons.drawing.matplotlib.qsave

MatplotlibBackend
-----------------

.. class:: ezdxf.addons.drawing.matplotlib.MatplotlibBackend

    .. method:: __init__(ax: plt.Axes, *, adjust_figure: bool = True, font: FontProperties,  use_text_cache: bool = True, params: Dict = None)

PyQtBackend
-----------

.. class:: ezdxf.addons.drawing.pyqt.PyQtBackend

    .. method:: __init__(scene: qw.QGraphicsScene = None, *, use_text_cache: bool = True, debug_draw_rect: bool = False, params: Dict = None)

Backend Options `params`
------------------------

Additional options for a backend can be passed by the `params` argument of the
backend constructor :meth:`__init__()`. Not every option will be supported by
all backends and currently most options are only supported by the matplotlib
backend.


point_size
    size for the POINT entity

point_size_relative
    POINT entity size is relative to the viewport (screen) if ``True``

linetype_renderer
    - "internal" uses the matplotlib linetype renderer which is oriented on the
      output medium and dpi setting, This method is simpler and faster but may
      not replicate the results of CAD applications.
    - "ezdxf" replicate AutoCAD linetype rendering oriented on drawing units and
      various ltscale factors.This rendering method break lines into small
      segments which causes a longer rendering time!

linetype_scaling
    Overall linetype scaling factor.

lineweight_scaling
    overall lineweight scaling factor, set to 0 to disable lineweight support
    at all - the current result is correct, in SVG the line width is 0.7 points
    for 0.25mm as required, but it often looks too thick.

min_lineweight
    Minimum lineweight.

min_dash_length
    Minimum dash length.

max_flattening_distance
    Maximum flattening distance in drawing units for curve approximations.

show_hatch
    - 0 to disable HATCH entities
    - 1 to show HATCH entities

hatch_pattern
    - 0 to disable hatch pattern
    - 1 to use predefined matplotlib pattern by pattern-name matching
    - 2 to draw HATCH pattern as solid fillings.

Default Values
++++++++++++++

=========================== =================== ===================
Backend Option              MatplotlibBackend   PyQtBackend
=========================== =================== ===================
point_size                  2.0                 1.0
point_size_relative         ``True``            not supported
linetype_renderer           "internal"          not supported
linetype_scaling            ``None``            not supported
lineweight_scaling          1.0                 not supported
min_lineweight              0.24                not supported
min_dash_length             0.1                 not supported
max_flattening_distance     0.01                0.01
show_hatch                  1                   1
hatch_pattern               1                   not supported
=========================== =================== ===================

Properties
----------

.. class:: ezdxf.addons.drawing.properties.Properties

LayerProperties
---------------

.. class:: ezdxf.addons.drawing.properties.LayerProperties

RenderContext
-------------

.. class:: ezdxf.addons.drawing.properties.RenderContext

Frontend
--------

.. class:: ezdxf.addons.drawing.frontend.Frontend

Backend
--------

.. class:: ezdxf.addons.drawing.backend.Backend

Details
-------

The rendering is performed in two stages. The front-end traverses the DXF document
structure, converting each encountered entity into primitive drawing commands.
These commands are fed to a back-end which implements the interface:
:class:`~ezdxf.addons.drawing.backend.Backend`.

Currently a :class:`PyQtBackend` (QGraphicsScene based) and a
:class:`MatplotlibBackend` are implemented.

Although the resulting images will not be pixel-perfect with AutoCAD (which was
taken as the ground truth when developing this add-on) great care has been taken
to achieve similar behavior in some areas:

- The algorithm for determining color should match AutoCAD. However, the color
  palette is not stored in the dxf file, so the chosen colors may be different
  to what is expected. The :class:`~ezdxf.addons.drawing.properties.RenderContext`
  class supports passing a plot style table (:term:`CTB`-file) as custom color
  palette but uses the same palette as AutoCAD by default.
- Text rendering is quite accurate, text positioning, alignment and word wrapping
  are very faithful. Differences may occur if a different font from what was
  used by the CAD application but even in that case, for supported backends,
  measurements are taken of the font being used to match text as closely as possible.
- Visibility determination (based on which layers are visible) should match AutoCAD

See ``examples/addons/drawing/cad_viewer.py`` for an advanced use of the module.

See ``examples/addons/drawing/draw_cad.py`` for a simple use of the module.

See ``drawing.md`` in the ezdxf repository for additional behaviours documented
during the development of this add-on.

Limitations
-----------

- Line types and hatch patterns/gradients are ignored by the :class:`PyQtBackend`
- Rich text formatting is ignored (drawn as plain text)
- If the backend does not match the font then the exact text placement and
  wrapping may appear slightly different
- No support for MULTILEADER
- The style which POINT entities are drawn in are not stored in the dxf file and
  so cannot be replicated exactly
- only basic support for:

  - infinite lines (rendered as lines with a finite length)
  - viewports (rendered as rectangles)
  - 3D (some entities may not display correctly in 3D (see possible improvements below))
    however many things should already work in 3D.
  - vertical text (will render as horizontal text)
  - multiple columns of text (placement of additional columns may be incorrect)


Future Possible Improvements
----------------------------

- pass the font to backend if available
- text formatting commands could be interpreted and broken into text chunks
  which can be drawn with a single font weight or modification such as italics

.. _Triangulation: https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf
.. _MatplotlibHatch: https://matplotlib.org/3.2.1/gallery/shapes_and_collections/hatch_demo.html
.. _QtBrushHatch: https://doc.qt.io/qt-5/qbrush.html



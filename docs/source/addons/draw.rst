.. module:: ezdxf.addons.drawing
    :noindex:

.. _draw:

Drawing / Export Addon
======================

This add-on provides the functionality to render a DXF document to produce a rasterized or vector-graphic image which
can be saved to a file or viewed interactively depending on the backend being used.

The module provides two scripts which can be run to save rendered images to files or view an interactive visualisation

.. code-block::

    $ ./draw_cad.py --suppored_formats
    # will list the file formats supported by the matplotlib backend.
    # Many formats are supported including vector graphics formats
    # such as pdf and svg

    $ ./draw_cad.py <my_file.dxf> --out image.png

    # draw a layout other than the model space
    $ ./draw_cad.py <my_file.dxf> --layout Layout1 --out image.png

    # opens a GUI application to view CAD files
    $ ./cad_viewer.py


Simple example for the :mod:`matplotlib` backend:

.. code-block:: Python

    import ezdxf
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing.front_end import draw_layout
    from ezdxf.addons.drawing.matplotlib_backend import MatplotlibBackend

    doc = ezdxf.readfile('your.dxf')
    msp = doc.modelspace()

    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
    out = MatplotlibBackend(ax)
    draw_layout(msp, out)
    out.finalise()
    fig.savefig('your.png', dpi=300)

Details
-------

The rendering is performed in two stages. The front-end traverses the DXF document structure, converting each
encountered entity into primitive drawing commands. These commands are fed to a back-end which implements the interface:
:class:`ezdxf.addons.drawing.backend_interface.DrawingBackend`.
Currently a PyQt5 (QGraphicsScene based) and Matplotlib backend are implemented.

Although the resulting images will not be pixel-perfect with AutoCAD (which was taken as the ground truth when
developing this add-on) great care has been taken to achieve similar behavior in some areas:

- The algorithm for determining color should match AutoCAD. However, the color palette is not stored in the dxf file,
  so the chosen colors may be different to what is expected. The :class:`ezdxf.addons.drawing.colors.ColorContext` class
  supports passing a custom color palette but uses the same palette as AutoCAD by default.
- Text rendering is quite accurate, text positioning, alignment and word wrapping are very faithful. Differences may
  occur if a different font from what was used by the CAD application but even in that case, for supported backends,
  measurements are taken of the font being used to match text as closely as possible.
- Visibility determination (based on which layers are visible) should match AutoCAD

see `ezdxf.addons.drawing.cad_viewer` for an advanced use of the module. See `ezdxf.addons.drawing.draw_cad`
for a simple use of the module.

see `drawing.md` in the ezdxf repository for additional behaviours documented during the development of this add-on.

Limitations
-----------
- Patterns, line styles and line widths are ignored
- If the backend does not match the font then the exact text placement and wrapping may appear slightly different
- No support for leaders
- The style which POINT entities are drawn in are not stored in the dxf file and so cannot be replicated exactly
- only basic support for:

  - infinite lines (rendered as lines with a finite length)
  - hatches with holes (holes are rendered filled)
  - viewports (rendered as rectangles)
  - 3D (some entities may not display correctly in 3D (see possible improvements below)) however many things should already work in 3D.
  - vertical text (will render as horizontal text)
  - multiple columns of text (placement of additional columns may be incorrect)


Future Possible Improvements
----------------------------
- remove all dependence on getting the direction from the extrusion vector. `get_rotation_direction_from_extrusion_vector()` is only correct for 2D drawings so this is the main limitation for drawing in 3D
- render polylines using draw_line_string if it does not contain any arcs
- pass the font to backend if available
- deal with nested polygons/hatches by triangulating them: Triangulation_
- both the matplotlib and pyqt backends have built-in support for rendering hatched patterns (see MatplotlibHatch_ and QtBrushHatch_) so the interface could pass that information through or query the backend to determine whether it automatically supports complex drawing commands such as hatching, or whether the frontend should break the shape into simpler commands (i.e. calculate and draw each line of a hatch)
- text formatting commands could be interpreted and broken into text chunks which can be drawn with a single font weight or modification such as italics

.. _Triangulation: https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf
.. _MatplotlibHatch: https://matplotlib.org/3.2.1/gallery/shapes_and_collections/hatch_demo.html
.. _QtBrushHatch: https://doc.qt.io/qt-5/qbrush.html



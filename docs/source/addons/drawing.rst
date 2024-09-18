.. module:: ezdxf.addons.drawing

Drawing / Export Add-on
=======================

This add-on provides the functionality to render a DXF document to produce a
rasterized or vector-graphic image which can be saved to a file or viewed
interactively depending on the backend being used.

The module provides two example scripts in the folder ``examples/addons/drawing``
which can be run to save rendered images to files or view an interactive
visualisation.

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

.. seealso::

    How-to section for the FAQ about the :ref:`how_to_drawing_addon`.

Design
------

The implementation of the :mod:`drawing` add-on is divided into a frontend and
multiple backends. The frontend handles the translation of DXF features and
properties into simplified structures, which are then processed by the backends.

Common Limitations to all Backends
----------------------------------

- rich text formatting of the MTEXT entity is close to AutoCAD but not pixel perfect
- relative size of POINT entities cannot be replicated exactly
- rendering of ACIS entities is not supported
- no 3D rendering engine, therefore:

    - 3D entities are projected into the xy-plane and 3D text is not supported
    - only top view rendering of the modelspace
    - VIEWPORTS are always rendered as top view
    - no VISUALSTYLE support

- only basic support for:

  - infinite lines (rendered as lines with a finite length)
  - OLE2FRAME entities (rendered as rectangles)
  - vertical text (will render as horizontal text)
  - rendering of additional MTEXT columns may be incorrect

MatplotlibBackend
-----------------

.. autoclass:: ezdxf.addons.drawing.matplotlib.MatplotlibBackend(ax, *, adjust_figure=True, font=FontProperties(), use_text_cache=True)

The :class:`MatplotlibBackend` is used by the :ref:`draw_command` command of the
`ezdxf` launcher.

Example for the usage of the :mod:`Matplotlib` backend:

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


PyQtBackend
-----------

.. autoclass:: ezdxf.addons.drawing.pyqt.PyQtBackend(scene=None)

The :class:`PyQtBackend` is used by the :ref:`view_command` command of the
`ezdxf` launcher.

.. seealso::

    The `qtviewer.py`_ module implements the core of a simple DXF viewer and the
    `cad_viewer.py`_ example is a skeleton to show how to launch the
    :class:`CADViewer` class.

Recorder
--------

.. versionadded:: 1.1

This is a special backend which records the output of the :class:`~ezdxf.addons.drawing.frontend.Frontend`
class in compact numpy arrays and these recordings and can be played by a :class:`Player`
instance on one or more backends.
The recorded numpy arrays support measurement of bounding boxes and transformations
which is for some backends a requirement to place the DXF content on size limited pages.

.. autoclass:: ezdxf.addons.drawing.recorder.Recorder

    The class implements the :class:`BackendInterface` but does not record :meth:`enter_entity`,
    :meth:`exit_entity` and :meth:`clear` events.

    .. automethod:: player


.. autoclass:: ezdxf.addons.drawing.recorder.Player

    .. automethod:: bbox

    .. automethod:: copy

    .. automethod:: crop_rect

    .. automethod:: recordings

    .. automethod:: replay

    .. automethod:: transform

.. autoclass:: ezdxf.addons.drawing.recorder.Override


Layout
------

.. versionadded:: 1.1

The :class:`Layout` class builds the page layout and the matrix to transform the DXF
content to page coordinates according to the layout :class:`Settings`.
The DXF coordinate transformation is required for PDF and HPGL/2 which expects the
output coordinates in the first quadrant and SVG which has an inverted y-axis.

The :class:`Layout` class uses following classes and enums for configuration:

- :class:`~ezdxf.addons.drawing.layout.Page` - page definition
- :class:`~ezdxf.addons.drawing.layout.Margins` - page margins definition
- :class:`~ezdxf.addons.drawing.layout.Settings`  - configuration settings
- :class:`~ezdxf.addons.drawing.layout.Units`  - enum for page units

.. autoclass:: ezdxf.addons.drawing.layout.Page

    .. autoproperty:: is_landscape

    .. autoproperty:: is_portrait

    .. automethod:: from_dxf_layout

    .. automethod:: get_margin_rect

    .. automethod:: to_landscape

    .. automethod:: to_portrait

.. autoclass:: ezdxf.addons.drawing.layout.Margins

    .. automethod:: all

    .. automethod:: all2

    .. automethod:: scale


.. autoclass:: ezdxf.addons.drawing.layout.PageAlignment

.. autoclass:: ezdxf.addons.drawing.layout.Settings

.. autoclass:: ezdxf.addons.drawing.layout.Units

SVGBackend
----------

.. versionadded:: 1.1

.. autoclass:: ezdxf.addons.drawing.svg.SVGBackend

    .. automethod:: get_xml_root_element

    .. automethod:: get_string

Usage:

.. code-block:: Python

    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing import layout, svg

    doc = ezdxf.readfile("your.dxf")
    msp = doc.modelspace()
    backend = svg.SVGBackend()
    Frontend(RenderContext(doc), backend).draw_layout(msp)

    with open("your.svg", "wt") as fp:
        fp.write(backend.get_string(layout.Page(0, 0))

PyMuPdfBackend
--------------

.. versionadded:: 1.1

.. autoclass:: ezdxf.addons.drawing.pymupdf.PyMuPdfBackend

    .. automethod:: get_pdf_bytes

    .. automethod:: get_pixmap_bytes

Usage:

.. code-block:: Python

    import ezdxf
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing import layout, pymupdf

    doc = ezdxf.readfile("your.dxf")
    msp = doc.modelspace()
    backend = pymupdf.PyMuPdfBackend()
    Frontend(RenderContext(doc), backend).draw_layout(msp)

    with open("your.pdf", "wb") as fp:
        fp.write(backend.get_pdf_bytes(layout.Page(0, 0))


Load the output of the :class:`PyMuPdfBackend` into the :class:`Image` class of the `Pillow`_
package for further processing or to output additional image formats:

.. code-block:: Python

    import io
    from PIL import Image

    ...  # see above

    # the ppm format is faster to process than png
    fp = io.BytesIO(backend.get_pixmap_bytes(layout.Page(0, 0), fmt="ppm", dpi=300))
    image = Image.open(fp, formats=["ppm"])

PlotterBackend
--------------

.. versionadded:: 1.1

.. autoclass:: ezdxf.addons.drawing.hpgl2.PlotterBackend

    .. automethod:: get_bytes

    .. automethod:: compatible

    .. automethod:: low_quality

    .. automethod:: normal_quality

    .. automethod:: high_quality

Usage:

.. code-block:: Python

    import ezdxf
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing import layout, hpgl2

    doc = ezdxf.readfile("your.dxf")
    psp = doc.paperspace("Layout1")
    backend = hpgl2.PlotterBackend()
    Frontend(RenderContext(doc), backend).draw_layout(psp)
    page = layout.Page.from_dxf_layout(psp)

    with open("your.plt", "wb") as fp:
        fp.write(backend.normal_quality(page)

You can check the output by the HPGL/2 viewer::

    ezdxf hpgl your.plt

DXFBackend
----------

.. versionadded:: 1.1

.. autoclass:: ezdxf.addons.drawing.dxf.DXFBackend

.. autoclass:: ezdxf.addons.drawing.dxf.ColorMode

Render a paperspace layout into modelspace:

.. code-block:: Python

    import ezdxf
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing import layout, dxf

    doc = ezdxf.readfile("your.dxf")
    layout1 = doc.paperspace("Layout1")
    output_doc = ezdxf.new()
    output_msp = output_doc.modelspace()

    backend = dxf.DXFBackend(output_msp)
    Frontend(RenderContext(doc), backend).draw_layout(layout1)

    output_doc.saveas("layout1_in_modelspace.dxf")

GeoJSONBackend
--------------

.. versionadded:: 1.3.0

.. autoclass:: ezdxf.addons.drawing.json.GeoJSONBackend

CustomJSONBackend
-----------------

.. versionadded:: 1.3.0

.. autoclass:: ezdxf.addons.drawing.json.CustomJSONBackend


Configuration
-------------

Additional options for the drawing add-on can be passed by the `config`
argument of the :class:`Frontend` constructor :meth:`__init__()`. Not every
option will be supported by all backends.

Usage::

    my_config = Configuration(lineweight_scaling=2)

.. autoclass:: ezdxf.addons.drawing.config.Configuration

    .. automethod:: with_changes()

BackgroundPolicy
----------------

.. autoclass:: ezdxf.addons.drawing.config.BackgroundPolicy

ColorPolicy
-----------

.. autoclass:: ezdxf.addons.drawing.config.ColorPolicy

HatchPolicy
-----------

.. autoclass:: ezdxf.addons.drawing.config.HatchPolicy

ImagePolicy
-----------

.. autoclass:: ezdxf.addons.drawing.config.ImagePolicy

LinePolicy
----------

.. autoclass:: ezdxf.addons.drawing.config.LinePolicy

LineweightPolicy
----------------

.. autoclass:: ezdxf.addons.drawing.config.LineweightPolicy

ProxyGraphicPolicy
------------------

.. autoclass:: ezdxf.addons.drawing.config.ProxyGraphicPolicy

TextPolicy
----------

.. autoclass:: ezdxf.addons.drawing.config.TextPolicy

Properties
----------

.. autoclass:: ezdxf.addons.drawing.properties.Properties

    .. attribute:: color

        The actual color value of the DXF entity as "#RRGGBB" or "#RRGGBBAA"
        string. An alpha value of "00" is opaque and "ff" is fully transparent.

    .. attribute:: rgb

        RGB values extract from the :attr:`color` value as tuple of integers.

    .. attribute:: luminance

        Perceived luminance calculated from the :attr:`color` value as float in
        the range [0.0, 1.0].

    .. attribute:: linetype_name

        The actual linetype name as string like "CONTINUOUS"

    .. attribute:: linetype_pattern

        The simplified DXF linetype pattern as tuple of floats, all line
        elements and gaps are values greater than 0.0 and 0.0 represents a
        point. Line or point elements do always alternate with gap elements:
        line-gap-line-gap-point-gap and the pattern always ends with a gap.
        The continuous line is an empty tuple.

    .. attribute:: linetype_scale

        The scaling factor as float to apply to the :attr:`linetype_pattern`.

    .. attribute:: lineweight

        The absolute lineweight to render in mm as float.

    .. attribute:: is_visible

        Visibility flag as bool.

    .. attribute:: layer

        The actual layer name the entity resides on as UPPERCASE string.

    .. attribute:: font

        The :class:`FontFace` used for text rendering or ``None``.

    .. attribute:: filling

        The actual :class:`Filling` properties of the entity or ``None``.

    .. attribute:: units

        The actual drawing units as :class:`~ezdxf.enums.InsertUnits` enum.


LayerProperties
---------------

.. class:: ezdxf.addons.drawing.properties.LayerProperties

    Actual layer properties, inherits from class :class:`Properties`.

    .. attribute:: is_visible

        Modified meaning: whether entities belonging to this layer should be drawn

    .. attribute:: layer

        Modified meaning: stores real layer name (mixed case)

LayoutProperties
----------------

.. class:: ezdxf.addons.drawing.properties.LayoutProperties

    Actual layout properties.

    .. attribute:: name

        Layout name as string

    .. attribute:: units

        Layout units as :class:`~ezdxf.enums.InsertUnits` enum.

    .. autoproperty:: background_color

    .. autoproperty:: default_color

    .. autoproperty:: has_dark_background

    .. automethod:: set_colors

RenderContext
-------------

.. autoclass:: ezdxf.addons.drawing.properties.RenderContext

    .. automethod:: resolve_aci_color

    .. automethod:: resolve_all

    .. automethod:: resolve_color

    .. automethod:: resolve_filling

    .. automethod:: resolve_font

    .. automethod:: resolve_layer

    .. automethod:: resolve_layer_properties

    .. automethod:: resolve_linetype

    .. automethod:: resolve_lineweight

    .. automethod:: resolve_units

    .. automethod:: resolve_visible

    .. automethod:: set_current_layout

    .. automethod:: set_layer_properties_override

The :class:`RenderContext` class can be used isolated from the :mod:`drawing`
add-on to resolve DXF properties.

Frontend
--------

.. autoclass:: ezdxf.addons.drawing.frontend.Frontend(ctx: RenderContext, out: BackendInterface, config: Configuration = Configuration.defaults(), bbox_cache: ezdxf.bbox.Cache = None)

    .. automethod:: log_message

    .. automethod:: skip_entity

    .. automethod:: override_properties

    .. automethod:: push_property_override_function

    .. automethod:: pop_property_override_function

    .. automethod:: draw_layout


BackendInterface
----------------

.. class:: ezdxf.addons.drawing.backend.BackendInterface

    Public interface definition for 2D rendering backends.

    For more information read the source code: `backend.py`_


Backend
--------

.. class:: ezdxf.addons.drawing.backend.Backend

    Abstract base class for concrete backend implementations and
    implements some default features.

    For more information read the source code: `backend.py`_


Details
-------

The rendering is performed in two stages. The frontend traverses the DXF document
structure, converting each encountered entity into primitive drawing commands.
These commands are fed to a backend which implements the interface:
:class:`~ezdxf.addons.drawing.backend.Backend`.

Although the resulting images will not be pixel-perfect with AutoCAD (which was
taken as the ground truth when developing this add-on) great care has been taken
to achieve similar behavior in some areas:

- The algorithm for determining color should match AutoCAD. However, the color
  palette is not stored in the DXF file, so the chosen colors may be different
  to what is expected. The :class:`~ezdxf.addons.drawing.properties.RenderContext`
  class supports passing a plot style table (:term:`CTB`-file) as custom color
  palette but uses the same palette as AutoCAD by default.
- Text rendering is quite accurate, text positioning, alignment and word wrapping
  are very faithful. Differences may occur if a different font from what was
  used by the CAD application but even in that case, for supported backends,
  measurements are taken of the font being used to match text as closely as possible.
- Visibility determination (based on which layers are visible) should match AutoCAD

.. seealso::

    - `draw_cad.py`_ for a simple use of this module
    - `cad_viewer.py`_ for an advanced use of this module
    - :ref:`notes_on_rendering_dxf_content` for additional behaviours documented
      during the development of this add-on.


.. _Triangulation: https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf
.. _MatplotlibHatch: https://matplotlib.org/3.2.1/gallery/shapes_and_collections/hatch_demo.html
.. _QtBrushHatch: https://doc.qt.io/qt-5/qbrush.html
.. _cad_viewer.py: https://github.com/mozman/ezdxf/blob/master/examples/addons/drawing/cad_viewer.py
.. _draw_cad.py: https://github.com/mozman/ezdxf/blob/master/examples/addons/drawing/draw_cad.py
.. _qtviewer.py: https://github.com/mozman/ezdxf/blob/master/src/ezdxf/addons/drawing/qtviewer.py
.. _backend.py: https://github.com/mozman/ezdxf/blob/master/src/ezdxf/addons/drawing/backend.py
.. _Pillow: https://pypi.org/project/Pillow/

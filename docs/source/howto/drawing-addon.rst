.. _how_to_drawing_addon:

Drawing Add-on
==============

This section consolidates the `FAQ`_ about the drawing add-on from the github
forum.

Matplotlib Backend
------------------

.. _matplotlib_how_to_get_pixel_coordinates:

How to Get the Pixel Coordinates of DXF Entities
++++++++++++++++++++++++++++++++++++++++++++++++

.. seealso::

    - Source: https://github.com/mozman/ezdxf/discussions/219

Transformation from modelspace coordinates to image coordinates:

.. code-block:: Python

    import matplotlib.pyplot as plt
    from PIL import Image, ImageDraw

    import ezdxf
    from ezdxf.math import Matrix44
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    def get_wcs_to_image_transform(
        ax: plt.Axes, image_size: tuple[int, int]
    ) -> Matrix44:
        """Returns the transformation matrix from modelspace coordinates to image
        coordinates.
        """

        x1, x2 = ax.get_xlim()
        y1, y2 = ax.get_ylim()
        data_width, data_height = x2 - x1, y2 - y1
        image_width, image_height = image_size
        return (
            Matrix44.translate(-x1, -y1, 0)
            @ Matrix44.scale(
                image_width / data_width, -image_height / data_height, 1.0
            )
            # +1 to counteract the effect of the pixels being flipped in y
            @ Matrix44.translate(0, image_height + 1, 0)
        )

    # create the DXF document
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (1, 0), (1, 1), (0, 1)], close=True)
    msp.add_line((0, 0), (1, 1))

    # export the pixel image
    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    fig.savefig("cad.png")
    plt.close(fig)

    # reload the pixel image by Pillow (PIL)
    img = Image.open("cad.png")
    draw = ImageDraw.Draw(img)

    # add some annotations to the pixel image by using modelspace coordinates
    m = get_wcs_to_image_transform(ax, img.size)
    a, b, c = (
        (v.x, v.y)  # draw.line() expects tuple[float, float] as coordinates
        # transform modelspace coordinates to image coordinates
        for v in m.transform_vertices([(0.25, 0.75), (0.75, 0.25), (1, 1)])
    )
    draw.line([a, b, c, a], fill=(255, 0, 0))

    # show the image by the default image viewer
    img.show()

.. _matplotlib_how_to_get_msp_coordinates:

How to Get Modelspace Coordinates from Pixel Coordinates
++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This is the reverse operation of the previous how-to: :ref:`matplotlib_how_to_get_pixel_coordinates`

.. seealso::

    - Full example script: `wcs_to_image_coordinates.py`_
    - Source: https://github.com/mozman/ezdxf/discussions/269

.. code-block:: Python

    def get_image_to_wcs_transform(
        ax: plt.Axes, image_size: tuple[int, int]
    ) -> Matrix44:
        m = get_wcs_to_image_transform(ax, image_size)
        m.inverse()
        return m

    # -x-x-x snip -x-x-x-

    img2wcs = get_image_to_wcs_transform(ax, img.size)
    print(f"0.25, 0.75 == {img2wcs.transform(a).round(2)}")
    print(f"0.75, 0.25 == {img2wcs.transform(b).round(2)}")
    print(f"1.00, 1.00 == {img2wcs.transform(c).round(2)}")


.. _matplotlib_export_specific_area:

How to Export a Specific Area of the Modelspace
+++++++++++++++++++++++++++++++++++++++++++++++

This code exports the specified modelspace area from (5, 3) to (7, 8) as a
2x5 inch PNG image to maintain the aspect ratio of the source area.

.. seealso::

    - Full example script: `export_specific_area.py`_
    - Source: https://github.com/mozman/ezdxf/discussions/451

.. code-block:: Python

    # -x-x-x snip -x-x-x-

    # export the pixel image
    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)

    # setting the export area:
    xmin, xmax = 5, 7
    ymin, ymax = 3, 8
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # set the output size to get the expected aspect ratio:
    fig.set_size_inches(xmax - xmin, ymax - ymin)
    fig.savefig("x5y3_to_x7y8.png")



.. _FAQ: https://github.com/mozman/ezdxf/discussions/550
.. _wcs_to_image_coordinates.py: https://github.com/mozman/ezdxf/blob/master/examples/addons/drawing/wcs_to_image_coodinates.py
.. _export_specific_area.py: https://github.com/mozman/ezdxf/blob/master/examples/addons/drawing/export_specific_area.py
DXF Viewer
==========

A360 Viewer Problems
--------------------

AutoDesk web service A360_ seems to be more picky than the AutoCAD desktop applications, may be it helps to use the
latest DXF version supported by ezdxf, which is DXF R2018 (AC1032) in the year of writing this lines (2018).

DXF Entities Are Not Displayed in the Viewer
--------------------------------------------

`ezdxf` does not automatically locate the main viewport of the modelspace at the entities, you have to perform the
"Zoom to Extends" command, here in TrueView 2020:

.. image:: gfx/trueview_2020_zoom_to_extends.png
    :align: center

And here in the Autodesk Online Viewer:

.. image:: gfx/autodesk_online_viewer_zoom_to_extends.png
    :align: center

Add this line to your code to relocate the main viewport, adjust the `center` (in modelspace coordinates) and
the `height` (in drawing units) arguments to your needs::

    doc.set_modelspace_vport(height=10, center=(0, 0))

Show IMAGES/XREFS on Loading in AutoCAD
---------------------------------------

If you are adding XREFS and IMAGES with relative paths to existing drawings and they do not show up in AutoCAD
immediately, change the HEADER variable :code:`$PROJECTNAME=''` to *(not really)* solve this problem.
The ezdxf templates for DXF R2004 and later have :code:`$PROJECTNAME=''` as default value.

Thanks to `David Booth <https://github.com/worlds6440>`_:

    If the filename in the IMAGEDEF contains the full path (absolute in AutoCAD) then it shows on loading,
    otherwise it won't display (reports as unreadable) until you manually reload using XREF manager.

    A workaround (to show IMAGES on loading) appears to be to save the full file path in the DXF or save it as a DWG.

So far - no solution for showing IMAGES with relative paths on loading.

Set Initial View/Zoom for the Modelspace
----------------------------------------

See section "General Document": :ref:`set msp initial view`


.. _A360: https://a360.autodesk.com/viewer/

.. _tut_psp_viewports:

Tutorial for Viewports in Paperspace
====================================

This tutorial is based on the example script `viewports_in_paperspace.py`.
The script creates DXF files for the version R12 and for R2000+, but the
export for DXF R12 has a wrong papersize in BricsCAD and wrong margins in
Autodesk DWG Trueview. I don't know why this happens and I don't waste my time
to fix this.

.. important::

    If you need paperspace layouts use DXF version R2000 or newer because
    the export of the page dimensions does not work for DXF R12!

The scripts creates three flat geometries in the xy-plane of the :ref:`WCS` and a
3D mesh as content of the modelspace:

.. image:: gfx/vp-tut-msp-content.png
    :align: center

Page Setup
----------

Viewport Setup
--------------

.. _viewports_in_paperspace.py: https://github.com/mozman/ezdxf/blob/master/examples/viewports_in_paperspace.py
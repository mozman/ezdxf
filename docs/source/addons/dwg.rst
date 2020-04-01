.. _dwg_addon:

DWG Loader
==========

Load a DXF file from a DWG file, which means this add-on convert DWG data into DXF tags and load this data into
an :class:`~ezdxf.drawing.Drawing` object. This add-on can not export :term:`DWG` files and support for this feature is not
planned.

Supported DWG versions so far:

    - None (alpha phase)

Usage:

.. code-block::

    from ezdxf.addons import dwg

    # This creates a regular ezdxf document.
    doc = dwg.readfile('my.dwg')

    # Save the document as DXF file but some DWG features will be lost.
    doc.saveas('my.dxf')

.. module:: ezdxf.addons.dwg

.. autofunction:: readfile

.. autofunction:: load

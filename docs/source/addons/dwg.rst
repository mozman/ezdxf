.. _dwg_addon:

DWG Loader
==========

Load a DXF file from a DWG file, which means this add-on convert DWG data into DXF tags and load this data into
an :class:`~ezdxf.document.Drawing` object. This add-on can not export :term:`DWG` files and support for this feature is not
planned.

Load DXF structures from a :term:`DWG` file, which means this add-on convert data stored in a DWG file into
:term:`DXF` tags and load this tags into a regular class:`~ezdxf.document.Drawing` object. This process is not
perfect and much data from the DWG file will be lost by saving the document as DXF file,
**don’t use this add-on as DWG to DXF converter**,
there are much better tools available for free like the `ODA File Converter`_.

Loading DWG files is much slower than loading DXF files, because of the required complex bit stream decoding.

This add-on can not export DWG files and support for this feature is not planned.

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

.. _ODA File Converter: https://www.opendesign.com/guestfiles/oda_file_converter
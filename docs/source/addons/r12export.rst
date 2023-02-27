.. _r12export_addon:

.. module:: ezdxf.addons.r12export

R12 Export
==========

.. versionadded:: 1.1

This module exports any DXF file as a simple DXF R12 file. Many complex entities will be
converted into DXF primitives.  This exporter is intended for creating a simple file
format as an input format for other software such as laser cutters. In order to get a
file that can be edited well in a CAD application, the results of the ODA file converter
are much better.

Usage
-----

.. code-block:: Python

    import ezdxf
    from ezdxf.addons import r12export

    doc = ezdxf.readfile("any.dxf")
    r12export.saveas(doc, "r12.dxf")

Converted Entity Types
----------------------

=============== ===
LWPOLYLINE      translated to POLYLINE
MESH            translated to POLYLINE (PolyfaceMesh)
SPLINE          flattened to POLYLINE
ELLIPSE         flattened to POLYLINE
MTEXT           exploded into DXF primitives
LEADER          exploded into DXF primitives
MLEADER         exploded into DXF primitives
MULTILEADER     exploded into DXF primitives
MLINE           exploded into DXF primitives
HATCH           exploded into DXF primitives
MPOLYGON        exploded into DXF primitives
ACAD_TABLE      export of pre-rendered BLOCK content
=============== ===

For proxy- or unknown entities the available proxy graphic will be exported as DXF
primitives.

Limitations
-----------

- Explosion of MTEXT into DXF primitives is not perfect
- Pattern rendering for complex HATCH entities has issues
- Solid fill rendering for complex HATCH entities has issues

ODA File Converter
------------------

The advantage of the :mod:`~ezdxf.addons.r12export` module is that the ODA file converter
isn't needed, but the ODA file converter will produce a much better result:

.. code-block:: Python

    from ezdxf.addons import odafc

    odafc.convert("any.dxf", "r12.dxf", version="R12")


Functions
---------

.. autosummary::
    :nosignatures:

    write
    saveas
    convert

.. autofunction:: write

.. autofunction:: saveas

.. autofunction:: convert

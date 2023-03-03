.. _r12strict:

.. module:: ezdxf.r12strict

r12strict
=========

.. versionadded:: 1.1

Due to ACAD release 14 the resource names, such as layer-, linetype, text style-,
dimstyle- and block names, were limited to 31 characters in length and all names were
uppercase.

Names can include the letters A to Z, the numerals 0 to 9, and the special characters,
dollar sign ``"$"``, underscore ``"_"``, hyphen ``"-"`` and the asterix ``"*"`` as
first character for special names like anonymous blocks.
Most applications do not care about that and work fine with longer names and any
characters used in names for some exceptions, but of course Autodesk applications are
very picky about that.

The function :func:`make_acad_compatible` makes DXF R12 drawings to 100% compatible to
Autodesk products and does everything at once, but the different processing steps can
be called manually.

.. important::

    This module can only process DXF R12 file and will throw a :class:`DXFVersionError`
    otherwise. For exporting any DXF document as DXF R12 use the
    :mod:`ezdxf.addons.r12export` add-on.

Usage
-----

.. code-block:: Python

    import ezdxf
    from ezdxf import r12strict

    doc = ezdxf.readfile("r12sloppy.dxf")
    r12strict.make_acad_compatible(doc)
    doc.saveas("r12strict.dxf")

Functions
---------

.. autosummary::
    :nosignatures:

    make_acad_compatible
    translate_names
    clean

.. autofunction:: make_acad_compatible

.. autofunction:: translate_names

.. autofunction:: clean

.. autoclass:: R12NameTranslator

    .. automethod:: reset

    .. automethod:: translate

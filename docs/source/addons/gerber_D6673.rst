.. _gerber_D6673:

ASTM-D6673-10 Exporter
======================

.. module:: ezdxf.addons.gerber_D6673

This add-on creates special DXF files for use by Gerber Technology applications which
have a low quality DXF parser and cannot parse/ignore BLOCKS which do not contain
data according the ASTM-D6673-10 standard.  The function :func:`export_file` exports
DXF R12 and only DXF R12 files which do not contain the default "$MODEL_SPACE" and
"$PAPER_SPACE" layout block definitions, have an empty HEADER section and no TABLES
section.  These special requirements of the Gerber Technology parser are annoying, but
correspond to the DXF R12 standard.

Autodesk applications maybe complain about invalid BLOCK names such as "Shape 0_M", which
in my opinion are valid, maybe spaces were not allowed in the original R12 version, but
this is just a minor issue and is more a problem of the picky Autodesk DXF parser, which
is otherwise very forgiving for DXF R12 files.

.. code-block:: Python

    import ezdxf
    from ezdxf.addons import gerber_D6673

    doc = ezdxf.new("R12")  # the export function rejects other DXF versions
    msp = doc.modelspace()

    # Create your content according the ASTM-D6673-10 standard
    # Do not use any linetypes or text styles, the TABLES section will not be exported.
    # The ASTM-D6673-10 standard supports only 7-bit ASCII characters.

    gerber_D6673.export_file(doc, "gerber_file.dxf")

.. autofunction:: export_file

.. autofunction:: export_stream


.. _tut_underlay:

Tutorial for Underlay and UnderlayDefinition
============================================

This example shows hot to insert a a PDF, DWF, DWFx or DGN file as drawing
underlay. Each UNDERLAY entity requires an associated UNDERLAYDEF entity in the
objects section, which stores the filename of the linked document and the
parameters of the underlay. Multiple UNDERLAY entities can share the same
UNDERLAYDEF entity.

.. important::

    The underlay file is NOT embedded into the DXF file:

.. code-block:: Python

    import ezdxf


    doc = ezdxf.new('AC1015')  # underlay requires the DXF R2000 format or later
    my_underlay_def = doc.add_underlay_def(filename='my_underlay.pdf', name='1')
    # The (PDF)DEFINITION entity is like a block definition, it just defines the underlay
    # 'name' is misleading, because it defines the page/sheet to be displayed
    # PDF: name is the page number to display
    # DGN: name='default' ???
    # DWF: ????

    msp = doc.modelspace()
    # add first underlay
    msp.add_underlay(my_underlay_def, insert=(2, 1, 0), scale=0.05)
    # The (PDF)UNDERLAY entity is like the INSERT entity, it creates an underlay reference,
    # and there can be multiple references to the same underlay in a drawing.

    msp.add_underlay(my_underlay_def, insert=(4, 5, 0), scale=.5, rotation=30)

    # get existing underlay definitions, Important: UNDERLAYDEFs resides in the objects section
    pdf_defs = doc.objects.query('PDFDEFINITION')  # get all pdf underlay defs in drawing

    doc.saveas("dxf_with_underlay.dxf")


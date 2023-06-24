.. _tut_xref_module:

Tutorial for External References
================================

This tutorial uses the :mod:`ezdxf.xref` module to work with external references (XREF).

Attached XREFs are links to the modelspace of a specified drawing file. Changes made
to the referenced drawing are automatically reflected in the current drawing when it's
opened or if the XREF is reloaded.

.. important::

    **AutoCAD can only display DWG files as attached XREFs.**
    Any DXF file attached as an XREF to a DXF document must be converted to DWG in order
    to be viewed in AutoCAD.
    Fortunately, other CAD applications are more cooperative, BricsCAD has no problem
    displaying DXF files as XREFs.

    The :mod:`~ezdxf.addons.drawing` add-on included in `ezdxf` **does not display external
    references at all!**

There are some example files included in the `examples/xref <https://github.com/mozman/ezdxf/tree/master/examples/xref>`_
folder of the repository:

    - attach_dxf_dwg_xref.py
    - detach_block_as_xref.py
    - embed_dxf_dwg_xref.py
    - load_table_resources.py

Environment Setup
-----------------

Required imports:

.. literalinclude:: src/xref/attach_dxf_dwg_xref.py
    :lines: 3-9

Function to create a simple DXF file as XREF, the insertion point of the XREF is set to
(5, 5):

.. literalinclude:: src/xref/attach_dxf_dwg_xref.py
    :lines: 14-26

Create the DXF file::

    make_dxf_xref_document("xref.dxf")

The XREF looks like this:

.. image:: gfx/xref_doc.png
    :align: center

Attach a DXF File
-----------------

Create a host document to which the XREF will be attached::

    host_doc = ezdxf.new(DXFVERSION, units=units.M)

Attach the XREF by the :func:`ezdxf.xref.attach` function and save the host DXF file::

    xref.attach(host_doc, block_name="dxf_xref", insert=(0, 0), filename="attached_xref.dxf")
    host_doc.set_modelspace_vport(height=10, center=(0, 0))
    host_doc.saveas("attach_host_dxf.dxf")


The :func:`attach` function is meant to simply attach an XREF once without any
overhead, therefore the :func:`attach` function creates the required block definition
automatically and raises an :class:`XrefDefinitionError` exception if the block definition
already exist. To attach additional XREF references use the method
:meth:`~ezdxf.layouts.BaseLayout.add_blockref`::

    msp.add_blockref("dxf_xref", insert=another_location)


The attached DXF file in BricsCAD:

.. image:: gfx/xref_attached_dxf.png
    :align: center

.. important::

    AutoCAD can not display DXF files as attached XREFs.

Attach a DWG File
-----------------

Export the DXF file as DWG by the :mod:`~ezdxf.addons.odafc` add-on::

    # It's not required to save the DXF file!
    doc = make_dxf_xref_document("attached_xref.dxf")
    try:
        odafc.export_dwg(doc, "attached_xref.dwg", replace=True)
    except odafc.ODAFCError as e:
        print(str(e))

Attach the DWG file by the :func:`ezdxf.xref.attach` function and save the host DXF file::

    host_doc = ezdxf.new(DXFVERSION, units=units.M)
    xref.attach(host_doc, block_name="dwg_xref", filename="attached_xref.dwg", insert=(0, 0))
    host_doc.set_modelspace_vport(height=10, center=(0, 0))
    host_doc.saveas("attached_dwg.dxf")


Attached DWG file in Autodesk DWG TrueView 2023:

.. image:: gfx/xref_attached_dwg.png
    :align: center

Detach an XREF
--------------

The :func:`~ezdxf.xref.detach` function writes the content of a block definition into
the modelspace of a new DXF document and convert the block to an external reference (XREF).
The new DXF document has to be written/exported by the caller.
The function does not create any block references. These references should already exist
and do not need to be changed since references to blocks and XREFs are the same.

.. literalinclude:: src/xref/detach_dxf_dwg_xref.py
    :lines: 23-29

.. important::

    Save the host document after detaching the block!
    Detaching a block definition modifies the host document.

The :func:`detach` function returns a :class:`Drawing` instance, so it's possible
to convert the DXF document to DWG by the :mod:`~ezdxf.addons.odafc` add-on if necessary
(e.g. for Autodesk products). It's important that the argument :attr:`xref_filename`
match the filename of the exported DWG file:

.. literalinclude:: src/xref/detach_dxf_dwg_xref.py
    :lines: 33-42

It's recommended to clean up the entity database of the host document afterwards::

    host_doc.entitydb.purge()

For understanding, this is the :func:`make_block` function:

.. literalinclude:: src/xref/detach_dxf_dwg_xref.py
    :lines: 10-19

Embed an XREF
-------------

For loading the content of DWG files is a loading function required, which loads the
DWG file as :class:`Drawing` document. The :mod:`~ezdxf.addons.odafc` add-on module
provides such a function: :func:`~ezdxf.addons.odafc.readfile`

Load Modelspace
---------------

Load Paperspace
---------------

Write Block
-----------

Load Table Resources
--------------------

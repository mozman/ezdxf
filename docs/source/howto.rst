Howto
=====

General preconditions::

    import ezdxf
    dwg = ezdxf.readfile("your_dxf_file.dxf")
    modelspace = dwg.modelspace()

.. _howto_get_attribs:

Get/Set block reference attributes
----------------------------------

Block references (:class:`Insert`) can have attached attributes (:class:`Attrib`), these are simple text annotations
with an associated tag appended to the block reference.

Iterate over all appended attributes::

    blockrefs = modelspace.query('INSERT[name=="Part12"]')  # get all INSERT entities with entity.dxf.name == "Part12"
    if len(blockrefs):
        entity = blockrefs[0]  # process first entity found
        for attrib in entity.attribs():
            if attrib.dxf.tag == "diameter":  # identify attribute by tag
                attrib.dxf.text = "17mm"  # change attribute content


Get attribute by tag::

    diameter = entity.get_attrib('diameter')
    if diameter is not None:
        diameter.dxf.text = "17mm"

.. _howto_reduce_memory_footprint:

Reduce Memory Footprint
-----------------------

- compress binary data by :meth:`Drawing.compress_binary_data`
- compress useless sections like `THUMBNAILIMAGE` by setting :code:`ezdxf.options.compress_default_chunks = True`,
  *before* opening the DXF file.

.. warning:: Data compression costs time: *memory usage* vs *run time*

.. _howto_create_more_readable_dxf_files:

Create More Readable DXF Files (DXF Pretty Printer)
---------------------------------------------------

DXF files are plain text files, you can open this files with every text editor which handles bigger files.
But it is not really easy to get quick the information you want.

Create a more readable HTML file (DXF Pretty Printer)::

    # on Windows
    py -3 -m ezdxf.pp your_dxf_file.dxf

    # on Linux/Mac
    python3 -m ezdxf.pp your_dxf_file.dxf

This produces a HTML file *your_dxf_file.html* with a nicer layout than a plain DXF file and DXF handles as links
between DXF entities, this simplifies the navigation between the DXF entities.

.. important:: This does not render the graphical content of the DXF file to a HTML canvas element.

Adding New XDATA to Entity
--------------------------

Adding XDATA as list of tuples (group code, value)::

    dwg.appids.new('YOUR_APP_NAME')  # IMPORTANT: create an APP ID entry

    circle = modelspace.add_circle((10, 10), 100)
    circle.tags.new_xdata('YOUR_APP_NAME',
                     [
                         (1000, 'your_web_link.org'),
                         (1002, '{'),
                         (1000, 'some text'),
                         (1002, '{'),
                         (1071, 1),
                         (1002, '}'),
                         (1002, '}')
                     ])

For group code meaning see DXF reference section `DXF Group Codes in Numerical Order Reference`, valid group codes are
in the range 1000 - 1071.

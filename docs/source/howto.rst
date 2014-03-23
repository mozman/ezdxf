Howto
=====

General preconditions::

    import ezdxf
    dwg = ezdxf.readfile("your_dxf_file.dxf")
    modelspace = dwg.modelspace()

.. _howto get attribs:

Get/Set block reference attributes
----------------------------------

Block references (:class:`Insert`) can have attached attributes (:class:`Attrib`), these are simple text annotations
with an associated tag appended to the block reference.

Iterate over all appended attributes::

    blockrefs = modelspace.query('INSERT[name=="Part12"]')  # get all INSERT entities with entity.dxf.name == "Part12"
    entity = blockrefs[0]  # process first entity found
    for attrib in entity:
        if attrib.dxf.tag == "diameter":  # identify attribute by tag
            attrib.dxf.text = "17mm"  # change attribute content


Get attribute by tag::

    diameter = entity.get_attrib('diameter')
    if diameter is not None:
        diameter.dxf.text = "17mm"

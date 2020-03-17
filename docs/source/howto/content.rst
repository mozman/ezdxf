Content
=======

General preconditions:

.. code-block:: python

    import ezdxf
    doc = ezdxf.readfile("your_dxf_file.dxf")
    msp = doc.modelspace()

.. _howto_get_attribs:

Get/Set Block Reference Attributes
----------------------------------

Block references (:class:`~ezdxf.entities.Insert`) can have attached attributes (:class:`~ezdxf.entities.Attrib`),
these are simple text annotations with an associated tag appended to the block reference.

Iterate over all appended attributes:

.. code-block:: python

    # get all INSERT entities with entity.dxf.name == "Part12"
    blockrefs = msp.query('INSERT[name=="Part12"]')
    if len(blockrefs):
        entity = blockrefs[0]  # process first entity found
        for attrib in entity.attribs():
            if attrib.dxf.tag == "diameter":  # identify attribute by tag
                attrib.dxf.text = "17mm"  # change attribute content

.. versionchanged:: 0.10

    :meth:`attribs` replaced by a ``list`` of :class:`~ezdxf.entities.Attrib` objects, new code:

.. code-block:: python

    for attrib in entity.attribs:
        if attrib.dxf.tag == "diameter":  # identify attribute by tag
            attrib.dxf.text = "17mm"  # change attribute content

Get attribute by tag:

.. code-block:: python

    diameter = entity.get_attrib('diameter')
    if diameter is not None:
        diameter.dxf.text = "17mm"


Adding XDATA to Entities
------------------------

Adding XDATA as list of tuples (group code, value) by :meth:`~ezdxf.entities.DXFEntity.set_xdata`, overwrites
data if already present:

.. code-block:: python

    doc.appids.new('YOUR_APPID')  # IMPORTANT: create an APP ID entry

    circle = msp.add_circle((10, 10), 100)
    circle.set_xdata(
        'YOUR_APPID',
        [
            (1000, 'your_web_link.org'),
            (1002, '{'),
            (1000, 'some text'),
            (1002, '{'),
            (1071, 1),
            (1002, '}'),
            (1002, '}')
        ])

For group code meaning see DXF reference section `DXF Group Codes in Numerical Order Reference`_, valid group codes are
in the range 1000 - 1071.

Method :meth:`~ezdxf.entities.DXFEntity.get_xdata` returns the extended data for an entity as
:class:`~ezdxf.lldxf.tags.Tags` object.

.. _DXF Group Codes in Numerical Order Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-3F0380A5-1C15-464D-BC66-2C5F094BCFB9
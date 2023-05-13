.. _arch-usr:

Usage for Beginners
===================

This section shows the intended usage of the `ezdxf` package.
This is just a brief overview for new `ezdxf` users, follow the provided links
for more detailed information.


First import the package::

    import ezdxf

Loading DXF Files
-----------------

`ezdxf` supports loading ASCII and binary DXF documents from a file::

    doc = ezdxf.readfile(filename)

or from a zip-file::

    doc = ezdxf.readzip(zipfilename[, filename])

Which loads the DXF document `filename` from the zip-file `zipfilename` or the
first DXF file in the zip-file if `filename` is absent.

It is also possible to read a DXF document from a stream by the :func:`ezdxf.read`
function, but this is a more advanced feature, because this requires detection
of the file encoding in advance.

This works well with DXF documents from trusted sources like AutoCAD or BricsCAD.
For loading DXF documents with minor or major flaws use the :mod:`ezdxf.recover`
module.

.. seealso::

    Documentation for :func:`ezdxf.readfile`, :func:`ezdxf.readzip` and
    :func:`ezdxf.read`, for more information about file
    management go to the :ref:`dwgmanagement` section. For loading DXF documents
    with structural errors look at the :mod:`ezdxf.recover` module.

Layouts and Blocks
------------------

Layouts are containers for DXF entities like LINE or CIRCLE. The most important
layout is the modelspace labeled as "Model" in CAD applications which represents
the "world" work space. Paperspace layouts represents plottable sheets which
contains often the framing and the tile block of a drawing and VIEWPORT entities
as scaled and clipped "windows" into the modelspace.

The modelspace is always present and can not be deleted. The active paperspace
is also always present in a new DXF document but can be deleted, in that case
another paperspace layout gets the new active paperspace, but you can not delete
the last paperspace layout.

Getting the modelspace of a DXF document::

    msp = doc.modelspace()

Getting a paperspace layout by the name as shown in the tab of a
CAD application::

    psp = doc.paperspace("Layout1")

A block is just another kind of entity space, which can be inserted
multiple times into other layouts and blocks by the INSERT entity also called
block references, this is a very powerful and an important concept of the DXF
format.

Getting a block layout by the block name::

    blk = doc.blocks.get("NAME")


All these layouts have factory functions to create graphical DXF entities for
their entity space, for more information about creating entities see section:
`Create new DXF Entities`_

Query DXF Entities
------------------

As said in the `Layouts and Blocks`_ section, all graphical DXF entities are
stored in layouts, all these layouts can be iterated and do support the index
operator e.g. :code:`layout[-1]` returns the last entity.

The main difference between iteration and index access is, that iteration filters
destroyed entities, but the index operator returns also destroyed entities
until these entities are purged by :code:`layout.purge()`, more about this topic
in section: `Delete Entities`_.

There are two advanced query methods: :meth:`~ezdxf.layouts.BaseLayout.query`
and :meth:`~ezdxf.layouts.BaseLayout.groupby`.

Get all lines of layer ``"MyLayer"``::

    lines = msp.query('LINE[layer=="MyLayer"]')

This returns an :class:`~ezdxf.query.EntityQuery` container, which also provides
the same :meth:`query` and :meth:`groupby` methods.

Get all lines categorized by a DXF attribute like color::

    all_lines_by_color = msp.query("LINE").groupby("color")
    lines_with_color_1 = all_lines_by_color.get(1, [])

The :meth:`groupby` method returns a regular Python :class:`dict` with colors as
key and a regular Python :class:`list` of entities as values
(not an :class:`~ezdxf.query.EntityQuery` container).

.. seealso::

    For more information go to the :ref:`tut_getting_data`

Examine DXF Entities
--------------------

Each DXF entity has a :attr:`dxf` namespace attribute, which stores the named
DXF attributes, some entity attributes and assets are only available from
Python properties or methods outside the :attr:`dxf` namespace like the
vertices of the LWPOLYLINE entity. More information about the DXF attributes of
each entity can found in the documentation of the :mod:`ezdxf.entities` module.

Get some basic DXF attributes::

    layer = entity.dxf.layer  # default is "0"
    color = entity.dxf.color  # default is 256 = BYLAYER

Most DXF attributes have a default value, which will be returned if the DXF
attribute is not present, for DXF attributes without a default value you can
check if the attribute really exist::

    entity.dxf.hasattr("true_color")

or use the :meth:`get` method and provide a default value::

    entity.dxf.get("true_color", 0)

.. seealso::

    - :ref:`Common graphical DXF attributes`
    - Helper class :class:`ezdxf.gfxattribs.GfxAttribs` for building DXF attribute
      dictionaries.

Create a New DXF File
---------------------

Create new document for the latest supported DXF version::

    doc = ezdxf.new()

Create a new DXF document for a specific DXF version, e.g. for DXF R12::

    doc = ezdxf.new("R12")


The :func:`ezdxf.new` function can create some standard resources, such as
linetypes and text styles, by setting the argument `setup` to ``True``::

    doc = ezdxf.new(setup=True)

.. seealso::

    - :ref:`tut_simple_drawings`
    - Documentation for :func:`ezdxf.new`, for more information about file
      management go to the :ref:`dwgmanagement` section.

Create New DXF Entities
-----------------------

The factory methods for creating new graphical DXF entities are located in the
:class:`~ezdxf.layouts.BaseLayout` class and these factory methods are
available for all entity containers:

    - :class:`~ezdxf.layouts.Modelspace`
    - :class:`~ezdxf.layouts.Paperspace`
    - :class:`~ezdxf.layouts.BlockLayout`

The usage is simple::

    msp = doc.modelspace()
    msp.add_line((0, 0), (1, 0), dxfattribs={"layer": "MyLayer"})


A few important/required DXF attributes are explicit method arguments,
most additional DXF attributes are gives as a regular Python
:class:`dict` object by the keyword only argument :attr:`dxfattribs`.
The supported DXF attributes can be found in the documentation of the
:mod:`ezdxf.entities` module.

.. warning::

    Do not instantiate DXF entities by yourself and add them to layouts, always
    use the provided factory methods to create new graphical entities, this is
    the intended way to use `ezdxf`.

.. seealso::

    - :ref:`thematic_factory_method_index`
    - :ref:`tut_simple_drawings`
    - :ref:`tut_dxf_primitives`
    - :ref:`tut_lwpolyline`
    - :ref:`tut_text`
    - :ref:`tut_mtext`
    - :ref:`tut_hatch`

Saving DXF Files
----------------

Save the DXF document with a new name::

    doc.saveas("new_name.dxf")

or with the same name as loaded::

    doc.save()

.. seealso::

    Documentation for :func:`ezdxf.document.Drawing.save` and
    :func:`ezdxf.document.Drawing.saveas`, for more information about file
    management go to the :ref:`dwgmanagement` section.

Create New Blocks
-----------------

The block definitions of a DXF document are managed by the
:class:`~ezdxf.sections.blocks.BlocksSection` object::

    my_block = doc.blocks.new("MyBlock")

.. seealso::

    :ref:`tut_blocks`


Create Block References
-----------------------

A block reference is just another DXF entity called INSERT.
The :class:`~ezdxf.entities.Insert` entity is created by the factory method:
:meth:`~ezdxf.layouts.BaseLayout.add_blockref`::

    msp.add_blockref("MyBlock", (0, 0))


.. seealso::

    See :ref:`tut_blocks` for more advanced features like using
    :class:`~ezdxf.entities.Attrib` entities.


Create New Layers
-----------------

A layer is not an entity container, a layer is just another DXF attribute
stored in the entity and the entity can inherit some properties from this
:class:`~ezdxf.entities.Layer` object.
Layer objects are stored in the layer table which is available as
attribute :code:`doc.layers`.

You can create your own layers::

    my_layer = doc.layers.add("MyLayer")

The layer object also controls the visibility of entities which references this
layer, the on/off state of the layer is unfortunately stored as positive or
negative color value which make the raw DXF attribute of layers useless, to
change the color of a layer use the property :attr:`Layer.color` ::

    my_layer.color = 1

To change the state of a layer use the provided methods of the
:class:`~ezdxf.entities.Layer` object, like
:meth:`~ezdxf.entities.Layer.on`, :meth:`~ezdxf.entities.Layer.off`,
:meth:`~ezdxf.entities.Layer.freeze` or :meth:`~ezdxf.entities.Layer.thaw`::

    my_layer.off()

.. seealso::

    :ref:`layer_concept`

Delete Entities
---------------

The safest way to delete entities is to delete the entity from the layout
containing that entity::

    line = msp.add_line((0, 0), (1, 0))
    msp.delete_entity(line)

This removes the entity immediately from the layout and destroys the entity.
The property :attr:`~ezdxf.entities.DXFEntity.is_alive` returns ``False`` for a
destroyed entity and all Python attributes are deleted, so
:code:`line.dxf.color` will raise an :class:`AttributeError` exception,
because ``line`` does not have a :attr:`~ezdxf.entities.DXFEntity.dxf`
attribute anymore.

`Ezdxf` also supports manually destruction of entities by calling the method
:meth:`~ezdxf.entities.DXFEntity.destroy`::

    line.destroy()

Manually destroyed entities are not removed immediately from entities containers
like :class:`Modelspace` or :class:`EntityQuery`, but iterating such a container
will filter destroyed entities automatically, so a :code:`for e in msp: ...` loop
will never yield destroyed entities. The index operator and the :func:`len`
function do **not** filter deleted entities, to avoid getting deleted entities
call the :func:`purge` method of the container manually to remove deleted
entities.

Further Information
-------------------

- :ref:`reference`

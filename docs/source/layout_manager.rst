.. _layout_manager:

Layout Manager
==============

The layout manager is unique to each DXF drawing, access the layout manager by :attr:`Drawing.layouts`.

.. class:: Layouts

    The :class:`Layouts` class manages paper space layouts and the model space.

.. method:: Layouts.__len__()

    Return the count for layouts.

.. method:: Layouts.__contains__(name)

    Support for the :code:`in` operator

    :param str name: layout name as shown in tab

.. method:: Layouts.__iter__()

    Iterate over model space layout and all paper space layouts as :class:`Layout` objects.

.. method:: Layouts.modelspace()

    Returns the model space layout as :class:`Layout` object.

.. method:: Layouts.names()

    Returns iterable of all layout names.

.. method:: Layouts.get(name)

    Returns layout *name* as :class:`Layout` object.

    :param str name: layout name as shown in tab

.. method:: Layouts.rename(old_name, new_name)

    Rename a layout. Layout *Model* can not renamed and the new name of a layout must not exist.

    :param str old_name: actual layout name
    :param str new_name: new layout name

.. method:: Layouts.names_in_taborder()

    Returns all layout names in tab order as a list of strings.

.. method:: Layouts.new(name, dxfattribs=None)

    Create a new :class:`Layout`.

    :param str name: layout name as shown in tab

.. method:: Layouts.delete(name)

    Delete layout and all entities in this layout.

    :param str name: layout name as shown in tab

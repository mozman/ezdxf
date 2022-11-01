.. _paperspace_concept:

Paperspace
==========

A paperspace layout is where the modelspace drawing content is assembled and
organized for 2D output, such as printing on a sheet of paper, or as a digital
document, such as a PDF file.

Each DXF document can have one or more paperspace layouts but the DXF version R12
supports only one paperspace layout and it is not recommended to rely on
paperspace layouts in DXF version R12.

Graphical entities can be added to the paperspace by factory
methods: :ref:`thematic_factory_method_index`. Views or "windows" to the
modelspace are added as :class:`~ezdxf.entities.Viewport` entities, each
viewport displays a region of the modelspace and can have an individual scaling
factor, rotation angle, clipping path, view direction or overridden layer attributes.

.. seealso::

    - Reference of class :class:`~ezdxf.layouts.Paperspace`
    - :ref:`thematic_factory_method_index`
    - Example for usage of paperspace viewports: `viewports_in_paperspace.py`_

.. _`viewports_in_paperspace.py`: https://github.com/mozman/ezdxf/blob/master/examples/viewports_in_paperspace.py

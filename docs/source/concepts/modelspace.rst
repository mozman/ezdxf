.. _modelspace_concept:

Modelspace
==========

The modelspace contains the "real" world representation of the drawing subjects
in real world units and is displayed in the tab called "Model" in CAD
applications. The modelspace is always present and can't be deleted.

The modelspace object is acquired by the method :meth:`~ezdxf.document.Drawing.modelspace`
of the :class:`~ezdxf.document.Drawing` class and new entities
should be added to the modelspace by factory methods: :ref:`thematic_factory_method_index`.

This is a common idiom for creating a new document and acquiring the modelspace::

    import ezdxf

    doc = ezdxf.new()
    msp = doc.modelspace()

The modelspace can have one or more rectangular areas called modelspace
viewports. The modelspace viewports can be used for displaying different views
of the modelspace from different locations of the modelspace or viewing
directions. It is important to know that modelspace viewports (:class:`~ezdxf.entities.VPort`)
are not the same as paperspace viewport entities (:class:`~ezdxf.entities.Viewport`).


.. seealso::

    - Reference of class :class:`~ezdxf.layouts.Modelspace`
    - :ref:`thematic_factory_method_index`
    - Example for usage of modelspace viewports: `tiled_window_setup.py`_

.. _tiled_window_setup.py: https://github.com/mozman/ezdxf/blob/master/examples/tiled_window_setup.py
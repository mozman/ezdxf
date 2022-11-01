.. _modelspace_concept:

Modelspace
==========

The modelspace contains the "real" world representation of the drawing subjects
in real world units and is displayed in the tab called "Model" in CAD
applications. The modelspace is always present and can't be deleted.

The modelspace object is acquired by the method :meth:`~ezdxf.document.Drawing.modelspace`
of the :class:`~ezdxf.document.Drawing` class and new entities
should be added to the modelspace by factory methods: :ref:`thematic_factory_method_index`.

This is a common idiom to create new document and acquiring the modelspace::

    import ezdxf

    doc = ezdxf.new()
    msp = doc.modelspace()


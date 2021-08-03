Layout Factory Methods
----------------------

Recommended way to create DXF entities.

For all supported entities exist at least one factory method in the
:class:`ezdxf.layouts.BaseLayout` class.
All factory methods have the prefix: ``add_...``

.. code-block:: Python

    import ezdxf

    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_line((0, 0, 0), (3, 0, 0), dxfattribs={"color": 2})

.. seealso::

    Methods of the :class:`~ezdxf.layouts.BaseLayout` class.

Factory Functions
-----------------

Alternative way to create DXF entities for advanced `ezdxf` users.

The :mod:`ezdxf.entities.factory` module provides the
:func:`~ezdxf.entities.factory.new` function to create new DXF entities by
their DXF name and a dictionary of DXF attributes. This will bypass the
validity checks in the factory methods of the :class:`~ezdxf.layouts.BaseLayout`
class.

This new created entities are virtual entities which are not assigned to any
DXF document nor to any layout. Add the entity to a layout (and document) by
the layout method :meth:`~ezdxf.layouts.BaseLayout.add_entity`.

.. code-block:: Python

    import ezdxf
    from ezdxf.entities import factory

    doc = ezdxf.new()
    msp = doc.modelspace()
    line = factory.new(
        "LINE",
        dxfattribs={
            "start": (0, 0, 0),
            "end": (3, 0, 0),
            "color": 2,
        },
    )
    msp.add_entity(line)

Direct Object Instantiation
---------------------------

For advanced developers with knowledge about the internal design of `ezdxf`.

Import the entity classes from sub-package :mod:`ezdxf.entities` and instantiate
them. This will bypass the validity checks in the factory methods of the
:class:`~ezdxf.layouts.BaseLayout` class and maybe additional required setup
procedures for some entities - **study the source code!**.

.. warning::

    A refactoring of the internal `ezdxf` structures will break your code.

This new created entities are virtual entities which are not assigned to any
DXF document nor to any layout. Add the entity to a layout (and document) by
the layout method :meth:`~ezdxf.layouts.BaseLayout.add_entity`.

.. code-block:: Python

    import ezdxf
    from ezdxf.entities import Line

    doc = ezdxf.new()
    msp = doc.modelspace()
    line = Line.new(
        dxfattribs={
            "start": (0, 0, 0),
            "end": (3, 0, 0),
            "color": 2,
        }
    )
    msp.add_entity(line)

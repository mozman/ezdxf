Reorder
=======

.. module:: ezdxf.reorder

Tools to reorder DXF entities by handle or a special sort handle mapping.

Such reorder mappings are stored only in layouts as :class:`~ezdxf.layouts.Modelspace`,
:class:`~ezdxf.layouts.Paperspace` or :class:`~ezdxf.layouts.BlockLayout`,
and can be retrieved by the method :meth:`~ezdxf.layouts.Layout.get_redraw_order`.

Each entry in the handle mapping replaces the actual entity handle, where the
"0" handle has a special meaning, this handle always shows up at last in
ascending ordering.

.. autofunction:: ascending

.. autofunction:: descending


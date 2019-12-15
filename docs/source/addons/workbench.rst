.. module:: ezdxf.addons.workbench
    :noindex:

Workbench
=========

.. automodule:: ezdxf.addons.workbench

.. autofunction:: offset_vertices_2d

.. code-block:: Python

    source = [(0, 0), (3, 0), (3, 3), (0, 3)]
    result = list(offset_vertices(source, offset=0.5, closed=True))

.. image:: offset_vertices_2d_1.png
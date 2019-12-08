.. _linetypes:

Linetypes
=========

The :attr:`~ezdxf.entities.DXFGraphic.dxf.linetype` defines the pattern of a line. The linetype of an entity
can be specified by the DXF attribute :attr:`linetype`, this can be an explicit named linetype or the entity
can inherit its line type from the assigned layer by setting :attr:`linetype` to ``'BYLAYER'``,
which is also the default value. CONTINUOUS is the default line type for layers with
unspecified line type.

`ezdxf` creates several standard linetypes, if the argument `setup` is ``True`` at calling :func:`~ezdxf.new`,
this simple line types are supported by all DXF versions:

.. code-block:: Python

    doc = ezdxf.new('R2007', setup=True)

.. image:: all_std_line_types.png

In DXF R13 Autodesk introduced complex linetypes, containing TEXT or SHAPES in linetypes. `ezdxf` v0.8.4 and later
supports complex linetypes.

.. seealso::

    :ref:`tut_linetypes`

Linetype Scaling
-----------------

Global linetype scaling can be changed by setting the header variable :code:`doc.header['$LTSCALE'] = 2`,
which stretches the line pattern by factor 2.

To change the linetype scaling for single entities set scaling factor by DXF attribute
:attr:`~ezdxf.entities.DXFGraphic.dxf.ltscale`, which is supported since DXF version R2000.
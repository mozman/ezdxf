.. _get_entity_type:

Get DXF Entity Type
===================

The :meth:`~ezdxf.entities.DXFEntity.dxftype` method returns the entity type as defined 
by the DXF reference as an uppercase string.

.. code-block:: Python

    e = msp.add_line((0, 0), (1, 0))
    assert e.dxftype() == "LINE"

.. seealso::

    - `DXF Reference`_ for DXF R2018

.. _DXF Reference: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3
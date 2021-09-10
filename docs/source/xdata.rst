
.. module:: ezdxf.entities.xdata

XDATA
=====

XDATA is a DXF tags structure to store arbitrary data in DXF entities.

.. warning::

    Low level usage of XDATA is an advanced feature, it is the responsibility
    of the programmer to create valid XDATA structures. Any errors can
    invalidate the DXF file!

.. seealso::

    Internals about :ref:`xdata_internals`

.. class:: XData

    .. automethod:: __contains__

    .. automethod:: add

    .. automethod:: get

    .. automethod:: discard

    .. automethod:: has_xlist

    .. automethod:: get_xlist

    .. automethod:: set_xlist

    .. automethod:: discard_xlist

    .. automethod:: replace_xlist
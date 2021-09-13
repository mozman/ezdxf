XData
=====

.. module:: ezdxf.entities.xdata

.. class:: XData

    Internal management class for XDATA.

    .. seealso::

        - XDATA reference: :ref:`extended_data`
        - Wrapper class to store a list in XDATA: :class:`XDataUserList`
        - Wrapper class to store a dict in XDATA: :class:`XDataUserDict`
        - Tutorial: :ref:`tut_custom_data`
        - `DXF R2018 Reference <https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A2A628B0-3699-4740-A215-C560E7242F63>`_

    .. automethod:: __contains__

    .. automethod:: add

    .. automethod:: get

    .. automethod:: discard

    .. automethod:: has_xlist

    .. automethod:: get_xlist

    .. automethod:: set_xlist

    .. automethod:: discard_xlist

    .. automethod:: replace_xlist
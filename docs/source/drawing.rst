Drawing Object
==============

.. class:: Drawing

    The :class:`Drawing` class manages all entities and tables related to a
    DXF drawing. Every drawing has its own character :attr:`~Drawing.encoding`
    which is only important for saving to disk.

Drawing Attributes
------------------

.. attribute:: Drawing.dxfversion

    contains the DXF version as string like ``'AC1009'``, set by the
    :func:`new` or the :func:`readfile` function. (read only)

.. attribute:: Drawing.encoding

    DXF drawing text encoding, the default encoding for new drawings is
    ``'cp1252'``. (read/write)

    ============ =================
    supported    encodings
    ============ =================
    ``'cp874'``  Thai
    ``'cp932'``  Japanese
    ``'hz'``     SimpChinese
    ``'cp949'``  Korean
    ``'cp950'``  TradChinese
    ``'cp1250'`` CentralEurope
    ``'cp1251'`` Cyrillic
    ``'cp1252'`` WesternEurope
    ``'cp1253'`` Greek
    ``'cp1254'`` Turkish
    ``'cp1255'`` Hebrew
    ``'cp1256'`` Arabic
    ``'cp1257'`` Baltic
    ``'cp1258'`` Vietnam
    ============ =================

.. attribute:: Drawing.filename

    Contains the drawing filename, if the drawing was opend with the
    :func:`readfile` function else set to `None`. (read/write)

.. attribute:: Drawing.dxffactory

    DXF entity creation factory, see also :class:`DXFFactory` (read only).

.. attribute:: Drawing.header

    Reference to the :class:`HeaderSection` of the drawing, where
    you can change the drawing settings.

.. attribute:: Drawing.layers

    Reference to the layers table, where you can create, get and
    remove layers, see also :class:`Table` and :class:`Layer`

.. attribute:: Drawing.styles

    Reference to the styles table, see also :class:`Style`.

.. attribute:: Drawing.linetypes

    Reference to the linetypes table, see also :class:`Linetype`.

.. attribute:: Drawing.views

    Reference to the views table, see also :class:`View`.

.. attribute:: Drawing.viewports

    Reference to the viewports table, see also :class:`Viewport`.

.. attribute:: Drawing.dimstyles

    Reference to the dimstyles table, see also :class:`DimStyle`.

.. attribute:: Drawing.blocks

.. attribute:: Drawing.modelspace

Drawing Methods
---------------

.. method:: Drawing.save()

    Write drawing to file-system by using the :attr:`~Drawing.filename` attribute
    as filename.

.. method:: Drawing.saveas(filename)

    Write drawing to file-system by setting the :attr:`~Drawing.filename`
    attribute to `filename`.

.. method:: Drawing.write(stream)

    Write drawing to a text stream, opened with `encoding` = :attr:`Drawing.encoding`
    and and `mode` = ``'wt'``.

.. method:: Drawing.writebytes(stream)

    not implemented yet.
.. _DXF Unicode Decoder:

DXF Unicode Decoder
===================

The DXF format uses a special form of unicode encoding: "\\U+xxxx".

To avoid a speed penalty such encoded characters are not decoded
automatically by the regular loading function:func:`ezdxf.readfile`,
only the :mod:`~ezdxf.recover` module does the decoding
automatically, because this loading mode is already slow.

This kind of encoding is most likely used only in older DXF versions, because
since DXF R2007 the whole DXF file is encoded in ``utf8`` and a special unicode
encoding is not necessary.

The :func:`ezdxf.has_dxf_unicode` and :func:`ezdxf.decode_dxf_unicode` are
new support functions to decode unicode characters "\\U+xxxx" manually.

.. autofunction:: ezdxf.has_dxf_unicode

.. autofunction:: ezdxf.decode_dxf_unicode

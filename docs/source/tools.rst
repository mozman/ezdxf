Tools
=====

.. _DXF Unicode Decoder:

DXF Unicode Decoder
-------------------

The DXF format uses a special form of unicode encoding: "\\U+xxxx".

To avoid a big speed penalty such encoded characters are not decoded
automatically by the regular loading functions like :func:`ezdxf.readfile` or
:func:`ezdxf.read`, only the :mod:`~ezdxf.recover` module does the decoding
automatically, because this loading mode is already slow.

This kind of encoding is used most likely in older DXF versions, because since
DXF R2007 the DXF files is encoded in ``utf8`` and a  special unicode encoding
is not necessary.

.. versionadded:: 0.14

.. autofunction:: ezdxf.has_dxf_unicode

.. autofunction:: ezdxf.decode_dxf_unicode

Tools
-----

Some handy tool functions used internally by ``ezdxf``.

.. autofunction:: ezdxf.int2rgb

.. autofunction:: ezdxf.rgb2int

.. autofunction:: ezdxf.float2transparency

.. autofunction:: ezdxf.transparency2float

.. autofunction:: ezdxf.tools.juliandate

.. autofunction:: ezdxf.tools.calendardate

.. autofunction:: ezdxf.tools.set_flag_state

.. autofunction:: ezdxf.tools.guid

.. autofunction:: ezdxf.tools.bytes_to_hexstr

.. autofunction:: ezdxf.tools.suppress_zeros


.. autofunction:: ezdxf.tools.aci2rgb

.. autofunction:: ezdxf.tools.normalize_text_angle

SAT Format "Encryption"
-----------------------

.. autofunction:: ezdxf.tools.crypt.encode

.. autofunction:: ezdxf.tools.crypt.decode

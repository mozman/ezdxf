Colors Module
=============

.. module:: ezdxf.colors

This module provides functions and constants to manage all kinds of colors in
DXF documents.

Converter Functions
===================

.. autofunction:: rgb2int

.. autofunction:: int2rgb

.. autofunction:: aci2rgb

.. autofunction:: luminance

.. autofunction:: decode_raw_color

.. autofunction:: decode_raw_color_int

.. autofunction:: encode_raw_color

.. autofunction:: transparency2float

.. autofunction:: float2transparency

RGB Class
=========

.. autoclass:: RGB

    .. autoproperty:: luminance

    .. automethod:: to_hex

    .. automethod:: from_hex

    .. automethod:: to_floats

    .. automethod:: from_floats

RGBA Class
==========

.. autoclass:: RGBA

    .. autoproperty:: luminance

    .. automethod:: to_hex

    .. automethod:: from_hex

    .. automethod:: to_floats

    .. automethod:: from_floats

ACI Color Values
================

Common :ref:`ACI` values, also accessible as IntEnum :class:`ezdxf.enums.ACI`

=========================== ===
BYBLOCK                     0
BYLAYER                     256
BYOBJECT                    257
RED                         1
YELLOW                      2
GREEN                       3
CYAN                        4
BLUE                        5
MAGENTA                     6
BLACK (on light background) 7
WHITE (on dark background)  7
GRAY                        8
LIGHT_GRAY                  9
=========================== ===

Default Palettes
================

Default color mappings from :ref:`ACI` to :term:`true-color` values.

=========== =============================
model space DXF_DEFAULT_COLORS
paper space DXF_DEFAULT_PAPERSPACE_COLORS
=========== =============================

Raw Color Types
===============

======================= ====
COLOR_TYPE_BY_LAYER     0xC0
COLOR_TYPE_BY_BLOCK     0xC1
COLOR_TYPE_RGB          0xC2
COLOR_TYPE_ACI          0xC3
COLOR_TYPE_WINDOW_BG    0xC8
======================= ====

Raw Color Vales
===============

=================== ============
BY_LAYER_RAW_VALUE  -1073741824
BY_BLOCK_RAW_VALUE  -1056964608
WINDOW_BG_RAW_VALUE -939524096
=================== ============

Transparency Values
===================

======================= =========
OPAQUE                  0x20000FF
TRANSPARENCY_10         0x20000E5
TRANSPARENCY_20         0x20000CC
TRANSPARENCY_30         0x20000B2
TRANSPARENCY_40         0x2000099
TRANSPARENCY_50         0x200007F
TRANSPARENCY_60         0x2000066
TRANSPARENCY_70         0x200004C
TRANSPARENCY_80         0x2000032
TRANSPARENCY_90         0x2000019
TRANSPARENCY_BYBLOCK    0x1000000
======================= =========
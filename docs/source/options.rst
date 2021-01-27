Global Options
--------------

.. module:: ezdxf.options

Global options stored in :mod:`ezdxf.options`

.. attribute:: default_text_style

    Default text styles, default value is ``OpenSans``.

.. attribute:: default_dimension_text_style

    Default text style for Dimensions, default value is ``OpenSansCondensed-Light``.

.. attribute:: use_matplotlib_font_support

    Active the matplotlib font support to calculate font metrics:
    This requires a working matplotlib installation else an ``ImportError``
    exception will be raised sooner or later.
    Default is ``False``

.. attribute:: load_system_font

    Load also system fonts if matplotlib font support is activated.
    This process can take a while. Default is ``False``

.. attribute:: filter_invalid_xdata_group_codes

    Check for invalid XDATA group codes, default value is ``False``

.. attribute:: log_unprocessed_tags

    Log unprocessed DXF tags for debugging, default value is ``True``

.. attribute:: load_proxy_graphics

    Load proxy graphics if ``True``, default is ``False``.

.. attribute:: store_proxy_graphics

    Export proxy graphics if ``True``, default is ``False``.

.. attribute:: write_fixed_meta_data_for_testing

    Enable this option to always create same meta data for testing scenarios,
    e.g. to use a diff like tool to compare DXF documents.

.. method:: preserve_proxy_graphics()

    Enable proxy graphic load/store support.

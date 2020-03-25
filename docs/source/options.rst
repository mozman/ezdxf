Global Options
--------------

.. module:: ezdxf.options

Global options stored in :mod:`ezdxf.options`

.. attribute:: default_text_style

    Default text styles, default value is ``OpenSans``.

.. attribute:: default_dimension_text_style

    Default text style for Dimensions, default value is ``OpenSansCondensed-Light``.

.. attribute:: check_entity_tag_structures

    Check app data (:ref:`app_data_internals`) and XDATA (:ref:`xdata_internals`) tag structures, set this option to
    ``False`` for a little performance boost, default value is ``True``.

.. attribute:: filter_invalid_xdata_group_codes

    Check for invalid XDATA group codes, default value is ``False``

.. attribute:: log_unprocessed_tags

    Log unprocessed DXF tags for debugging, default value is ``True``

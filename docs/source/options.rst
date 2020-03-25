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

.. attribute:: fix_invalid_located_group_tags

    Try to fix invalid located group tags, default value is ``False``

    Moves AcDbEntity group tags into correct subclass if necessary, try this option if you miss DXF entity
    attributes like `layer` or `color` after reading DXF files created by other applications. This is not necessary for
    DXF files created by established CAD applications like AutoCAD or BricsCAD.

.. attribute:: log_unprocessed_tags

    Log unprocessed DXF tags for debugging, default value is ``True``

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

.. attribute:: load_system_fonts

    Load also system fonts if matplotlib font support is activated.
    This may take a while and does not improve the calculations, if the
    used fonts are already included in the ``fonts.json`` file.
    Set this option use only, if this makes a real difference on your system.
    Default is ``False``.

    The ``fonts.json`` file is extendable see next option:
    :attr:`path_to_fonts_json`

.. attribute:: path_to_fonts_json

    Set path to an external stored ``fonts.json`` file: e.g. ``"~/.ezdxf"`` do
    not include ``fonts.json``.

    Example how to create your own ``fonts.json`` file in ``"~/.ezdxf"``, this
    has to be done only once or if you want to update this file:

    .. code-block:: Python

        from pathlib import Path
        from ezdxf.addons.drawing import fonts

        fonts.load()  # load the ezdxf default file
        fonts.add_system_fonts()
        p = Path("~/.ezdxf").expanduser()
        p.mkdir(exist_ok=True)
        fonts.save(p)  # create your fonts.json

    In your main_script.py:

    .. code-block:: Python

        from ezdxf import options

        option.use_matplotlib_font_support = True
        option.path_to_fonts_json = "~/.ezdxf"

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

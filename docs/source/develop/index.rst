.. _Developer Guides:

Developer Guides
================

Information about `ezdxf` internals.

Source Code Formatting
----------------------

Reformat code by `Black`_ for a column width of 80::

    C:\> black -l 80 <python-file>

Reformatting the `ezdxf` code base is an ongoing process, add
reformatted code in a separate commit without changing the runtime logic.

Type Annotations
----------------

The use of type annotations is encouraged. New modules should pass `mypy`_
without errors in non-strict mode. Using ``# type: ignore`` is fine in tricky
situations - type annotations should be helpful in understanding the code
and not be a burden.

The following global options are required to pass `mypy`_ without error
messages:

.. code-block:: ini

    [mypy]
    python_version = 3.7
    ignore_missing_imports = True

Read `this <https://mypy.readthedocs.io/en/stable/config_file.html>`_ to learn
where `mypy`_ searches for config files.

Use the `mypy`_ command line option ``--ignore-missing-imports`` and ``-p`` to
check the whole package from any location in the file system:

.. code-block:: Powershell

    PS D:\Source\ezdxf.git> mypy --ignore-missing-imports -p ezdxf
    Success: no issues found in 255 source files

Design
------

The :ref:`pkg-design` section shows the structure of the `ezdxf` package for
developers with more experience, which want to have more insight into the
package an maybe want to develop add-ons or want contribute to the `ezdxf`
package.

.. toctree::
    :maxdepth: 2

    pkg-design


Internal Data Structures
------------------------

.. toctree::
    :maxdepth: 2

    entitydb
    dxftags
    dxftag_collections
    xdata

Documentation Guide
-------------------

.. toctree::
    :maxdepth: 1

    doc_formatting_guide

.. _Black: https://pypi.org/project/black/
.. _mypy: https://pypi.org/project/mypy/
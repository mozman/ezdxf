.. _recover:

.. module:: ezdxf.recover

Recover
=======

.. versionadded:: v0.14

This module provides function to "recover" ASCII DXF documents with structural
flaws, which prevents the regular :func:`ezdxf.read` and :func:`ezdxf.readfile`
functions to load the document.

The :func:`read` and :func:`readfile` functions will repair as much
flaws as possible and run the required audit process automatically
afterwards and return the result of this audit process:

.. code-block:: Python

    from ezdxf import recover

    doc, auditor = recover.readfile("messy.dxf")
    if auditor.has_errors:
        auditor.print_error_report()


This efforts cost some time, loading the DXF document with :func:`ezdxf.read` or
:func:`ezdxf.readfile` will be faster.

.. warning::

    This module will load DXF files which have decoding errors, most likely binary
    data stored in XRECORD entities, these errors are logged as unrecoverable
    ``AuditError.DECODE_ERRORS`` in the :attr:`Auditor.errors` attribute, but no
    :class:`DXFStructureError` exception will be raised, because for many use
    cases this errors can be ignored.

    Despite this are valid DXF files, writing such files back with `ezdxf`
    may create **invalid** DXF files, or at least some **information will be lost**
    - handle with care!

Some loading scenarios as examples:
-----------------------------------

1. It will work
~~~~~~~~~~~~~~~

Mostly DXF files from AutoCAD or BricsCAD (e.g. for In-house solutions)

.. code-block:: Python

    try:
        doc = ezdxf.readfile(name)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {name}.')

2. Try Hard
~~~~~~~~~~~

From trusted and untrusted sources but with good hopes, the worst case works
like a cache miss, you pay for the first try and pay the extra fee for the
recover mode:

.. code-block:: Python

    try:  # fast path:
        doc = ezdxf.readfile(name)
    except ezdxf.DXFStructureError:
        try:  # slow path with low level structure repair:
            doc, auditor = recover.readfile(name)
            if auditor.has_errors:
                print(f'Found unrecoverable errors in DXF file: {name}.')
                auditor.print_error_report()
        except ezdxf.DXFStructureError:
            print(f'Invalid or corrupted DXF file: {name}.')

3. Just pay the extra fee
~~~~~~~~~~~~~~~~~~~~~~~~~

Untrusted sources and expecting many invalid DXF files, you always pay an
extra fee for the recover mode:

.. code-block:: Python

    try:  # low level structure repair:
        doc, auditor = recover.readfile(name)
        if auditor.has_errors:
            print(f'Found unrecoverable errors in DXF file: {name}.')
            auditor.print_error_report()
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {name}.')


.. hint::

    This functions can handle only ASCII DXF files!

.. autofunction:: readfile

.. autofunction:: read




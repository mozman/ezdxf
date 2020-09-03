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

    import sys
    import ezdxf
    from ezdxf import recover

    try:
        doc, auditor = recover.readfile("messy.dxf")
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted Not a DXF file.')
        sys.exit(2)

    # DXF file can still have unrecoverable errors, but this is maybe just
    # a problem when saving the recovered DXF file.
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
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {name}.')
        sys.exit(2)

2. DXF file with minor flaws
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DXF files has only minor flaws, like undefined resources.

.. code-block:: Python

    try:
        doc = ezdxf.readfile(name)
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {name}.')
        sys.exit(2)

    auditor = doc.audit()
    if auditor.has_errors:
        auditor.print_error_report()



3. Try Hard
~~~~~~~~~~~

From trusted and untrusted sources but with good hopes, the worst case works
like a cache miss, you pay for the first try and pay the extra fee for the
recover mode:

.. code-block:: Python

    try:  # Fast path:
        doc = ezdxf.readfile(name)
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    # Catch all DXF errors:
    except ezdxf.DXFError:
        try:  # Slow path with low level structure repair:
            doc, auditor = recover.readfile(name)
        except ezdxf.DXFStructureError:
            print(f'Invalid or corrupted DXF file: {name}.')
            sys.exit(2)

    # DXF file can still have unrecoverable errors, but this is maybe
    # just a problem when saving the recovered DXF file.
    if auditor.has_errors:
        print(f'Found unrecoverable errors in DXF file: {name}.')
        auditor.print_error_report()

4. Just use the slow recover module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Untrusted sources and expecting many invalid or corrupted  DXF files, you
always pay an extra fee for the recover mode:

.. code-block:: Python

    try:  # low level structure repair:
        doc, auditor = recover.readfile(name)
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {name}.')
        sys.exit(2)

    # DXF file can still have unrecoverable errors, but this is maybe
    # just a problem when saving the recovered DXF file.
    if auditor.has_errors:
        print(f'Found unrecoverable errors in DXF file: {name}.')
        auditor.print_error_report()

.. hint::

    This functions can handle only ASCII DXF files!

.. autofunction:: readfile

.. autofunction:: read




.. _recover:

.. module:: ezdxf.recover

Recover
=======

.. versionadded:: v0.14

This module provides functions to "recover" ASCII DXF documents with structural
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

    Writing such files back with `ezdxf` may create **invalid** DXF files, or
    at least some **information will be lost** - handle with care!

    To avoid this problem use :code:`recover.readfile(filename, errors='strict')`
    which raises an :class:`UnicodeDecodeError` exception for such binary data.
    Catch the exception and handle this DXF files as unrecoverable.

Loading Scenarios
-----------------

1. It will work
~~~~~~~~~~~~~~~

Mostly DXF files from AutoCAD or BricsCAD (e.g. for In-house solutions):

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

DXF files have only minor flaws, like undefined resources:

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
        try:  # Slow path including fixing low level structures:
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

    try:  # Slow path including fixing low level structures:
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

5. Unrecoverable Decoding Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If files contain binary data which can not be decoded by the document encoding,
it is maybe the best to ignore this files, this works in normal and recover
mode:

.. code-block:: Python

    try:
        doc, auditor = recover.readfile(name, errors='strict')
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {name}.')
        sys.exit(2)
    except UnicodeDecodeError:
        print(f'Decoding error in DXF file: {name}.')
        sys.exit(3)

6. Ignore/Locate Decoding Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes ignoring decoding errors can recover DXF files or at least
you can detect where the decoding errors occur:

.. code-block:: Python

    try:
        doc, auditor = recover.readfile(name, errors='ignore')
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file: {name}.')
        sys.exit(2)
    if auditor.has_errors:
        auditor.print_report()

The error messages with code :attr:`AuditError.DECODING_ERROR` shows the
approximate line number of the decoding error:
"Fixed unicode decoding error near line: xxx."



.. hint::

    This functions can handle only ASCII DXF files!

.. autofunction:: readfile

.. autofunction:: read




.. _recover:

.. module:: ezdxf.recover

Recover
=======

This module provides function to "recover" ASCII DXF documents with structural
flaws, which prevents the regular :func:`ezdxf.read` and :func:`ezdxf.readfile`
functions to load the document.

This function will repair as much flaws as possible to take the document
to a state, where the :class:`~ezdxf.audit.Auditor` could start his journey
to repair further issues, but the audit process has to be started manually::

    doc = ezdxf.recover.readfile("messy.dxf")
    auditor = doc.audit()
    if auditor.has_errors:
        auditor.print_error_report()


This efforts cost some time, loading the DXF document with :func:`ezdxf.read` or
:func:`ezdxf.readfile` will be faster.

.. versionadded:: v0.14

.. hint::

    This functions can handle only ASCII DXF files!

.. autofunction:: read

.. autofunction:: readfile



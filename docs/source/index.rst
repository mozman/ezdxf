.. ezdxf documentation master file, created by
   sphinx-quickstart on Tue Mar 15 06:49:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: gfx/ezdxf-logo-light-bg.svg
   :align: center
   :width: 400px

Welcome! This is the documentation for ezdxf release |release|, last updated |today|.

.. note::

   **Python 2** support REMOVED, *ezdxf* >= v0.9 requires at least **Python 3.5**


Quick-Info
==========

- *ezdxf* is a Python package to create new DXF files and read/modify/write existing DXF files
- the intended audience are developers
- requires at least Python 3.5
- OS independent
- additional required packages: `pyparsing <https://pypi.python.org/pypi/pyparsing/>`_
- MIT-License
- read/write/new support for DXF versions: R12, R2000, R2004, R2007, R2010, R2013 and R2018
- additional read support for DXF versions R13/R14 (upgraded to R2000)
- additional read support for older DXF versions than R12 (upgraded to R12)
- preserves third-party DXF content
- additional :ref:`r12writer`, that creates just an ENTITIES section with support for the basic DXF entities
- source code generator as add-on to generate Python code from DXF structures as starting point for parametric
  DXF entity creation from existing DXF files.

Website
-------

https://ezdxf.mozman.at/

Documentation
-------------

Documentation of development version at https://ezdxf.mozman.at/docs

Documentation of latest release at http://ezdxf.readthedocs.io/

Source Code: http://github.com/mozman/ezdxf.git

Issue Tracker at GitHub: http://github.com/mozman/ezdxf/issues

Questions and Feedback at Google Groups
---------------------------------------

Please post questions at the `forum <https://groups.google.com/d/forum/python-ezdxf>`_ or
`stack overflow <https://stackoverflow.com/>`_ to make answers available to other users as well.


Contents
========

.. toctree::
   :maxdepth: 2

   introduction
   tutorials/index
   concepts/index
   reference
   render/index
   addons/index
   howto
   dxfinternals/index
   develop/index
   glossary

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`


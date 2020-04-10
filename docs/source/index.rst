.. ezdxf documentation master file, created by
   sphinx-quickstart on Tue Mar 15 06:49:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: gfx/ezdxf-logo-light-bg.svg
   :align: center
   :width: 400px

Welcome! This is the documentation for ezdxf release |release|, last updated |today|.

Quick-Info
==========

- *ezdxf* is a Python package to create new DXF files and read/modify/write existing DXF files
- the intended audience are developers
- requires at least Python 3.6
- OS independent
- additional required packages: `pyparsing <https://pypi.python.org/pypi/pyparsing/>`_
- MIT-License
- read/write/new support for DXF versions: R12, R2000, R2004, R2007, R2010, R2013 and R2018
- additional read support for DXF versions R13/R14 (upgraded to R2000)
- additional read support for older DXF versions than R12 (upgraded to R12)
- read/write support for ASCII DXF and Binary DXF
- preserves third-party DXF content

Included Extensions
-------------------

- :ref:`r12writer` add-on to write basic DXF entities direct and fast into a DXF R12 file or stream
- :ref:`iterdxf` add-on to iterate over entities of the modelspace of really big (> 5GB) DXF files which
  do not fit into memory
- :ref:`importer` add-on to import entities, blocks and table entries from another DXF document
- :ref:`dxf2code` add-on to generate Python code for DXF structures loaded from DXF
  documents as starting point for parametric DXF entity creation
- :ref:`plot_style_files` read/write add-on
- :ref:`pycsg2` add-on for Constructive Solid Geometry (CSG) modeling technique

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
   howto/index
   faq
   render/index
   addons/index
   dxfinternals/index
   develop/index
   glossary

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`


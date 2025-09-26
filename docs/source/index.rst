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

- *ezdxf* is a Python package to create new DXF documents and read/modify/write
  existing DXF documents
- MIT-License
- the intended audience are programmers
- requires at least Python 3.10
- OS independent
- tested with CPython and pypy3
- has type annotations and passes ``mypy --ignore-missing-imports -p ezdxf`` successful
- additional required packages for the core package without add-ons:
  `typing_extensions <https://pypi.org/project/typing-extensions/>`_,
  `pyparsing <https://pypi.org/project/pyparsing/>`_,
  `numpy <https://pypi.org/project/numpy/>`_,
  `fontTools <https://pypi.org/project/fonttools>`_
- read/write/new support for DXF versions: R12, R2000, R2004, R2007, R2010, R2013 and R2018
- additional read-only support for DXF versions R13/R14 (upgraded to R2000)
- additional read-only support for older DXF versions than R12 (upgraded to R12)
- read/write support for ASCII DXF and Binary DXF
- retains third-party DXF content
- optional C-extensions for CPython are included in the binary wheels, available
  on `PyPI <https://pypi.org/project/ezdxf/>`_ for Windows, Linux and macOS

Included Extensions
-------------------

Additional packages required for these add-ons are not automatically installed
during the *basic* setup, for more information about the setup & dependencies
visit the `documentation <https://ezdxf.mozman.at/docs/setup.html>`_.


- :mod:`~ezdxf.addons.drawing` add-on to visualise and convert DXF files to
  images which can be saved as PNG, PDF or SVG files
- :mod:`~ezdxf.addons.r12writer` add-on to write basic DXF entities direct and
  fast into a DXF R12 file or stream
- :mod:`~ezdxf.addons.iterdxf` add-on to iterate over DXF entities from the
  modelspace of huge DXF files (> 5GB) which do not fit into memory
- :mod:`~ezdxf.addons.importer` add-on to import entities, blocks and table
  entries from another DXF document
- :mod:`~ezdxf.addons.dxf2code` add-on to generate Python code for DXF structures
  loaded from DXF documents as starting point for parametric DXF entity creation
- :mod:`~ezdxf.addons.acadctb` add-on to read/write :ref:`plot_style_files`
- :mod:`~ezdxf.addons.pycsg` add-on for Constructive Solid Geometry (CSG)
  modeling technique
- :class:`~ezdxf.addons.MTextExplode` add-on for exploding MTEXT entities into
  single-line TEXT entities
- :mod:`~ezdxf.addons.text2path` add-on to convert text into outline paths
- :mod:`~ezdxf.addons.geo` add-on to support the `__geo_interface__ <https://gist.github.com/sgillies/2217756>`_
- :mod:`~ezdxf.addons.meshex` add-on for exchanging meshes with other tools as
  STL, OFF or OBJ files
- :mod:`~ezdxf.addons.openscad`  add-on, an interface to `OpenSCAD <https://openscad.org>`_
- :mod:`~ezdxf.addons.odafc` add-on, an interface to the `ODA File Converter <https://www.opendesign.com/guestfiles/oda_file_converter>`_
  to read and write DWG files
- :mod:`~ezdxf.addons.hpgl2` add-on for converting `HPGL/2 <https://en.wikipedia.org/wiki/HP-GL>`_
  plot files to DXF, SVG and PDF

Website
-------

https://ezdxf.mozman.at/

Documentation
-------------

Documentation of development version at https://ezdxf.mozman.at/docs

Documentation of latest release at http://ezdxf.readthedocs.io/

Knowledge Graph
---------------

The :ref:`knowledge_graph` contains additional information beyond the documentation and is 
managed by `logseq <https://logseq.com/>`_.  The source data is included in the repository 
in the folder ``ezdxf/notes``.  There is also a `HTML export <https://ezdxf.mozman.at/notes/#/page/ezdxf>`_
on the website which gets regular updates.

Release Notes
-------------

The `release notes <https://ezdxf.mozman.at/notes/#/page/release%20notes>`_ are included 
in the :ref:`knowledge_graph`.

Changelog
---------

The `changelog <https://ezdxf.mozman.at/notes/#/page/changelog>`_ is included 
in the :ref:`knowledge_graph`.


Source Code & Feedback
----------------------

Source Code: http://github.com/mozman/ezdxf.git

Issue Tracker: http://github.com/mozman/ezdxf/issues

Forum: https://github.com/mozman/ezdxf/discussions

Questions and Answers
---------------------

Please post questions at the `forum <https://github.com/mozman/ezdxf/discussions>`_
or `stack overflow <https://stackoverflow.com/>`_ to make answers available to
other users as well.


Contents
========

.. toctree::
   :maxdepth: 3

   introduction
   setup
   usage_for_beginners
   concepts/index
   tasks/index
   xref
   addons/index
   reference
   launcher
   tutorials/index
   howto/index
   faq
   glossary
   knowledgegraph

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`


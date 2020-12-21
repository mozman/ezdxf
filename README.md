
ezdxf
=====

Abstract
--------

A Python package to create and modify DXF drawings, independent of the DXF
version. You can open/save every DXF file without losing any content (except comments),
Unknown tags in the DXF file will be ignored but preserved for saving. With this behavior
it is possible to open also DXF drawings that contains data from 3rd party applications.

Quick-Info
----------

- ezdxf is a Python package to create new DXF files and read/modify/write existing DXF files
- the intended audience are developers
- requires at least Python 3.6
- OS independent
- tested with CPython and pypy3
- C-extensions for CPython as binary wheels available on PyPI for Windows, Linux and macOS
- additional required packages: [pyparsing](https://pypi.org/project/pyparsing/) 
- optional Cython implementation of some low level math classes
- MIT-License
- read/write/new support for DXF versions: R12, R2000, R2004, R2007, R2010, R2013 and R2018
- additional read support for DXF versions R13/R14 (upgraded to R2000)
- additional read support for older DXF versions than R12 (upgraded to R12)
- read/write support for ASCII DXF and Binary DXF
- preserves third-party DXF content

Included Extensions
-------------------

- The `drawing` add-on is a translation layer to send DXF data to a render backend, interfaces to 
  [matplotlib](https://pypi.org/project/matplotlib/), which can export images as png, pdf or svg, 
  and [PyQt5](https://pypi.org/project/PyQt5/) are implemented.
- `geo` add-on to support the [`__geo_interface__`](https://gist.github.com/sgillies/2217756)
- `r12writer` add-on to write basic DXF entities direct and fast into a DXF R12 file or stream
- `iterdxf` add-on to iterate over DXF entities of the modelspace of really big (> 5GB) DXF files which
  do not fit into memory
- `Importer` add-on to import entities, blocks and table entries from another DXF document
- `dxf2code` add-on to generate Python code for DXF structures loaded from DXF 
  documents as starting point for parametric DXF entity creation
- Plot Style Files (CTB/STB) read/write add-on

A simple example:

```python
import ezdxf

# Create a new DXF document.
doc = ezdxf.new(dxfversion='R2010')

# Create new table entries (layers, linetypes, text styles, ...).
doc.layers.new('TEXTLAYER', dxfattribs={'color': 2})

# DXF entities (LINE, TEXT, ...) reside in a layout (modelspace, 
# paperspace layout or block definition).  
msp = doc.modelspace()

# Add entities to a layout by factory methods: layout.add_...() 
msp.add_line((0, 0), (10, 0), dxfattribs={'color': 7})
msp.add_text(
    'Test', 
    dxfattribs={
        'layer': 'TEXTLAYER'
    }).set_pos((0, 0.2), align='CENTER')

# Save DXF document.
doc.saveas('test.dxf')
```

Example for the *r12writer*, which writes a simple DXF R12 file without 
in-memory structures:

```python
from random import random
from ezdxf.addons import r12writer

MAX_X_COORD = 1000
MAX_Y_COORD = 1000

with r12writer("many_circles.dxf") as doc:
    for _ in range(100000):
        doc.add_circle((MAX_X_COORD*random(), MAX_Y_COORD*random()), radius=2)
```

The r12writer supports only the ENTITIES section of a DXF R12 drawing, no HEADER, 
TABLES or BLOCKS section is present, except FIXED-TABLES are written, than some 
additional predefined text styles and line types are available.

Installation
------------

Install with pip including the optional C-extensions from PyPI as binary wheels:

    pip install ezdxf

Install from source code. To build the optional C-extensions the Cython package, 
and a working C++ compiler setup is required:

    python setup.py install

Install the latest development version with pip from GitHub:

    pip install git+https://github.com/mozman/ezdxf.git@master


Dependencies in Detail
----------------------

The `pyparsing` package is the only hard dependency and will be installed 
automatically by `pip`!

- INSTALL from PyPI including C-extensions: pyparsing (most common case)
- INSTALL from PyPI for usage of the `drawing` add-on: pyparsing, matplotlib, pyqt5
- INSTALL from source code without C-extensions: setuptools, pyparsing
- INSTALL from source code including C-extensions: setuptools, pyparsing, 
  Cython, and a working C++ compiler setup 
- TESTING requires the additional packages: pytest, [geomdl](https://github.com/orbingol/NURBS-Python)
- BUILD packages from source code without C-extensions: setuptools, wheel
- BUILD packages from source code including C-extensions: setuptools, wheel, 
  Cython, and a working C++ compiler setup

Install all optional packages:

    pip install setuptools wheel cython pytest geomdl matplotlib pyqt5

Windows users who want to compile the C-extensions from source code need the 
build tools from Microsoft: https://visualstudio.microsoft.com/de/downloads/ 

Download and install the required Visual Studio Installer of the community 
edition and choose the option: `Visual Studio Build Tools 20..`

Website
-------

https://ezdxf.mozman.at/

Documentation
-------------

Documentation of development version at https://ezdxf.mozman.at/docs

Documentation of the latest release at http://ezdxf.readthedocs.io/

Contribution
------------

The source code of *ezdxf* can be found at __GitHub__, target your pull requests 
to the `master` branch:

http://github.com/mozman/ezdxf.git


Feedback
--------

Questions and feedback at __GitHub Discussions__:

https://github.com/mozman/ezdxf/discussions

Questions at __Stack Overflow__:

Post questions at [stack overflow](https://stackoverflow.com/) and use the tag `dxf` or `ezdxf`.

Issue tracker at __GitHub__:

http://github.com/mozman/ezdxf/issues

Contact
-------

Please __always__ post questions at the [forum](https://github.com/mozman/ezdxf/discussions) 
or [stack overflow](https://stackoverflow.com/) to make answers 
available to other users as well. 

ezdxf@mozman.at

Feedback is greatly appreciated.

Manfred

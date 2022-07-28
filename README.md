
ezdxf
=====

Abstract
--------

A Python package for creating and modifying DXF drawings, regardless of the DXF
version. You can open/save any DXF file without losing content (except comments).
Unknown tags in the DXF file are ignored but retained for saving. With this behavior
it is possible to also open DXF drawings that contain data from third-party 
applications.

Quick-Info
----------

- *ezdxf* is a Python package to create new DXF files and read/modify/write 
  existing DXF files
- MIT-License
- the intended audience are programmers
- requires at least Python 3.7
- OS independent
- tested with CPython and pypy3
- has type annotations and passes `mypy --ignore-missing-imports -p ezdxf` successful
- additional required packages for the core package without add-ons: 
  [typing_extensions](https://pypi.org/project/typing-extensions/), 
  [pyparsing](https://pypi.org/project/pyparsing/) 
- read/write/new support for DXF versions: R12, R2000, R2004, R2007, R2010, R2013 and R2018
- read-only support for DXF versions R13/R14 (upgraded to R2000)
- read-only support for older DXF versions than R12 (upgraded to R12)
- read/write support for ASCII DXF and Binary DXF
- retains third-party DXF content
- optional C-extensions for CPython are included in the binary wheels, available 
  on [PyPI](https://pypi.org/project/ezdxf/) for Windows, Linux and macOS

Included Extensions
-------------------

Additional packages required for these add-ons are not automatically installed 
during the *basic* setup, for more information about the setup & dependencies 
visit the [documentation](https://ezdxf.mozman.at/docs/setup.html).

- The `drawing` add-on is a translation layer to send DXF data to a render backend, 
  interfaces to [matplotlib](https://pypi.org/project/matplotlib/), which can export 
  images as png, pdf or svg, and [PyQt5](https://pypi.org/project/PyQt5/) are implemented.
- `r12writer` add-on to write basic DXF entities direct and fast into a DXF R12 
  file or stream
- `iterdxf` add-on to iterate over DXF entities from the modelspace of huge DXF 
  files (> 5GB) which do not fit into memory
- `Importer` add-on to import entities, blocks and table entries from another DXF document
- `dxf2code` add-on to generate Python code for DXF structures loaded from DXF 
  documents as starting point for parametric DXF entity creation
- `acadctb` add-on to read/write plot style files (CTB/STB)
- `pycsg` add-on for basic Constructive Solid Geometry (CSG) modeling
- `MTextExplode` add-on for exploding MTEXT entities into single-line TEXT entities
- `text2path` add-on to convert text into linear paths
- `geo` add-on to support the [`__geo_interface__`](https://gist.github.com/sgillies/2217756)
- `meshex` for exchanging meshes with other tools as STL, OFF or OBJ files
- `openscad` add-on, an interface to [OpenSCAD](https://openscad.org)
- `odafc` add-on, an interface to the [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) 
  to read and write DWG files

A simple example:

```Python
import ezdxf

# Create a new DXF document.
doc = ezdxf.new(dxfversion="R2010")

# Create new table entries (layers, linetypes, text styles, ...).
doc.layers.add("TEXTLAYER", color=2)

# DXF entities (LINE, TEXT, ...) reside in a layout (modelspace, 
# paperspace layout or block definition).  
msp = doc.modelspace()

# Add entities to a layout by factory methods: layout.add_...() 
msp.add_line((0, 0), (10, 0), dxfattribs={"color": 7})
msp.add_text(
    "Test", 
    dxfattribs={
        "layer": "TEXTLAYER"
    }).set_pos((0, 0.2), align="CENTER")

# Save the DXF document.
doc.saveas("test.dxf")
```

Example for the *r12writer*, which writes a simple DXF R12 file without 
in-memory structures:

```Python
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

Basic installation by pip including the optional C-extensions from PyPI as 
binary wheels:

    pip install ezdxf

Full installation with all dependencies (matplotlib, PyQt5) to use the 
drawing add-on:

    pip install ezdxf[draw]

For more information about the setup & dependencies visit the 
[documentation](https://ezdxf.mozman.at/docs/setup.html).

Website
-------

https://ezdxf.mozman.at/

Documentation
-------------

Documentation of the development version at https://ezdxf.mozman.at/docs

Documentation of the latest release at https://ezdxf.readthedocs.io/

Contribution
------------

The source code of *ezdxf* can be found at __GitHub__, target your pull requests 
to the `master` branch:

https://github.com/mozman/ezdxf.git


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

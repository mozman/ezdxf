
Setup & Dependencies
====================

The primary goal is to keep the dependencies for the `core` package as small
as possible. The add-ons are not part of the core package and can therefore
use as many packages as needed. The only requirement for these packages is an
easy way to install them on Windows, Linux and macOS, preferably as
``pip3 install ...``.

The ``pyparsing`` package is the only hard dependency and will be installed
automatically by ``pip3``!

Ezdxf provides since v0.15 some C-extensions, which will be deployed
automatically at each release to PyPI as binary wheels for Windows,
ManyLinux 2010 and macOS. The supported Python versions start with the latest
stable version of pypy3, which is currently Python 3.7 (2021) and ends with
the latest stable release of CPython.

The C-extensions are disabled for pypy3, because the JIT compiled code of pypy
is much faster than the compiled C-extensions for pypy.

Basic Installation
------------------

The most common case is the installation by ``pip3`` including the optional
C-extensions from PyPI as binary wheels::

    pip3 install ezdxf

Installation with Extras
------------------------

To use all features of the drawing add-on, add the [draw] tag::

    pip3 install ezdxf[draw]

======== ===================================================
Tag      Additional Installed Packages
======== ===================================================
[draw]   matplotlib, PyQt5
[test]   geomdl, pytest
[dev]    setuptools, wheel, Cython + [test]
[all]    [draw] + [test] + [dev]
======== ===================================================

Disable C-Extensions
--------------------

It is possible to disable the C-Extensions by setting the
environment variable ``EZDXF_DISABLE_C_EXT`` to ``1`` or ``true``::

    set EZDXF_DISABLE_C_EXT=1

or on Linux::

    export EZDXF_DISABLE_C_EXT=1

This is has to be done **before** anything from ezdxf is imported! If you are
working in an interactive environment, you have to restart the interpreter.


Installation from GitHub
------------------------

Install the latest development version by ``pip3`` from GitHub::

    pip3 install git+https://github.com/mozman/ezdxf.git@master

Build and Install from Source
-----------------------------

Make a build directory and a virtual environment and sorry,
I am working on Windows::

    mkdir build
    cd build
    py -m venv py39
    py39\Scripts\activate.bat

A working C++ compiler setup is required to compile the C-extensions from source
code. Windows users need the build tools from
Microsoft: https://visualstudio.microsoft.com/de/downloads/

Download and install the required Visual Studio Installer of the community
edition and choose the option: `Visual Studio Build Tools 20..`

Install required packages to build and install ezdxf with C-extensions::

    pip3 install setuptools wheel cython

Clone the GitHub repository::

    git clone https://github.com/mozman/ezdxf.git

Build and install ezdxf from source code::

    cd ezdxf
    pip3 install .

Install the test dependencies and run the tests::

    pip3 install pytest geomdl
    pytest tests integration_tests

Install optional dependencies to use all features, like the drawing add-on::

    pip3 install matplotlib pyqt

Build Documentation
-------------------

Assuming you are still in the build directory ``build\ezdxf`` of the previous
section and matplotlib is installed.

Install Sphinx::

    pip3 install Sphinx sphinx-rtd-theme

Build the HTML documentation::

    cd docs
    make.bat html

The output is located in ``build\ezdxf\docs\build\html``.

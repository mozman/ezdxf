
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
[draw]   Matplotlib, PySide6
[draw5]  Matplotlib, PyQt5 (use only if PySide6 is not available)
[test]   geomdl, pytest
[dev]    setuptools, wheel, Cython + [test]
[all]    [draw] + [test] + [dev]
[all5]   [draw5] + [test] + [dev]  (use only if PySide6 is not available)
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

Make a build directory and a virtual environment and I'm sorry, but I mostly
use Windows for work::

    mkdir build
    cd build
    py -m venv py39
    py39\Scripts\activate.bat

Windows Requirements
++++++++++++++++++++

A working C++ compiler setup is required to compile the C-extensions from source
code. Windows users need the build tools from
Microsoft: https://visualstudio.microsoft.com/de/downloads/

Download and install the required Visual Studio Installer of the community
edition and choose the option: `Visual Studio Build Tools 20..`

Install required packages to build and install ezdxf with C-extensions::

    pip3 install setuptools wheel cython

Linux Requirements
++++++++++++++++++

I got a Raspberry Pi 400 for testing `ezdxf` on ARM64 hardware and I use
sometimes the Windows Subsystem for Linux (WSL2) with Ubuntu for some tests.

Install python packages on Linux from the distribution repository if
available by the system packager, `apt` in the case of Debian based
distributions like Raspberry Pi OS or Ubuntu::

    sudo apt install python3-pip python3-wheel

Create the venv with access to the system site-packages for using `Matplotlib`
and the Qt bindings from the system installation, see `Install Optional Packages`_::

    python3 -m venv --system-site-packages py37
    source py37\bin\activate

By doing as fresh install on WSL2 & Ubuntu, I encountered an additional
requirement, the ``build-essential`` package adds the required C++ support::

    sudo apt install build-essential

Installation from Source
++++++++++++++++++++++++

Install Cython in the venv to got the C-extensions compiled::

    pip3 install cython

Clone the GitHub repository::

    git clone https://github.com/mozman/ezdxf.git

Build and install ezdxf from source code::

    cd ezdxf
    pip3 install .

Check if the installation was successful::

    ezdxf -V

The output should look like this::

    ezdxf 0.17.2b4 from <path to your venv>
    Python version: 3.10.1 (tags/v3.10.1:2cd268a, Dec  6 2021, 19:10:37) [MSC v.1929 64 bit (AMD64)]
    using C-extensions: yes
    using Matplotlib: yes <after installing Matplotlib!>

Install the test dependencies and run the tests::

    pip3 install pytest geomdl
    python3 -m pytest tests integration_tests

Install Optional Packages
+++++++++++++++++++++++++

Install optional dependencies on Windows by `pip` to use all features, like the
drawing add-on::

    pip3 install matplotlib PySide6

On Linux install `Matplotlib` and the `PyQt5` bindings also by the system
packager, an installation by `pip` in the venv worked, but the packages showed
errors at import on the Raspberry Pi::

    sudo apt install python3-matplotlib python3-pyqt5

`PySide6` is the preferred Qt binding but wasn't available on the Debian based
distributions at the time of writing this - `PyQt5` is supported as fallback.

Build Documentation
-------------------

Assuming you are still in the build directory ``build\ezdxf`` of the previous
section and matplotlib is installed.

Install Sphinx::

    pip3 install Sphinx sphinx-rtd-theme

Build the HTML documentation::

    cd docs
    make html

The output is located in ``build\ezdxf\docs\build\html``.

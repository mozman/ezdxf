
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

Windows 10
++++++++++

Make a build directory and a virtual environment::

    mkdir build
    cd build
    py -m venv py310
    py310/Scripts/activate.bat


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

Check if the installation was successful::

    python3 -m ezdxf -V

The `ezdxf` command should run without a preceding `python3 -m`, but calling the
launcher through the interpreter guarantees to call the version which was
installed in the venv if there exist a global installation of `ezdxf` like in
my case.

The output should look like this::

    ezdxf 0.17.2b4 from D:\Source\build\py310\lib\site-packages\ezdxf
    Python version: 3.10.1 (tags/v3.10.1:2cd268a, Dec  6 2021, 19:10:37) [MSC v.1929 64 bit (AMD64)]
    using C-extensions: yes
    using Matplotlib: no

To install optional packages go to section: `Install Optional Packages`_

To run then included tests go to section: `Run the Tests`_

WSL2 & Ubuntu
+++++++++++++

I use sometimes the Windows Subsystem for Linux (WSL2) with Ubuntu 20.04 LTS
for some tests.

By doing as fresh install on WSL2 & Ubuntu, I encountered an additional
requirement, the `build-essential` package adds the required C++ support::

    sudo apt install build-essential

The system Python 3 interpreter has the version 3.8, but I will show you how to
install an additional newer Python version from the source code in a later
section::

    cd ~
    mkdir build
    cd build
    python3 -m venv py38
    source py38/bin/activate

Install `Cython` and `wheel` in the venv to got the C-extensions compiled::

    pip3 install cython wheel

Clone the GitHub repository::

    git clone https://github.com/mozman/ezdxf.git

Build and install ezdxf from source code::

    cd ezdxf
    pip3 install .

Check if the installation was successful::

    python3 -m ezdxf -V

The output should look like this::

    ezdxf 0.17.2b4 from /home/mozman/src/py38/lib/python3.8/site-packages/ezdxf
    Python version: 3.8.10 (default, Nov 26 2021, 20:14:08)
    [GCC 9.3.0]
    using C-extensions: yes
    using Matplotlib: no

To install optional packages go to section: `Install Optional Packages`_

To run then included tests go to section: `Run the Tests`_

Raspberry Pi OS
+++++++++++++++

Testing platform is a Raspberry Pi 400 and the OS is the Raspberry Pi OS which
runs on 64bit hardware but it is a 32bit OS.

The system Python 3 interpreter is the version 3.7, but I will show you how to
install an additional newer Python version from the source code in a later
section.

Install the build requirements, `Matplotlib` and the `PyQt5` bindings
from the distribution repository::

    sudo apt install python3-pip python3-matplotlib python3-pyqt5

Installing `Matplotlib` and the `PyQt5` bindings by `pip` from `piwheels.org`
in the venv worked, but the packages showed errors at import. `PySide6` is the
preferred Qt binding but wasn't available on Raspberry Pi OS at the time of
writing this - `PyQt5` is supported as fallback.

Create the venv with access to the system site-packages for using `Matplotlib`
and the Qt bindings from the system installation::

    cd ~
    mkdir build
    cd build
    python3 -m venv --system-site-packages py37
    source py37/bin/activate

Install `Cython` and  `wheel` in the venv to got the C-extensions compiled::

    pip3 install cython wheel

Clone the GitHub repository::

    git clone https://github.com/mozman/ezdxf.git

Build and install ezdxf from source code::

    cd ezdxf
    pip3 install .

Check if the installation was successful::

    python3 -m ezdxf -V

The output should look like this::

    ezdxf 0.17.2b4 from /home/pi/src/py37/lib/python3.7/site-packages/ezdxf
    Python version: 3.7.3 (default, Jan 22 2021, 20:04:44)
    [GCC 8.3.0]
    using C-extensions: yes
    using Matplotlib: yes

To run then included tests go to section: `Run the Tests`_

Install Optional Packages
-------------------------

Only Windows & Ubuntu, for Raspberry Pi OS install the packages by the system
packager.

Install optional dependencies by `pip` to use all features, like the
`drawing` add-on::

    pip3 install matplotlib PySide6

Run the Tests
-------------

This is the same procedure for all systems, assuming you are still in
the build directory `build/ezdxf` and `ezdxf` is now installed in the venv.

Install the test dependencies and run the tests::

    pip3 install pytest geomdl
    python3 -m pytest tests integration_tests

Build Documentation
-------------------

Assuming you are still in the build directory `build/ezdxf` of the previous
section.

Install Sphinx::

    pip3 install Sphinx sphinx-rtd-theme

Build the HTML documentation::

    cd docs
    make html

The output is located in `build/ezdxf/docs/build/html`.

Python from Source
------------------

Debian based systems have often very outdated software installed and
sometimes there is no easy way to install a newer Python version.
This is a brief summery how I installed Python 3.9.9 on my
Raspberry Pi 400, for more information go to the source of the recipe: `Real Python`_

Install build requirements::

    sudo apt-get update
    sudo apt-get upgrade

    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
       libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
       libncurses5-dev libncursesw5-dev xz-utils tk-dev

Make a build directory::

    cd ~
    mkdir build
    cd build

Download and unpack the source code from `Python.org`_, replace 3.9.9 by
your desired version::

    wget https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tgz
    tar -xvzf Python-3.9.9.tgz
    cd Python-3.9.9/

Configure the build process, use a prefix to the directory where the
interpreter will be installed::

    ./configure --prefix=/opt/python3.9.9 --enable-optimizations

Build & install the Python interpreter. The `-j` option simply tells `make` to
split the building into parallel steps to speed up the compilation, the
Raspberry Pi 400 has 4 cores so 4 seems to be a good choice::

    make -j 4
    sudo make install

The building time was ~25min and the new Python 3.9.9 interpreter is now
installed as `/opt/python3.9.9/bin/python3`.

At the time there were no system packages for `Matplotlib` and `PyQt5` for
this new Python version available, so there is no benefit of using the option
`--system-site-packages` for building the venv::

    cd ~/build
    /opt/python3.9.9/bin/python3 -m venv py39
    source py39/bin/activate

I have not tried to build `Matplotlib` and `PyQt5` by myself and the
installation by `pip` from `piwheels.org` did not work, in this case you don't
get `Matplotlib` support for better font measuring and the `drawing` add-on will
not work.

Proceed with the `ezdxf` installation from source as shown for the  `Raspberry Pi OS`_.

.. _Real Python:  https://realpython.com/installing-python/#how-to-build-python-from-source-code
.. _python.org: https://www.python.org
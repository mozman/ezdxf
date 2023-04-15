
Setup & Dependencies
====================

The primary goal is to keep the dependencies of the `core` package as small
as possible. The add-ons are not part of the core package and can therefore
use as many packages as needed. The only requirement for these packages is an
easy way to install them on `Windows`, `Linux` and `macOS`, preferably as::

    pip3 install ezdxf

The `pyparsing`_ package and the `typing_extensions`_ are the only hard dependency
and will be installed automatically by `pip3`!

The minimal required Python version is determined by the latest stable version
of `pypy3`_ and the Python version deployed by the `Raspberry Pi`_ OS, which
would be Python 3.9 in 2022, but Python 3.7 will be kept as the minimal version
for the 1.0 release.

Basic Installation
------------------

The most common case is the installation by `pip3` including the optional
C-extensions from `PyPI`_ as binary wheels::

    pip3 install ezdxf

Installation with Extras
------------------------

To use all features of the drawing add-on, add the [draw] tag::

    pip3 install ezdxf[draw]

======== ===================================================
Tag      Additional Installed Packages
======== ===================================================
[draw]   `Matplotlib`_, `PySide6`_, `Pillow`_, `PyMuPDF`_
[draw5]  `Matplotlib`_, `PyQt5`_, `Pillow`_, `PyMuPDF`_ (use only if PySide6 is not available)
[test]   geomdl, pytest
[dev]    setuptools, wheel, Cython + [test]
[all]    [draw] + [test] + [dev]
[all5]   [draw5] + [test] + [dev]  (use only if PySide6 is not available)
======== ===================================================

Binary Wheels
-------------

Ezdxf includes some C-extensions, which will be deployed
automatically at each release to `PyPI`_ as binary wheels to `PyPI`:

- `Windows`: only amd64 packages
- `Linux`: manylinux and musllinux packages for x86_64 & aarch64
- `macOS`: x86_64, arm64 and universal packages

The wheels are created by the continuous integration (CI) service provided by
`GitHub`_ and the build container `cibuildwheel`_ provided by `PyPA`_ the Python
Packaging Authority.
The `workflows`_ are kept short and simple, so my future me will understand what's
going on and they are maybe also helpful for other developers which do not touch
CI services every day.

The C-extensions are disabled for `pypy3`_, because the JIT compiled code of pypy
is much faster than the compiled C-extensions.

Disable C-Extensions
--------------------

It is possible to disable the C-Extensions by setting the
environment variable ``EZDXF_DISABLE_C_EXT`` to ``1`` or ``true``::

    set EZDXF_DISABLE_C_EXT=1

or on Linux::

    export EZDXF_DISABLE_C_EXT=1

This is has to be done **before** anything from `ezdxf` is imported! If you are
working in an interactive environment, you have to restart the interpreter.


Installation from GitHub
------------------------

Install the latest development version by `pip3` from `GitHub`_::

    pip3 install git+https://github.com/mozman/ezdxf.git@master

Build and Install from Source
-----------------------------

This is only required if you want the compiled C-extensions, the `ezdxf`
installation by `pip` from the source code package works without the C-extension
but is slower. There are binary wheels available on `PyPi`_ which included the
compiled C-extensions.

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

Clone the `GitHub`_ repository::

    git clone https://github.com/mozman/ezdxf.git

Build and install ezdxf from source code::

    cd ezdxf
    pip3 install .

Check if the installation was successful::

    python3 -m ezdxf -V

The `ezdxf` command should run without a preceding `python3 -m`, but calling the
launcher through the interpreter guarantees to call the version which was
installed in the venv if there exist a global installation of `ezdxf` like in
my development environment.

The output should look like this::

    ezdxf 0.17.2b4 from D:\Source\build\py310\lib\site-packages\ezdxf
    Python version: 3.10.1 (tags/v3.10.1:2cd268a, Dec  6 2021, 19:10:37) [MSC v.1929 64 bit (AMD64)]
    using C-extensions: yes
    using Matplotlib: no

To install optional packages go to section: `Install Optional Packages`_

To run the included tests go to section: `Run the Tests`_

WSL & Ubuntu
++++++++++++

I use sometimes the Windows Subsystem for Linux (`WSL`_) with `Ubuntu`_ 20.04 LTS
for some tests (how to install `WSL`_).

By doing as fresh install on `WSL & Ubuntu`, I encountered an additional
requirement, the `build-essential` package adds the required C++ support::

    sudo apt install build-essential

The system Python 3 interpreter has the version 3.8 (in 2021), but I will show
in a later section how to install an additional newer Python version from the
source code::

    cd ~
    mkdir build
    cd build
    python3 -m venv py38
    source py38/bin/activate

Install `Cython` and `wheel` in the venv to get the C-extensions compiled::

    pip3 install cython wheel

Clone the `GitHub`_ repository::

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

To run the included tests go to section: `Run the Tests`_

Raspberry Pi OS
+++++++++++++++

Testing platform is a `Raspberry Pi`_ 400 and the OS is the `Raspberry Pi`_ OS
which runs on 64bit hardware but is a 32bit OS. The system Python 3
interpreter comes in version 3.7 (in 2021), but I will show in a later
section how to install an additional newer Python version from the source code.

Install the build requirements, `Matplotlib`_ and the `PyQt5`_ bindings
from the distribution repository::

    sudo apt install python3-pip python3-matplotlib python3-pyqt5

Installing `Matplotlib`_ and the `PyQt5`_ bindings by `pip` from `piwheels`_
in the venv worked, but the packages showed errors at import, seems to be an
packaging error in the required `numpy`_ package.
`PySide6`_ is the preferred Qt binding but wasn't available on `Raspberry Pi`_
OS at the time of writing this - `PyQt5`_ is supported as fallback.

Create the venv with access to the system site-packages for using `Matplotlib`_
and the Qt bindings from the system installation::

    cd ~
    mkdir build
    cd build
    python3 -m venv --system-site-packages py37
    source py37/bin/activate

Install `Cython` and  `wheel` in the venv to get the C-extensions compiled::

    pip3 install cython wheel

Clone the `GitHub`_ repository::

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

To run the included tests go to section: `Run the Tests`_

Manjaro on Raspberry Pi
+++++++++++++++++++++++

Because the (very well working) `Raspberry Pi`_ OS is only a 32bit OS, I searched
for a 64bit alternative like `Ubuntu`_, which just switched to version 21.10 and
always freezes at the installation process! So I tried `Manjaro`_ as rolling
release, which I used prior in a virtual machine and wasn't really happy,
because there is always something to update. Anyway the distribution
looks really nice and has Python 3.9.9 installed.

Install build requirements and optional packages by the system packager
`pacman`::

    sudo pacman -S python-pip python-matplotlib python-pyqt5

Create and activate the venv::

    cd ~
    mkdir build
    cd build
    python3 -m venv --system-site-packages py39
    source py39/bin/activate

The rest is the same procedure as for the `Raspberry Pi OS`_::

    pip3 install cython wheel
    git clone https://github.com/mozman/ezdxf.git
    cd ezdxf
    pip3 install .
    python3 -m ezdxf -V

To run the included tests go to section: `Run the Tests`_

Ubuntu Server 21.10 on Raspberry Pi
+++++++++++++++++++++++++++++++++++

I gave the `Ubuntu`_ Server 21.10 a chance after the desktop version failed to
install by a nasty bug and it worked well.
The distribution comes with Python 3.9.4 and after installing some
requirements::

    sudo apt install build-essential python3-pip python3.9-venv

The remaining process is like on `WSL & Ubuntu`_ except for the newer Python
version. Installing `Matplotlib`_ by `pip` works as expected and is maybe useful
even on a headless server OS to create SVG and PNG from DXF files.
`PySide6`_ is not available by `pip` and the installation of `PyQt5`_ starts from
the source code package which I stopped because this already didn't finished
on `Manjaro`_, but the installation of the `PyQt5`_ bindings by `apt` works::

    sudo apt install python3-pyqt5

Use the ``--system-site-packages`` option for creating the venv to get access to
the `PyQt5`_ package.

Install Optional Packages
-------------------------

Install the optional dependencies by `pip` only for `Windows 10`_ and
`WSL & Ubuntu`_, for `Raspberry Pi OS`_ and `Manjaro on Raspberry Pi`_ install
these packages by the system packager::

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
This is a brief summery how I installed Python 3.9.9 on the `Raspberry Pi`_ OS,
for more information go to the source of the recipe: `Real Python`_

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
interpreter should be installed::

    ./configure --prefix=/opt/python3.9.9 --enable-optimizations

Build & install the Python interpreter. The `-j` option simply tells `make` to
split the building into parallel steps to speed up the compilation, my
`Raspberry Pi`_ 400 has 4 cores so 4 seems to be a good choice::

    make -j 4
    sudo make install

The building time was ~25min and the new Python 3.9.9 interpreter is now
installed as `/opt/python3.9.9/bin/python3`.

At the time there were no system packages for `Matplotlib`_ and `PyQt5`_ for
this new Python version available, so there is no benefit of using the option
``--system-site-packages`` for building the venv::

    cd ~/build
    /opt/python3.9.9/bin/python3 -m venv py39
    source py39/bin/activate

I have not tried to build `Matplotlib`_ and `PyQt5`_ by myself and the
installation by `pip` from `piwheels`_ did not work, in this case you don't
get `Matplotlib`_ support for better font measuring and the `drawing` add-on
will not work.

Proceed with the `ezdxf` installation from source as shown for the  `Raspberry Pi OS`_.

.. _Real Python:  https://realpython.com/installing-python/#how-to-build-python-from-source-code
.. _python.org: https://www.python.org
.. _piwheels: https://piwheels.org
.. _Matplotlib: https://matplotlib.org
.. _Manjaro: https://www.manjaro.org
.. _Ubuntu: https://ubuntu.com
.. _Raspberry Pi: https://www.raspberrypi.com
.. _wsl: https://docs.microsoft.com/en-us/windows/wsl/install
.. _pyqt5: https://pypi.org/project/PyQt5/
.. _pyside6: https://pypi.org/project/PySide6/
.. _pillow: https://pypi.org/project/Pillow/
.. _PyMuPDF: https://pypi.org/project/PyMuPDF/
.. _numpy: https://pypi.org/project/numpy/
.. _pyparsing: https://pypi.org/project/pyparsing/
.. _typing_extensions: https://pypi.org/project/typing_extensions/
.. _pypi: https://pypi.org/project/ezdxf
.. _pypy3: https://www.pypy.org
.. _pypa: https://www.pypa.io/en/latest/
.. _cibuildwheel: https://github.com/pypa/cibuildwheel
.. _github: https://github.com
.. _workflows: https://github.com/mozman/ezdxf/tree/master/.github/workflows
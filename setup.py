#!/usr/bin/env python3
# Copyright (c) 2011-2024 Manfred Moitzi
# License: MIT License
import sys
from setuptools import setup
from setuptools import Extension

# setuptools docs: https://setuptools.pypa.io/en/latest/index.html
# build source distribution
#
#   python setup.py sdist --formats=zip,gztar
#
# build wheels:
#
#   python setup.py bdist_wheel
#
# All Cython accelerated modules are optional:
ext_modules = [
    Extension("ezdxf.acc.vector", ["src/ezdxf/acc/vector.pyx"], optional=True),
    Extension("ezdxf.acc.matrix44", ["src/ezdxf/acc/matrix44.pyx"], optional=True),
    Extension("ezdxf.acc.bezier4p", ["src/ezdxf/acc/bezier4p.pyx"], optional=True),
    Extension("ezdxf.acc.bezier3p", ["src/ezdxf/acc/bezier3p.pyx"], optional=True),
    Extension("ezdxf.acc.bspline", ["src/ezdxf/acc/bspline.pyx"], optional=True),
    Extension("ezdxf.acc.construct", ["src/ezdxf/acc/construct.pyx"], optional=True),
    Extension(
        "ezdxf.acc.mapbox_earcut", ["src/ezdxf/acc/mapbox_earcut.pyx"], optional=True
    ),
    Extension("ezdxf.acc.linetypes", ["src/ezdxf/acc/linetypes.pyx"], optional=True),
    Extension("ezdxf.acc.np_support", ["src/ezdxf/acc/np_support.pyx"], optional=True),
]
commands = {}
try:
    from Cython.Distutils import build_ext

    commands = {"build_ext": build_ext}
except ImportError:
    ext_modules = []


PYPY = hasattr(sys, "pypy_version_info")
if PYPY:
    print(
        "C-extensions are disabled for pypy, because JIT compiled Python code "
        "is much faster!"
    )
    ext_modules = []
    commands = {}


def get_version() -> str:
    v = {}
    for line in open("./src/ezdxf/version.py").readlines():
        if line.strip().startswith("__version__"):
            exec(line, v)
            return v["__version__"]
    raise IOError("__version__ string not found")


# static attributes are stored in pyproject.toml
# https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
# https://setuptools.pypa.io/en/latest/index.html
setup(
    version=get_version(),
    cmdclass=commands,
    ext_modules=ext_modules,
)

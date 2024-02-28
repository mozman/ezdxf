#!/usr/bin/env python3
# Copyright (c) 2011-2024 Manfred Moitzi
# License: MIT License
import os
import sys
from setuptools import setup, find_packages
from setuptools import Extension

# setuptools docs: https://setuptools.readthedocs.io/en/latest/setuptools.html
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

    commands["build_ext"] = build_ext
except ImportError:
    ext_modules.clear()


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


def read(fname: str) -> str:
    try:
        with open(os.path.join(os.path.dirname(__file__), fname)) as f:
            return f.read()
    except IOError:
        return "File '%s' not found.\n" % fname


DRAW = ["matplotlib", "PySide6", "PyMuPDF>=1.20.0", "Pillow"]
DRAW5 = ["matplotlib", "PyQt5", "PyMuPDF>=1.20.0", "Pillow"]
TEST = ["pytest", "Pillow"]
DEV = ["setuptools", "wheel", "Cython"]

setup(
    name="ezdxf",
    version=get_version(),
    description="A Python package to create/manipulate DXF drawings.",
    author="Manfred Moitzi",
    url="https://ezdxf.mozman.at",
    download_url="https://pypi.org/project/ezdxf/",
    author_email="me@mozman.at",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages("src"),
    zip_safe=False,
    package_data={
        "ezdxf": [
            "pp/*.html",
            "pp/*.js",
            "pp/*.css",
            "resources/*.png",
            "py.typed",
        ]
    },
    entry_points={
        "console_scripts": [
            "ezdxf = ezdxf.__main__:main",  # ezdxf launcher
        ]
    },
    provides=["ezdxf"],
    cmdclass=commands,
    ext_modules=ext_modules,
    install_requires=[
        "pyparsing>=2.0.1",
        "typing_extensions>=4.6.0",
        "numpy",
        "fonttools",
    ],
    setup_requires=["setuptools", "wheel"],
    tests_require=TEST,
    extras_require={
        "draw": DRAW,
        "draw5": DRAW5,
        "dev": DRAW + TEST + DEV,
        "dev5": DRAW5 + TEST + DEV,
    },
    keywords=["DXF", "CAD"],
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    platforms="OS Independent",
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
)

# Development Status :: 3 - Alpha
# Development Status :: 4 - Beta
# Development Status :: 5 - Production/Stable
# Development Status :: 6 - Mature
# Development Status :: 7 - Inactive

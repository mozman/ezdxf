#!/usr/bin/env python3
# Copyright (c) 2011-2021 Manfred Moitzi
# License: MIT License
import os
import sys
from setuptools import setup, find_packages
from setuptools import Extension

# setuptools docs: https://setuptools.readthedocs.io/en/latest/setuptools.html
# All Cython accelerated modules are optional:
ext_modules = [
    Extension(
        "ezdxf.acc.vector",
        [
            "src/ezdxf/acc/vector.pyx",
        ],
        optional=True,
        language="c++",
    ),
    Extension(
        "ezdxf.acc.matrix44",
        [
            "src/ezdxf/acc/matrix44.pyx",
        ],
        optional=True,
        language="c++",
    ),
    Extension(
        "ezdxf.acc.bezier4p",
        [
            "src/ezdxf/acc/bezier4p.pyx",
            "src/ezdxf/acc/_cpp_cubic_bezier.cpp",
        ],
        optional=True,
        language="c++",
    ),
    Extension(
        "ezdxf.acc.bezier3p",
        [
            "src/ezdxf/acc/bezier3p.pyx",
            "src/ezdxf/acc/_cpp_quad_bezier.cpp",
        ],
        optional=True,
        language="c++",
    ),
    Extension(
        "ezdxf.acc.bspline",
        [
            "src/ezdxf/acc/bspline.pyx",
        ],
        optional=True,
        language="c++",
    ),
    Extension(
        "ezdxf.acc.construct",
        [
            "src/ezdxf/acc/construct.pyx",
        ],
        optional=True,
        language="c++",
    ),
    Extension(
        "ezdxf.acc.mapbox_earcut",
        [
            "src/ezdxf/acc/mapbox_earcut.pyx",
        ],
        optional=True,
        language="c++",
    ),
    Extension(
        "ezdxf.acc.linetypes",
        [
            "src/ezdxf/acc/linetypes.pyx",
        ],
        optional=True,
        language="c++",
    ),

]
try:
    from Cython.Distutils import build_ext

    commands = {"build_ext": build_ext}
except ImportError:
    ext_modules = []
    commands = {}


PYPY = hasattr(sys, "pypy_version_info")
if PYPY:
    print(
        "C-extensions are disabled for pypy, because JIT compiled Python code "
        "is much faster!"
    )
    ext_modules = []
    commands = {}


def get_version():
    v = {}
    for line in open("./src/ezdxf/version.py").readlines():
        if line.strip().startswith("__version__"):
            exec(line, v)
            return v["__version__"]
    raise IOError("__version__ string not found")


def read(fname, until=""):
    def read_until(lines):
        last_index = -1
        for index, line in enumerate(lines):
            if line.startswith(until):
                last_index = index
                break
        return "".join(lines[:last_index])

    try:
        with open(os.path.join(os.path.dirname(__file__), fname)) as f:
            return read_until(f.readlines()) if until else f.read()
    except IOError:
        return "File '%s' not found.\n" % fname


DRAW = ["matplotlib", "PySide6", "Pillow", "PyMuPDF"]
DRAW5 = ["matplotlib", "PyQt5", "Pillow", "PyMuPDF"]
TEST = ["pytest", "geomdl"]
DEV = ["setuptools", "wheel", "Cython"]

setup(
    name="ezdxf",
    version=get_version(),
    description="A Python package to create/manipulate DXF drawings.",
    author="Manfred Moitzi",
    url="https://ezdxf.mozman.at",
    download_url="https://pypi.org/project/ezdxf/",
    author_email="me@mozman.at",
    python_requires=">=3.8",
    package_dir={"": "src"},
    packages=find_packages("src"),
    zip_safe=False,
    package_data={
        "ezdxf": [
            "pp/*.html",
            "pp/*.js",
            "pp/*.css",
            "tools/font_face_cache.json",
            "tools/font_measurement_cache.json",
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
    install_requires=["pyparsing>=2.0.1", "typing_extensions", "numpy"],
    setup_requires=["wheel"],
    tests_require=["pytest", "geomdl"],
    extras_require={
        "draw": DRAW,
        "draw5": DRAW5,
        "test": TEST,
        "dev": DEV + TEST,
        "all": DRAW + DEV + TEST,
        "all5": DRAW5 + DEV + TEST,
    },
    keywords=["DXF", "CAD"],
    long_description=read("README.md")
    + read("NEWS.md", until="Version 0.11.2"),
    long_description_content_type="text/markdown",
    platforms="OS Independent",
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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

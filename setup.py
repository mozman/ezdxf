#!/usr/bin/env python3
# Created: 10.03.2011
# Copyright (c) 2011-2020 Manfred Moitzi
# License: MIT License
import os
from setuptools import setup, find_packages
from setuptools import Extension
# setuptools docs: https://setuptools.readthedocs.io/en/latest/setuptools.html

# Cython accelerated modules are optional:
try:
    from Cython.Distutils import build_ext

    ext_modules = [
        Extension("ezdxf.acc.vector", [
            "src/ezdxf/acc/vector.pyx",
        ], optional=True, language='c++'),
        Extension("ezdxf.acc.matrix44", [
            "src/ezdxf/acc/matrix44.pyx",
        ], optional=True, language='c++'),
        Extension("ezdxf.acc.bezier4p", [
            "src/ezdxf/acc/bezier4p.pyx",
            "src/ezdxf/acc/_cpp_cubic_bezier.cpp",
        ], optional=True, language='c++'),
        Extension("ezdxf.acc.tagger", [
            "src/ezdxf/acc/tagger.pyx",
        ], optional=True, language='c++'),
    ]
    commands = {'build_ext': build_ext}
except ImportError:
    ext_modules = []
    commands = {}


def get_version():
    v = {}
    for line in open('./src/ezdxf/version.py').readlines():
        if line.strip().startswith('__version__'):
            exec(line, v)
            return v['__version__']
    raise IOError('__version__ string not found')


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


setup(
    name='ezdxf',
    version=get_version(),
    description='A Python package to create/manipulate DXF drawings.',
    author='Manfred Moitzi',
    url='https://ezdxf.mozman.at',
    download_url='https://pypi.org/project/ezdxf/',
    author_email='me@mozman.at',
    python_requires='>=3.6',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    package_data={'ezdxf': [
        'pp/*.html',
        'pp/*.js',
        'pp/*.css',
        'addons/drawing/fonts.json',
    ]},
    entry_points={
        'console_scripts': [
            'dxfpp = ezdxf.pp.__main__:main',  # DXF Pretty Printer
        ]
    },
    provides=['ezdxf'],
    cmdclass=commands,
    ext_modules=ext_modules,
    install_requires=['pyparsing>=2.0.1'],
    setup_requires=['wheel'],
    tests_require=['pytest', 'geomdl'],
    keywords=['DXF', 'CAD'],
    long_description=read('README.md')+read('NEWS.md', until='Version 0.8.9'),
    long_description_content_type="text/markdown",
    platforms="OS Independent",
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)

# Development Status :: 3 - Alpha
# Development Status :: 4 - Beta
# Development Status :: 5 - Production/Stable
# Development Status :: 6 - Mature
# Development Status :: 7 - Inactive

#!/usr/bin/env python
# Created: 10.03.2011
# Copyright (c) 2011-2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import os, sys
from setuptools import setup

PY3 = sys.version_info.major > 2
VERSION = "0.8.9"  # also update VERSION in __init__.py
AUTHOR_NAME = 'Manfred Moitzi'
AUTHOR_EMAIL = 'me@mozman.at'

if PY3:
    PACKAGE_DATA = {'ezdxf': ['templates/*.dxf', 'pp/*.html', 'pp/*.js', 'pp/*.css', ]}
else:
    # Python 2.7: package_data seems to be broken
    # added required data to MANIFEST.in
    PACKAGE_DATA = dict()


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
    version=VERSION,
    description='A Python package to create/manipulate DXF drawings.',
    author=AUTHOR_NAME,
    url='https://ezdxf.mozman.at',
    download_url='https://pypi.org/project/ezdxf/',
    author_email=AUTHOR_EMAIL,
    # for v0.9.0 set 'universal = 0' in setup.cfg
    python_requires='>=2.7',
    packages=['ezdxf',
              'ezdxf.legacy',
              'ezdxf.modern',
              'ezdxf.lldxf',
              'ezdxf.pp',
              'ezdxf.sections',
              'ezdxf.templates',
              'ezdxf.tools',
              'ezdxf.addons',
              'ezdxf.algebra',
              'ezdxf.audit',
              ],
    package_data=PACKAGE_DATA,
    entry_points={
        'console_scripts': [
            'dxfpp = ezdxf.pp.__main__:main',  # DXF Pretty Printer
            'dxfaudit = ezdxf.audit.__main__:main',  # DXF Audit
        ]
    },
    provides=['ezdxf'],
    tests_require=['pytest'],
    install_requires=['pyparsing>=2.0.1'],
    keywords=['DXF', 'CAD'],
    long_description=read('README.rst')+read('NEWS.rst', until='Version 0.7.6'),
    platforms="OS Independent",
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
